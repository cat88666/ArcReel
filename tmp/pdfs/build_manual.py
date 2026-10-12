from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/pdf'
TMP = ROOT / 'tmp/pdfs'
SOURCE = OUT / 'ArcReel_AI短剧运营操作手册.md'
PDF = OUT / 'ArcReel_AI短剧运营操作手册.pdf'
pdfmetrics.registerFont(TTFont('CN', '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
W, H = 595.276, 841.89
LEFT, RIGHT, TOP, BOTTOM = 48, 48, 105, 58
WIDTH = W - LEFT - RIGHT
INK = colors.HexColor('#193147')
MUTED = colors.HexColor('#53697A')
TEAL = colors.HexColor('#087E8B')
PALE = colors.HexColor('#EAF4F5')
LINE = colors.HexColor('#DCE5EA')

styles = {
    'body': ParagraphStyle('body', fontName='CN', fontSize=10.3, leading=17.3, textColor=INK, wordWrap='CJK', spaceAfter=7),
    'h2': ParagraphStyle('h2', fontName='CN', fontSize=13.2, leading=19, textColor=TEAL, spaceBefore=10, spaceAfter=8),
    'cell': ParagraphStyle('cell', fontName='CN', fontSize=9.6, leading=15.5, textColor=INK, wordWrap='CJK'),
    'head': ParagraphStyle('head', fontName='CN', fontSize=9.6, leading=15.5, textColor=colors.white, wordWrap='CJK'),
    'note': ParagraphStyle('note', fontName='CN', fontSize=10, leading=17, textColor=INK, wordWrap='CJK'),
}

def clean(s):
    return escape(s.replace('`', '').replace('–', '-').replace('—', '-'))

def para(s, style='body'):
    return Paragraph(clean(s), styles[style])

def elements(lines):
    result = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[:\- ]+', c) for c in row):
                    rows.append(row)
                i += 1
            data = [[para(c, 'head' if n == 0 else 'cell') for c in row] for n, row in enumerate(rows)]
            widths = [WIDTH * .82, WIDTH * .18] if pno == 2 else [WIDTH * .29, WIDTH * .71]
            table = Table(data, colWidths=widths, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), TEAL),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F1F6F8'), colors.white]),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 4 if pno == 2 else 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4 if pno == 2 else 7),
                ('LINEBELOW', (0, -1), (-1, -1), .5, LINE),
            ]))
            result.extend([table, Spacer(1, 10)])
            continue
        if line.startswith('## '):
            result.extend([Spacer(1, 5), para(line[3:], 'h2')])
        elif line.startswith('> '):
            note = Table([[para(line[2:], 'note')]], colWidths=[WIDTH])
            note.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), PALE),
                ('LINEBEFORE', (0, 0), (0, -1), 3, TEAL),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            result.extend([note, Spacer(1, 10)])
        else:
            if line.startswith('- [ ] '):
                line = '□  ' + line[6:]
            elif line.startswith('- '):
                line = '•  ' + line[2:]
            result.extend([para(line), Spacer(1, 6)])
        i += 1
    return result

sections = SOURCE.read_text().split('<!-- PAGE -->')
assert len(sections) == 22, len(sections)
OUT.mkdir(parents=True, exist_ok=True)
c = canvas.Canvas(str(PDF), pagesize=(W, H))
c.setTitle('ArcReel AI 短剧运营操作手册')
c.setAuthor('ArcReel')
c.setSubject('小说与成品剧本制作 AI 短剧：运营操作、审核、生成、剪辑与交付')

for pno, section in enumerate(sections, 1):
    lines = section.strip().splitlines()
    title = lines[0][2:]
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    if pno == 1:
        c.setFillColor(INK)
        c.rect(0, H - 310, W, 310, fill=1, stroke=0)
        c.setFillColor(TEAL)
        c.rect(LEFT, H - 83, 58, 5, fill=1, stroke=0)
        c.setFont('CN', 20)
        c.setFillColor(colors.HexColor('#8CD8DD'))
        c.drawString(LEFT, H - 121, 'ArcReel')
        c.setFont('CN', 29)
        c.setFillColor(colors.white)
        c.drawString(LEFT, H - 182, 'AI 短剧')
        c.drawString(LEFT, H - 226, '运营操作手册')
        c.setFont('CN', 12)
        c.setFillColor(colors.HexColor('#B8D4DF'))
        c.drawString(LEFT, H - 270, '小说 / 成品剧本 · 剧情演绎 · 审核与交付')
        body = [line for line in lines[2:] if line.strip() and not line.startswith('从小说')]
        y = H - 343
    else:
        c.setFont('CN', 9)
        c.setFillColor(MUTED)
        c.drawString(LEFT, H - 34, 'ARCREEL  /  AI 短剧运营操作手册')
        c.setFillColor(TEAL)
        c.rect(LEFT, H - 55, 28, 3, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont('CN', 21)
        c.drawString(LEFT, H - 85, title)
        body = lines[1:]
        y = H - TOP
        c.bookmarkPage(f'page-{pno}')
        c.addOutlineEntry(title, f'page-{pno}', level=0)
    for item in elements(body):
        w, h = item.wrap(WIDTH, H)
        if y - h < BOTTOM:
            raise RuntimeError(f'Page {pno} overflow at {y-h:.1f}: {getattr(item, "text", type(item).__name__)}')
        item.drawOn(c, LEFT, y-h)
        y -= h
    c.setStrokeColor(LINE)
    c.line(LEFT, 44, W - RIGHT, 44)
    c.setFont('CN', 8)
    c.setFillColor(MUTED)
    c.drawString(LEFT, 28, '运营操作版  ·  v1.0  ·  2026-10-12')
    c.drawRightString(W - RIGHT, 28, f'{pno:02d} / {len(sections):02d}')
    c.showPage()
c.save()

doc = fitz.open(PDF)
assert len(doc) == 22
for i, page in enumerate(doc):
    page.get_pixmap(matrix=fitz.Matrix(1.25, 1.25), alpha=False).save(TMP / f'page-{i+1:02d}.png')
    assert len(page.get_text()) > 200, (i, 'empty page')
print(f'Created {PDF}, {len(doc)} pages, {PDF.stat().st_size:,} bytes')
print('All pages rendered; page overflow checks passed.')
