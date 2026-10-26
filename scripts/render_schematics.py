"""Rasterize KiCad's native SVG exports without changing their geometry."""
from pathlib import Path
import math
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def main():
    schematics=list((ROOT/'outputs/schematic-svg').glob('*.svg'))
    assert len(schematics)==1,schematics
    jobs=[(schematics[0],ROOT/'outputs/schematics.png',4200),*[(ROOT/f'outputs/assembly-{s}.svg',ROOT/f'outputs/assembly-{s}.png',1800) for s in ('top','bottom')]]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for source,target,width in jobs:
            text=source.read_text(encoding='utf-8')
            root=ET.fromstring(text)
            view=[float(x) for x in root.attrib['viewBox'].split()]
            height=math.ceil(width*view[3]/view[2])
            page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
            page.goto(source.resolve().as_uri())
            page.locator('svg').evaluate('(e,s)=>{e.style.width=s[0]+"px";e.style.height=s[1]+"px";e.style.background="white";document.body&&(document.body.style.margin="0")}',[width,height])
            page.locator('svg').screenshot(path=str(target))
            assert target.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
            print(target.name,width,height,flush=True)
            page.close()
        browser.close()

if __name__=='__main__':main()
