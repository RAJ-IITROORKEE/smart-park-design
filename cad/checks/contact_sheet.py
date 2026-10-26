"""Contact sheet of the saved CAD snapshots for visual review."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]/'renders'
names = ['base','lid','sensor_mask','sensor_retainer','front_oled','front_blank','oled_retainer','light_pipe','fit_coupon']
sheet = Image.new('RGB', (1200,990), 'white')
draw = ImageDraw.Draw(sheet)
for i, name in enumerate(names):
    image = Image.open(ROOT/f'{name}.png').convert('RGB')
    image.thumbnail((400,300))
    sheet.paste(image, ((i%3)*400,(i//3)*330))
    draw.text(((i%3)*400+12,(i//3)*330+305), name, fill='black')
sheet.save(ROOT/'parts-review.png')
