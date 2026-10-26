"""Small release check for retained files, preview copies, links and runtime arithmetic."""
from pathlib import Path
import hashlib,json,re,struct,sys,zipfile
from urllib.parse import unquote,urlsplit
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    (ROOT/'verification/delivery-check.json').write_text('{"status":"checking"}',encoding='utf-8')
    audit=json.loads((ROOT/'verification/release-electrical.json').read_text())
    critical={'hardware/SmartMark.kicad_pcb':audit['board_sha256'],'hardware/SmartMark.kicad_sch':audit['schematic_sha256'],'outputs/board.step':audit['step_sha256']}
    for name,digest in critical.items():assert sha(ROOT/name)==digest,name
    for name,digest in audit['fabrication_files'].items():assert sha(ROOT/'outputs/fabrication'/name)==digest,name
    assert sha(ROOT/'outputs/SmartPark-RevD-PCB-Fabrication.zip')==audit['archive_sha256']
    checks=json.loads((ROOT/'cad/checks/assembly-check-final.json').read_text())
    for name,info in checks['models'].items():
        for ext in ('step','glb'):
            path=ROOT/'cad'/ext.upper()/f'{name}.{ext}';assert sha(path)==info[f'{ext}_sha256'],path
    for item in json.loads((ROOT/'cad/checks/manufacturing-manifest.json').read_text()).values():
        for path,digest in item['sha256'].items():assert sha(ROOT/'cad'/path)==digest,path
    copies=json.loads((ROOT/'previews/preview-copies.json').read_text())
    for src,dst in copies.items():assert sha(ROOT/src)==sha(ROOT/'previews'/dst),dst
    link_count=0
    for p in ROOT.rglob('*.md'):
        if not p.is_file():continue
        for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text(encoding='utf-8-sig')):
            link=link.strip('<>');parts=urlsplit(link)
            if parts.scheme or not parts.path:continue
            target=(p.parent/unquote(parts.path)).resolve()
            assert target.is_relative_to(ROOT.resolve()) and target.exists(),(str(p.relative_to(ROOT)),link)
            link_count+=1
    for p in (ROOT/'previews').rglob('*.glb'):
        b=p.read_bytes();assert b[:4]==b'glTF' and struct.unpack_from('<I',b,8)[0]==len(b),p
    for p in (ROOT/'previews/01-pcb').glob('*.svg'):assert ET.parse(p).getroot().tag.endswith('svg')
    for p in [ROOT/'Case-Print-Files.zip',ROOT/'outputs/SmartPark-RevD-PCB-Fabrication.zip',ROOT/'docs/SmartPark-RevD-Build-Guide.docx']:
        with zipfile.ZipFile(p) as z:assert z.testzip() is None,p
    model=json.loads((ROOT/'docs/battery-runtime-scenarios.json').read_text())
    for r in model['scenarios']:
        avg=model['sleep_mA']+r['awake_mA']*r['awake_s']/r['interval_s']+model['radio_mA']*model['radio_s']/model['report_interval_s']
        assert abs(avg-r['average_mA'])<.0005
        assert abs(model['capacity_mAh']*model['usable_fraction']/avg/24-r['days'])<.051
    result={'status':'pass','critical_design_hashes_unchanged':critical,'fabrication_files_unchanged':len(audit['fabrication_files']),'preview_copies_identical':len(copies),'local_markdown_links_checked':link_count,'runtime_scenarios_checked':len(model['scenarios']),'docx_and_zip_crc':'pass'}
    (ROOT/'verification/delivery-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
