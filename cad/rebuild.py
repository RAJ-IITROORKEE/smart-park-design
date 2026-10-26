"""Rebuild declared CAD outputs; any failed model or missing artifact stops the build."""
from pathlib import Path
import subprocess,sys,json,hashlib
ROOT=Path(__file__).resolve().parent
NAMES=["base","lid","sensor_mask","sensor_retainer","front_oled","front_blank","oled_retainer","light_pipe","fit_coupon","electronics_stack","product_oled","product_status","exploded_oled","exploded_status"]
def main():
    names=sys.argv[1:] or NAMES
    manifest_path=ROOT/"checks"/"manufacturing-manifest.json"
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for name in names:
        assert name in NAMES,name
        result=subprocess.run([sys.executable,"-X","utf8",str(ROOT/"src"/(name+".py")),"--force"],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace")
        (ROOT/"checks"/("build-"+name+".log")).write_text(result.stdout+result.stderr,encoding="utf-8")
        assert result.returncode==0,result.stdout+result.stderr
        if name in ("base","lid","front_oled"):
            # OCCT's native solid mesher preserves latch-window seams that the preview mesh leaves open.
            from build123d import import_step,export_stl,Mesher
            shape=import_step(ROOT/"STEP"/(name+".step"))
            export_stl(shape,ROOT/"STL"/(name+".stl"),tolerance=.02,angular_tolerance=.1)
            mesh=Mesher();mesh.add_shape(shape,linear_deflection=.02,angular_deflection=.1)
            mesh.write(ROOT/"3MF"/(name+".3mf"))
            paths=["src/design.py","src/"+name+".py","STEP/"+name+".step","STL/"+name+".stl","3MF/"+name+".3mf"]
            manifest[name]={"method":"OCCT native solid tessellation,0.02mm/0.1rad","sha256":{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}}
            manifest_path.write_text(json.dumps(manifest,indent=2))
        for ext in ("STEP","GLB"):
            p=ROOT/ext/(name+("."+ext.lower()))
            assert p.exists() and p.stat().st_size>100,p
        print("BUILT "+name,flush=True)
if __name__=="__main__":main()

