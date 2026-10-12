from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
from fontTools.ttLib import TTFont
import pymupdf
import re

root = Path(__file__).resolve().parents[2]
folder = root / 'tmp/pdfs'
source = (root / 'output/pdf/ArcReel_AI短剧运营操作手册.md').read_text()
doc = pymupdf.open(root / 'output/pdf/ArcReel_AI短剧运营操作手册.pdf')
font = TTFont('/System/Library/Fonts/Supplemental/Arial Unicode.ttf')
cmap = font.getBestCmap()
missing = sorted({c for c in source if ord(c) > 127 and ord(c) not in cmap})
assert not missing, missing
for n in range(0, len(doc), 4):
    sheet = Image.new('RGB', (1510, 2170), '#CED7DC')
    draw = ImageDraw.Draw(sheet)
    for j in range(4):
        p = n + j
        if p >= len(doc):
            break
        im = Image.open(folder / f'page-{p+1:02d}.png').convert('RGB')
        im.thumbnail((735, 1040))
        x, y = 12 + (j % 2)*752, 25 + (j // 2)*1080
        sheet.paste(im, (x, y))
        draw.text((x, y-16), f'PAGE {p+1:02d}', fill='#193147')
    sheet.save(folder / f'review-{n//4+1}.png')
for i, page in enumerate(doc):
    text = page.get_text()
    assert '\ufffd' not in text, (i+1, 'replacement character')
    for block in page.get_text('dict')['blocks']:
        if block['type'] != 0:
            continue
        for line in block['lines']:
            for span in line['spans']:
                x0, y0, x1, y1 = span['bbox']
                assert x0 >= 0 and y0 >= 0 and x1 <= page.rect.width+.2 and y1 <= page.rect.height+.2, (i+1, span['text'])
print('22 pages; font coverage, text extraction and page boundary checks passed.')
print('Contact sheets: tmp/pdfs/review-1.png through review-6.png')
print('Page text character counts:', [len(p.get_text()) for p in doc])
