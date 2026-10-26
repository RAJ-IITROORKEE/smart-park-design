"""Rasterize the two native copper SVGs for the Word guide."""
from pathlib import Path
import math,xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]/'previews/01-pcb'
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    for side in ('front','back'):
        source=ROOT/f'pcb-{side}.svg';view=list(map(float,ET.parse(source).getroot().attrib['viewBox'].split()))
        width=1600;height=math.ceil(width*view[3]/view[2])
        page=browser.new_page(viewport={'width':width,'height':height})
        page.goto(source.as_uri())
        page.locator('svg').evaluate('(e,s)=>{e.style.width=s[0]+"px";e.style.height=s[1]+"px";e.style.background="white";document.body&&(document.body.style.margin="0")}',[width,height])
        output=source.with_suffix('.png');page.locator('svg').screenshot(path=str(output))
        assert output.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n';page.close()
    browser.close()
