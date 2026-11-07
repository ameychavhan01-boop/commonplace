"""Contact sheet: python sheet.py OUT.png img1 img2 ... (2 columns, each 960x540, labelled)"""
import sys
from PIL import Image, ImageDraw
out, imgs = sys.argv[1], sys.argv[2:]
cols = 2; rows = (len(imgs) + 1) // 2
sheet = Image.new('RGB', (cols * 960 + 10, rows * 545), (40, 40, 40))
d = ImageDraw.Draw(sheet)
for k, p in enumerate(imgs):
    im = Image.open(p).convert('RGB').resize((960, 540), Image.LANCZOS)
    x, y = (k % cols) * 970, (k // cols) * 545
    sheet.paste(im, (x, y)); d.rectangle([x, y, x + 260, y + 22], fill=(0, 0, 0)); d.text((x + 4, y + 4), p.split('/')[-1], fill=(255, 255, 0))
sheet.save(out)
