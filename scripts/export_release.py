"""Export and audit the frozen Rev D board with KiCad's Python runtime."""
from pathlib import Path
import csv, hashlib, json, subprocess, zipfile
import pcbnew

ROOT=Path(__file__).resolve().parents[1]
CLI=Path('C:/Users/rajra/.codex/pcb-toolchain/kicad/bin/kicad-cli.exe')
BOARD=ROOT/'hardware/SmartMark.kicad_pcb'
SCH=ROOT/'hardware/SmartMark.kicad_sch'
OUT=ROOT/'outputs'
FAB=OUT/'fabrication'
VERIFY=ROOT/'verification'

def run(*args):
    result=subprocess.run([str(CLI),*map(str,args)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    assert result.returncode==0,(args,result.returncode,result.stdout,result.stderr)
    print('OK',' '.join(map(str,args[:3])),flush=True)
    return result.stdout

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    FAB.mkdir(parents=True,exist_ok=True)
    run('pcb','drc','--format','json','--severity-all','--schematic-parity','--exit-code-violations','-o',VERIFY/'drc-final.json',BOARD)
    run('sch','erc','--format','json','--severity-all','--exit-code-violations','-o',VERIFY/'erc-final.json',SCH)
    drc=json.loads((VERIFY/'drc-final.json').read_text())
    erc=json.loads((VERIFY/'erc-final.json').read_text())
    assert not drc['violations'] and not drc['unconnected_items'] and not drc['schematic_parity']
    assert all(not s['violations'] for s in erc['sheets'])
    board=pcbnew.LoadBoard(str(BOARD))
    fps={f.GetReference():f for f in board.GetFootprints()}
    expected={
        'U1.1':'HC_TRIG','U1.2':'ECHO_GPIO','U1.4':'BOOST_EN','U1.5':'I2C_SDA','U1.6':'I2C_SCL','U1.7':'LED_DATA_3V3','U1.12':'3V3','U1.13':'GND',
        'U2.1':'GND','U2.2':'5V_SENSOR','U2.3':'BOOST_FB','U2.4':'BOOST_EN','U2.5':'BOOST_SW','U2.6':'3V3','U2.7':'GND',
        'U3.1':'3V3','U3.2':'GND','U3.3':'LED_DATA_3V3','U3.4':'LED_DATA_5V','U3.5':'3V3','U3.6':'5V_SENSOR',
        'U4.2':'HC_ECHO','U4.3':'GND','U4.4':'ECHO_GPIO','U4.5':'3V3',
        'D1.2':'GND','D1.3':'LED_DIN','D1.4':'5V_SENSOR',
        'J1.1':'5V_SENSOR','J1.2':'HC_TRIG','J1.3':'HC_ECHO','J1.4':'GND',
        'J2.1':'GND','J2.2':'3V3','J2.3':'I2C_SCL','J2.4':'I2C_SDA',
        'C5.1':'5V_SENSOR','C6.1':'3V3','C7.1':'5V_SENSOR','C5.2':'GND','C6.2':'GND','C7.2':'GND',
    }
    actual={f'{ref}.{p.GetNumber()}':p.GetNetname().lstrip('/') for ref,f in fps.items() for p in f.Pads()}
    assert all(actual.get(pin)==net for pin,net in expected.items()),[(pin,actual.get(pin),net) for pin,net in expected.items() if actual.get(pin)!=net]
    for pin in ('U1.3','U1.8','U1.9','U1.10','U1.11','U1.14','U4.1','D1.1'):
        assert actual[pin].startswith('unconnected-'),(pin,actual[pin])
    assert fps['D1'].GetLayer()==pcbnew.B_Cu and fps['C7'].GetLayer()==pcbnew.B_Cu
    assert len(fps)==33 and len([f for f in fps if f.startswith('H')])==4
    widths=[pcbnew.ToMM(t.GetWidth()) for t in board.GetTracks() if not isinstance(t,pcbnew.PCB_VIA)]
    assert widths and min(widths)>=.18-1e-6
    run('pcb','export','gerbers','-l','F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,B.Paste,Edge.Cuts','-o',str(FAB)+'/',BOARD)
    run('pcb','export','drill','--format','excellon','--excellon-units','mm','--excellon-separate-th','--generate-map','--map-format','pdf','--generate-report','-o',str(FAB)+'/',BOARD)
    for stem,extra in [('placements-all',[]),('placements-smd',['--smd-only'])]:
        run('pcb','export','pos','--format','csv','--units','mm',*extra,'-o',OUT/f'{stem}.csv',BOARD)
    position_path=OUT/'placements-smd.csv'
    with position_path.open(newline='',encoding='utf-8') as stream:
        reader=csv.DictReader(stream);fields=reader.fieldnames
        positions=[row for row in reader if not row['Ref'].startswith(('TP','H'))]
    assert {'D1','C7'}<={row['Ref'] for row in positions}
    assert all(row['Side']=='bottom' for row in positions if row['Ref'] in ('D1','C7'))
    with position_path.open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(positions)
    svg=OUT/'schematic-svg';svg.mkdir(exist_ok=True)
    run('sch','export','svg','-o',str(svg)+'/',SCH)
    run('sch','export','pdf','-o',OUT/'schematics.pdf',SCH)
    run('sch','export','netlist','--format','kicadxml','-o',VERIFY/'SmartMark-schematic.xml',SCH)
    for side,layers in [('top','F.Fab,F.Silkscreen,Edge.Cuts'),('bottom','B.Fab,B.Silkscreen,Edge.Cuts')]:
        run('pcb','export','svg','--mode-single','--fit-page-to-board','--exclude-drawing-sheet','--layers',layers,'-o',OUT/f'assembly-{side}.svg',BOARD)
    rows=[]
    for line in (ROOT/'docs/BOM.md').read_text(encoding='utf-8').splitlines():
        cells=[x.strip() for x in line.strip('|').split('|')]
        if len(cells)==5 and cells[0] in fps and not cells[0].startswith('TP'):
            rows.append(cells)
    assert rows and {'C5','C6','C7'} <= {r[0] for r in rows}
    with (OUT/'BOM.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.writer(stream);writer.writerow(['Reference','Value','Footprint','MPN / status','Assembly notes']);writer.writerows(rows)
    optional={'J2','R8','R9'}
    with (OUT/'BOM-no-OLED.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.writer(stream);writer.writerow(['Reference','Value','Footprint','MPN / status','Assembly notes']);writer.writerows(row for row in rows if row[0] not in optional)
    with (OUT/'placements-smd-no-OLED.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(row for row in positions if row['Ref'] not in optional)
    gerbers=list(FAB.glob('*.g??'));drills=list(FAB.glob('*.drl'))
    assert len(gerbers)>=9 and len(drills)==2,(gerbers,drills)
    archive=OUT/'SmartPark-RevD-PCB-Fabrication.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(FAB.iterdir()):
            if p.is_file():z.write(p,p.name)
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    report={'status':'pass','qualification':'digitally checked indoor pilot; unbuilt','board_sha256':sha(BOARD),'schematic_sha256':sha(SCH),'step_sha256':sha(OUT/'board.step'),'erc_violations':0,'drc_violations':0,'unrouted':0,'schematic_parity':0,'critical_pin_checks':len(expected),'footprint_instances':len(fps),'tracks':len(widths),'vias':sum(isinstance(t,pcbnew.PCB_VIA) for t in board.GetTracks()),'minimum_track_mm':min(widths),'fabrication_files':{p.name:sha(p) for p in FAB.iterdir() if p.is_file()},'archive_sha256':sha(archive),'native_default_ignored_checks':drc['ignored_checks']}
    (VERIFY/'release-electrical.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
