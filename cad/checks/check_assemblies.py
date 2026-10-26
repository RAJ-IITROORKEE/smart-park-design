"""Validate the saved STEP/GLB assemblies and bind them to their source hashes."""
from pathlib import Path
import hashlib,json,struct
from cadgen import read_step

ROOT=Path(__file__).resolve().parents[1]
NAMES=('electronics_stack','product_oled','product_status','exploded_oled','exploded_status')

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    report={'status':'pass','units':'mm in STEP; glTF Y-up','models':{},'inputs':{}}
    for relative in ('src/design.py','../outputs/board.step','../docs/mechanical-interface.json','imported/xiao-s3-wio-sx1262-stack.step'):
        report['inputs'][relative]=digest(ROOT/relative)
    for name in NAMES:
        step=ROOT/'STEP'/f'{name}.step';glb=ROOT/'GLB'/f'{name}.glb'
        shape=read_step(step);solids=list(shape.solids());assert len(solids)>60,(name,len(solids))
        assert all(s.is_valid and s.volume>0 for s in solids),name
        bb=shape.bounding_box()
        if name.startswith('product_'):
            assert abs(bb.size.X-94)<.05 and abs(bb.size.Z-50.4)<.05,(name,bb)
        blob=glb.read_bytes();assert blob[:4]==b'glTF' and struct.unpack_from('<I',blob,8)[0]==len(blob),name
        length,kind=struct.unpack_from('<II',blob,12);assert kind==0x4E4F534A
        scene=json.loads(blob[20:20+length]);assert scene['asset']['version']=='2.0' and scene['meshes'],name
        # Exporters may merge solids by material; validate geometry, not a mesh-count convention.
        primitives=[p for mesh in scene['meshes'] for p in mesh['primitives']]
        assert primitives and all('POSITION' in p['attributes'] for p in primitives),name
        assert sum(scene['accessors'][p['attributes']['POSITION']]['count'] for p in primitives)>100,name
        report['models'][name]={'solids':len(solids),'bbox_mm':str(bb),'step_sha256':digest(step),'glb_sha256':digest(glb)}
        print('PASS',name,len(solids),flush=True)
    (ROOT/'checks/assembly-check-final.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

if __name__=='__main__':main()
