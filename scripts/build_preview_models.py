"""Export enclosure-only previews from the frozen installed assemblies."""
from pathlib import Path
import hashlib,json
from cadgen import build123d as bd,read_step,step,glb
ROOT=Path(__file__).resolve().parents[1]

def enclosure(variant):
    source=read_step(ROOT/f'cad/STEP/product_{variant}.step')
    parts=[part for part in source.children if part.label!='Electronics stack - reference components marked']
    assert len(parts)==(7 if variant=='oled' else 6)
    assert all(len(p.solids())==1 and p.volume>0 and p.is_valid for p in parts)
    return bd.Compound(children=parts,label=f'SmartPark {variant} enclosure only')

@step(out='../previews/03-enclosure/case-oled.step')
@glb(out='../previews/03-enclosure/case-oled.glb')
def case_oled():
    return enclosure('oled')

@step(out='../previews/03-enclosure/case-no-oled.step')
@glb(out='../previews/03-enclosure/case-no-oled.glb')
def case_no_oled():
    return enclosure('status')

@glb(out='../previews/01-pcb/pcb-carrier.glb')
def carrier():
    return read_step(ROOT/'outputs/board.step')

def main():
    # @lat: [[index#SmartPark Revision D#Delivery and preview organization]]
    case_oled();case_no_oled();carrier()
    result={}
    for variant,count in [('oled',7),('no-oled',6)]:
        path=ROOT/f'previews/03-enclosure/case-{variant}.step'
        shape=read_step(path);solids=shape.solids()
        assert len(solids)==count and all(s.is_valid and s.volume>0 for s in solids)
        result[variant]={'solids':len(solids),'valid':True,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    (ROOT/'verification/preview-models.json').write_text(json.dumps(result,indent=2))
    print(result,flush=True)

if __name__=='__main__':main()
