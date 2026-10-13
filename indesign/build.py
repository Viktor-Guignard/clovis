#!/usr/bin/env python3
"""Reconstruit etude-graphique.html en document InDesign (IDML).

Textes en blocs de texte réels, avec styles de paragraphe et de caractère ;
couleurs en nuances CMJN ; visuels exportés à ~300 ppi et liés (dossier Links) ;
polices fournies (Document fonts). Le squelette (préférences, styles par défaut,
gabarit) vient d'un IDML exporté par InDesign (squelette/, licence BSD de
SimpleIDML) : le fichier produit a la structure d'un vrai export.

    python3 indesign/build.py        ->  etude-graphique-indesign.zip

Il faut Node et Playwright (Chromium) pour la mesure de la page, et Pillow.
"""
import json, os, re, shutil, subprocess, sys, tempfile, zipfile
from xml.sax.saxutils import escape, quoteattr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HTML = os.path.join(ROOT, 'etude-graphique.html')
BASE = os.path.join(HERE, 'squelette')
ZIP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'etude-graphique-indesign.zip')
OUT = tempfile.mkdtemp(prefix='cc-idml-')
NAME = 'CONTRE-CHAMP_etude-graphique'

PW, PH = 595.2755905511812, 841.8897637795276      # A4 en points
BLEED = 8.503937007874017                          # 3 mm
SPREAD_GAP = 180.0

# ------------------------------------------------------------------ spécification
def T(page, sel, style=None, pmap=None, **kw):
    return dict(type='text', page=page, sel=sel, style=style, pmap=pmap or {}, **kw)
def R(page, sel, **kw):  return dict(type='rect', page=page, sel=sel, **kw)
def B(page, sel, side, **kw): return dict(type='border', page=page, sel=sel, side=side, **kw)
def I(page, sel, **kw):  return dict(type='img', page=page, sel=sel, **kw)

def folio(p, sur=False):
    out = []
    if sur: out.append(R(p, '.folio', fill='paper'))
    out += [T(p, '.folio .n', 'Folio numero'), R(p, '.folio .f'), T(p, '.folio > span:last-child', 'Folio')]
    return out

ITEMS = []
# --- page 1 : ouverture
ITEMS += [
    I(0, '.hero', hide=['h1', '.tc'], bleed={'l': 1, 't': 1}, name='p1-ouverture'),
    T(0, '.hero h1', 'Titre ouverture'),
    T(0, '.hero .tc', 'Mention visuel'),
    R(0, '.soustitre .rg'),
    T(0, '.soustitre h2', 'Sous-titre ouverture'),
]
for i in range(1, 5):
    d = f'.corps1 > .duo:nth-child({i})'
    ITEMS += [I(0, f'{d} figure > :first-child', name=f'p1-vignette-{i}'), T(0, f'{d} figcaption', 'Legende'),
              T(0, f'{d} section', pmap={'h3': 'Intertitre', 'p': 'Texte colonne'})]
ITEMS += folio(0)
# --- page 2 : couvertures
ITEMS += [
    T(1, '.oeil', 'Oeil', dot=True),
    T(1, '.haut2 h2', pmap={'h2': 'Titre M', 'small': 'Sous-titre gris'}),
    T(1, '.crit', exclude=['.reperes'], pmap={'p.intro': 'Chapo', 'h3': 'Intertitre', 'p': 'Texte courant'}),
    B(1, '.reperes', 'top'),
    T(1, '.reperes > div', all=True, pmap={'b': 'Chiffre', 'span': 'Chiffre legende'}),
    T(1, '.reperes .src', 'Note source'),
    I(1, '.pile .cv', all=True, pad=16, alpha=True, name='p2-famille'),
    T(1, '.pile figcaption', all=True, pmap={'b': 'Legende titre', '*': 'Legende'}),
    I(1, '.planche', hide=['.etiq'], bleed={'r': 1, 'b': 1}, name='p2-table-du-libraire'),
    R(1, '.planche .etiq', fill='paper'),
    T(1, '.planche .etiq .cap', 'Legende'),
]
ITEMS += folio(1, sur=True)
# --- page 3 : le crible
ITEMS += [
    T(2, '.oeil', 'Oeil', dot=True),
    T(2, '.tete3 h2', 'Titre XL'),
    R(2, '.tete3 .rg'),
    T(2, '.tete3 .lead', 'Chapo grand'),
    T(2, '.crible .th > span', 'Tableau entete', all=True),
    B(2, '.crible .th', 'bottom'),
]
for i in range(1, 11):
    r = f'.crible .rows > .row:nth-child({i})'
    ITEMS += [T(2, f'{r} .code', 'Tableau code'), R(2, f'{r} .v'), T(2, f'{r} .v', 'Pastille', badge=True),
              T(2, f'{r} p', 'Tableau texte'), B(2, r, 'bottom')]
ITEMS += [
    B(2, '.bilan', 'top'),
    T(2, '.bilan .cpt > div', all=True, pmap={'b': 'Bilan chiffre', '*': 'Bilan libelle'}),
    T(2, '.bilan > p', 'Bilan phrase'),
]
ITEMS += folio(2)
# --- page 4 : la charte
ITEMS += [
    T(3, '.oeil', 'Oeil', dot=True),
    T(3, '.flux4 > header h2', 'Titre L'),
    T(3, '.bloc > h3', 'Titre de bloc', all=True),
    B(3, '.bloc > h3', 'bottom', all=True),
    R(3, '.sw .p', all=True, swatch=True),
    T(3, '.sw .p span', 'Nuance code', all=True),
    T(3, '.sw .nm', 'Nuance nom', all=True),
    T(3, '.sw .rl', 'Nuance role', all=True),
    T(3, '.typos .ech1', 'Specimen titrage'),
    T(3, '.typos .ech2', 'Specimen texte'),
    T(3, '.typos .ech3', 'Specimen repere'),
    T(3, '.typos .cap', 'Legende', all=True),
    B(3, '.typos .note', 'left'),
    T(3, '.typos .note', 'Note'),
    I(3, '.dispo .ms', all=True, name='p4-dispositif'),
    T(3, '.dispo figcaption', all=True, pmap={'b': 'Legende titre', '*': 'Legende'}),
    I(3, '.plat', pad=22, alpha=True, name='p4-piste-couverture'),
    T(3, '.couv .txt p:not(.cap)', 'Texte petit'),
    T(3, '.couv .txt .cap', 'Legende'),
]
ITEMS += folio(3)
for n, it in enumerate(ITEMS):
    it['id'] = f'p{it["page"]+1}-{n:03d}'

# ------------------------------------------------------------------ mesures
os.makedirs(os.path.join(OUT, 'Links'), exist_ok=True)
spec = os.path.join(OUT, 'spec.json')
json.dump({'items': ITEMS, 'dsf': 2.5}, open(spec, 'w'))
subprocess.run(['node', os.path.join(HERE, 'capture.js'), spec, HTML, OUT], check=True)
M = json.load(open(os.path.join(OUT, 'mesures.json')))
os.remove(spec); os.remove(os.path.join(OUT, 'mesures.json'))
K = PW / M['pageW']                                 # px CSS -> pt
PPI = M['pageW'] * M['dsf'] / (PW / 72.0)           # résolution réelle des PNG

# Résolution inscrite dans les PNG, pour qu'InDesign les mette à la bonne taille
try:
    from PIL import Image as PILImage
    for it in M['items']:
        if it.get('file'):
            p = os.path.join(OUT, 'Links', it['file'])
            im = PILImage.open(p); im.load(); im.save(p, dpi=(PPI, PPI), optimize=True)
except ImportError:
    print('Pillow absent : résolution des PNG non inscrite (72 ppi apparent)')

# ------------------------------------------------------------------ couleurs
def rgb(s):
    m = re.match(r'rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)', s or '')
    if not m: return None
    if m.group(4) is not None and float(m.group(4)) == 0: return None
    return '#%02X%02X%02X' % tuple(round(float(m.group(i))) for i in (1, 2, 3))

# Nuances nommées : valeurs CMJN ajustées à l'œil sur les teintes de la charte
def sep(h, k):
    """CMJN à noir imposé : C, M, J calculés pour retrouver la teinte RVB."""
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return ' '.join(str(max(0, round(100 * (1 - x / (1 - k))))) for x in (r, g, b)) + ' ' + str(round(k * 100))
NAMED = {
    '#121212': ('CC Encre', '0 0 0 100'),
    '#F2EEE4': ('CC Papier', sep('#F2EEE4', 0)),
    '#B9893F': ('CC Or', sep('#B9893F', .15)),
    '#8A662F': ('CC Or texte', sep('#8A662F', .40)),
    '#8B8578': ('CC Gris', sep('#8B8578', .25)),
    '#716C61': ('CC Gris texte', sep('#716C61', .45)),
    '#DAD4C6': ('CC Filet', sep('#DAD4C6', .10)),
    '#DED8CA': ('CC Pastille', sep('#DED8CA', .08)),
}
COLORS = {}  # hex -> (Self, Name, CMYK)
def naive_cmyk(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    k = 1 - max(r, g, b)
    if k >= 1: return '0 0 0 100'
    c, m, y = ((1 - x - k) / (1 - k) for x in (r, g, b))
    return ' '.join(str(round(v * 100)) for v in (c, m, y, k))
def swatch(h):
    if h is None: return 'Swatch/None'
    if h not in COLORS:
        name, cmyk = NAMED.get(h, ('CC Teinte ' + h[1:], None))
        COLORS[h] = ('Color/' + name, name, cmyk or naive_cmyk(h))
    return COLORS[h][0]
for h in NAMED: swatch(h)

# ------------------------------------------------------------------ styles
FONT_STYLE = {
    ('Oswald', '300', 'normal'): 'Light', ('Oswald', '400', 'normal'): 'Regular',
    ('Oswald', '500', 'normal'): 'Medium', ('Oswald', '600', 'normal'): 'SemiBold',
    ('Oswald', '700', 'normal'): 'Bold',
    ('Spectral', '300', 'normal'): 'Light', ('Spectral', '300', 'italic'): 'Light Italic',
    ('Spectral', '400', 'normal'): 'Regular', ('Spectral', '400', 'italic'): 'Italic',
    ('Spectral', '600', 'normal'): 'SemiBold', ('Spectral', '600', 'italic'): 'SemiBold Italic',
}
def fam(css):
    f = css['family'].split(',')[0].strip().strip('"\'')
    return 'Oswald' if 'Oswald' in f else 'Spectral'
def fontstyle(css):
    w = str(int(round(float(css['weight']) / 100) * 100))
    return FONT_STYLE.get((fam(css), w, 'italic' if css['style'] == 'italic' else 'normal'), 'Regular')
def num(x, nd=2):
    return ('%.*f' % (nd, x)).rstrip('0').rstrip('.')
def props(css):
    """Propriétés typographiques InDesign déduites du CSS calculé."""
    size = css['size'] * K
    ls = 0.0 if css['ls'] in ('normal', '') else float(css['ls'].replace('px', '')) / css['size'] * 1000
    lead = None if css['lh'] in ('normal', '') else float(css['lh'].replace('px', '')) * K
    align = {'left': 'LeftAlign', 'start': 'LeftAlign', 'right': 'RightAlign', 'end': 'RightAlign',
             'center': 'CenterAlign', 'justify': 'LeftJustified'}.get(css['align'], 'LeftAlign')
    return {'font': fam(css), 'FontStyle': fontstyle(css), 'PointSize': num(size),
            'Tracking': str(round(ls)), 'Leading': num(lead) if lead else 'Auto',
            'Capitalization': 'AllCaps' if css['tt'] == 'uppercase' else 'Normal',
            'Justification': align, 'FillColor': swatch(rgb(css['color']))}

PSTYLES = {}   # name -> props
CSTYLES = {}   # name -> attrs
def pstyle(name, p):
    if name not in PSTYLES:
        PSTYLES[name] = dict(p)
    return PSTYLES[name]

def cstyle_for(base, run):
    """Style de caractère pour un segment qui diffère de son paragraphe."""
    rp = props(run['css'])
    diff = {k: rp[k] for k in ('FontStyle', 'FillColor', 'Tracking', 'Capitalization', 'font')
            if rp[k] != base[k]}
    sup = run['css']['va'] == 'super' or run['tag'] == 'sup'
    if not diff and not sup: return None, {}
    if sup: diff = {'Position': 'Superscript'}
    if run['css']['size'] * K < float(base['PointSize']) - 0.3 and not sup:
        diff['PointSize'] = num(run['css']['size'] * K)
    # noms lisibles
    if 'Position' in diff: name = 'Exposant'
    elif diff.get('FillColor', '').endswith('Or texte') and 'Italic' in diff.get('FontStyle', ''): name = 'Accent or'
    elif 'Italic' in diff.get('FontStyle', '') and len(diff) == 1: name = 'Italique' if diff['FontStyle'] == 'Italic' else 'Italique light'
    elif diff.get('FillColor', '').endswith('Or texte') and diff.get('FontStyle') == 'Bold': name = 'Lettre de bloc'
    elif diff.get('Capitalization') == 'AllCaps' or diff.get('FontStyle') in ('SemiBold', 'Bold'): name = 'Legende titre'
    elif diff.get('FillColor', '').endswith('Or texte'): name = 'Or'
    else: name = 'Variante ' + '-'.join(sorted(diff.values())).replace('Color/', '').replace(' ', '')
    name = 'CC ' + name
    key = name
    n = 2
    while key in CSTYLES and CSTYLES[key] != diff:
        key = f'{name} {n}'; n += 1
    CSTYLES[key] = diff
    return key, diff

# ------------------------------------------------------------------ fabrique XML
_uid = [0x2000]
def uid():
    _uid[0] += 1
    return 'u%x' % _uid[0]

def path_geo(w, h):
    pts = [(0, 0), (0, h), (w, h), (w, 0)]
    pp = ''.join(f'<PathPointType Anchor="{num(x,4)} {num(y,4)}" LeftDirection="{num(x,4)} {num(y,4)}" RightDirection="{num(x,4)} {num(y,4)}"/>' for x, y in pts)
    return f'<Properties><PathGeometry><GeometryPathType PathOpen="false"><PathPointArray>{pp}</PathPointArray></GeometryPathType></PathGeometry></Properties>'

WRAP = '<TextWrapPreference Inverse="false" ApplyToMasterPageOnly="false" TextWrapSide="BothSides" TextWrapMode="None"><Properties><TextWrapOffset Top="0" Left="0" Bottom="0" Right="0"/></Properties></TextWrapPreference>'
COMMON = 'ItemLayer="ub3" Locked="false" LocalDisplaySetting="Default" Visible="true"'

def spread_xy(page, x, y):
    side = page % 2
    return x * K + (-PW if side == 0 else 0), y * K - PH / 2

def rect_xml(page, box, fill=None, stroke=None, sw=0, name='$ID/', content='Unassigned', inner=''):
    x, y = spread_xy(page, box[0], box[1])
    w, h = box[2] * K, box[3] * K
    st = f'StrokeColor="{stroke}" StrokeWeight="{num(sw,3)}" StrokeAlignment="InsideAlignment"' if stroke else 'StrokeColor="Swatch/None" StrokeWeight="0"'
    return (f'<Rectangle Self="{uid()}" ContentType="{content}" {COMMON} Name={quoteattr(name)} '
            f'FillColor="{fill or "Swatch/None"}" {st} AppliedObjectStyle="ObjectStyle/$ID/[None]" '
            f'ItemTransform="1 0 0 1 {num(x,4)} {num(y,4)}">{path_geo(w, h)}{WRAP}{inner}</Rectangle>')

def oval_xml(page, cx, cy, d, fill):
    x, y = spread_xy(page, cx - d / 2, cy - d / 2)
    r = d * K / 2; k = r * 0.5523
    pts = [((r, 2 * r), (r + k, 2 * r), (r - k, 2 * r)), ((2 * r, r), (2 * r, r - k), (2 * r, r + k)),
           ((r, 0), (r - k, 0), (r + k, 0)), ((0, r), (0, r + k), (0, r - k))]
    pp = ''.join(f'<PathPointType Anchor="{num(a[0],4)} {num(a[1],4)}" LeftDirection="{num(l[0],4)} {num(l[1],4)}" RightDirection="{num(rr[0],4)} {num(rr[1],4)}"/>' for a, l, rr in pts)
    return (f'<Oval Self="{uid()}" ContentType="Unassigned" {COMMON} Name="$ID/" FillColor="{fill}" StrokeColor="Swatch/None" StrokeWeight="0" '
            f'AppliedObjectStyle="ObjectStyle/$ID/[None]" ItemTransform="1 0 0 1 {num(x,4)} {num(y,4)}">'
            f'<Properties><PathGeometry><GeometryPathType PathOpen="false"><PathPointArray>{pp}</PathPointArray></GeometryPathType></PathGeometry></Properties>{WRAP}</Oval>')

def image_xml(page, it):
    box = it['box']
    w_pt, h_pt = box[2] * K, box[3] * K
    gw, gh = it['px'][0] * 72.0 / PPI, it['px'][1] * 72.0 / PPI
    sx, sy = w_pt / gw, h_pt / gh
    img = (f'<Image Self="{uid()}" Space="$ID/#Links_RGB" ActualPpi="{num(PPI,1)} {num(PPI,1)}" EffectivePpi="{num(PPI/sx,1)} {num(PPI/sy,1)}" '
           f'ImageRenderingIntent="UseColorSettings" LocalDisplaySetting="Default" ImageTypeName="$ID/Portable Network Graphics (PNG)" '
           f'AppliedObjectStyle="ObjectStyle/$ID/[None]" ItemTransform="{num(sx,6)} 0 0 {num(sy,6)} 0 0" Visible="true" Name="$ID/">'
           f'<Properties><Profile type="string">$ID/None</Profile><GraphicBounds Left="0" Top="0" Right="{num(gw,4)}" Bottom="{num(gh,4)}"/></Properties>'
           f'{WRAP}'
           f'<Link Self="{uid()}" AssetURL="$ID/" AssetID="$ID/" LinkResourceURI="file:Links/{it["file"]}" LinkResourceFormat="$ID/Portable Network Graphics (PNG)" '
           f'StoredState="Normal" LinkClassID="35906" LinkClientID="257" LinkResourceModified="false" LinkObjectModified="false" ShowInUI="true" '
           f'CanEmbed="true" CanUnembed="true" CanPackage="true" ImportPolicy="NoAutoImport" ExportPolicy="NoAutoExport"/>'
           f'<ClippingPathSettings ClippingType="None" InvertPath="false" IncludeInsideEdges="false" RestrictToFrame="false" UseHighResolutionImage="true" Threshold="25" Tolerance="2" InsetFrame="0" AppliedPathName="$ID/" Index="-1"/>'
           f'<ImageIOPreference ApplyPhotoshopClippingPath="true" AllowAutoEmbedding="true" AlphaChannelName="$ID/"/>'
           f'</Image>')
    fit = '<FrameFittingOption LeftCrop="0" TopCrop="0" RightCrop="0" BottomCrop="0"/>'
    return rect_xml(page, box, content='GraphicType', name=it['file'][:-4], inner=fit + img)

STORIES = []   # (Self, xml)
def story_xml(sid, paras):
    out = []
    for i, (pname, over, runs) in enumerate(paras):
        attrs = ''.join(f' {k}={quoteattr(v)}' for k, v in over.items() if k != 'Leading')
        body = []
        if 'Leading' in over:   # l'interlignage est une propriété, pas un attribut
            body.append(f'<Properties><Leading type="unit">{over["Leading"]}</Leading></Properties>')
        for j, (cname, ctext) in enumerate(runs):
            cs = f'CharacterStyle/{cname}' if cname else 'CharacterStyle/$ID/[No character style]'
            br = '<Br/>' if (i < len(paras) - 1 and j == len(runs) - 1) else ''
            body.append(f'<CharacterStyleRange AppliedCharacterStyle={quoteattr(cs)}><Content>{escape(ctext)}</Content>{br}</CharacterStyleRange>')
        out.append(f'<ParagraphStyleRange AppliedParagraphStyle={quoteattr("ParagraphStyle/" + pname)}{attrs}>{"".join(body)}</ParagraphStyleRange>')
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            f'<idPkg:Story xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">'
            f'<Story Self="{sid}" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">'
            f'<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>'
            f'<InCopyExportOption IncludeGraphicProxies="true" IncludeAllResources="false"/>'
            f'{"".join(out)}</Story></idPkg:Story>')

def pick_pstyle(it, para):
    pm = it.get('pmap') or {}
    tag, cls = para['tag'], para['cls'].split()
    for key, name in pm.items():
        if key == '*': continue
        t, _, c = key.partition('.')
        if t == tag and (not c or c in cls): return 'CC ' + name
    return 'CC ' + (pm.get('*') or it.get('style') or 'Texte courant')

def text_xml(page, it, extra_lines=1.0, center=False):
    paras, boxes = [], []
    prev_bottom = None
    for para in it['paras']:
        name = pick_pstyle(it, para)
        p = props(para['css'])
        base = pstyle(name, p)
        over = {}
        for k in ('FillColor', 'PointSize', 'FontStyle', 'Justification', 'Tracking', 'Capitalization'):
            if p[k] != base[k]: over[k] = p[k]
        if p['Leading'] != base['Leading']: over['Leading'] = p['Leading']
        top = para['box'][1]
        if prev_bottom is not None and top - prev_bottom > 0.8:
            over['SpaceBefore'] = num((top - prev_bottom) * K, 1)
        elif prev_bottom is not None and top < prev_bottom and para['css'].get('mt', 0) > 0.5:
            over['SpaceBefore'] = num(para['css']['mt'] * K, 1)   # bloc imbriqué (h2 > small)
        prev_bottom = para['box'][1] + para['box'][3]
        runs = []
        for r in para['runs']:
            cname, _ = cstyle_for(p, r)   # comparé au paragraphe tel qu'il est, dérogations comprises
            if runs and runs[-1][0] == cname: runs[-1] = (cname, runs[-1][1] + r['t'])
            else: runs.append((cname, r['t']))
        paras.append((name, over, runs))
        boxes.append(para['box'])
    # cadre : l'union des paragraphes (ou la boîte de l'élément)
    if boxes:
        x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
        x1 = max(b[0] + b[2] for b in boxes); y1 = max(b[1] + b[3] for b in boxes)
        box = [x0, y0, x1 - x0, y1 - y0]
    else:
        box = list(it['box'])
    if it.get('dot'):                     # pastille de l'œil : 0,9 cqw + 1,2 cqw d'écart
        cq = M['pageW'] / 100
        box[0] += 2.1 * cq; box[2] -= 2.1 * cq
    if not center:
        last = PSTYLES[paras[-1][0]]
        lead = float(paras[-1][1].get('Leading', last['Leading'])) if last['Leading'] != 'Auto' else float(last['PointSize']) * 1.2
        box[3] += lead / K * extra_lines
        # une marge de largeur, du côté libre, contre les écarts de chasse
        just = paras[0][1].get('Justification', PSTYLES[paras[0][0]]['Justification'])
        grow = max(box[2] * 0.03, 3)
        if just == 'RightAlign': box[0] -= grow; box[2] += grow
        elif just == 'CenterAlign': box[0] -= grow / 2; box[2] += grow
        elif just != 'LeftJustified': box[2] += grow
    sid = uid()
    STORIES.append((sid, story_xml(sid, paras)))
    x, y = spread_xy(page, box[0], box[1])
    w, h = box[2] * K, box[3] * K
    vj = 'CenterAlign' if center else 'TopAlign'
    return (f'<TextFrame Self="{uid()}" ParentStory="{sid}" PreviousTextFrame="n" NextTextFrame="n" ContentType="TextType" {COMMON} '
            f'Name="$ID/" FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0" AppliedObjectStyle="ObjectStyle/$ID/[None]" '
            f'ItemTransform="1 0 0 1 {num(x,4)} {num(y,4)}">{path_geo(w, h)}'
            f'<TextFramePreference TextColumnCount="1" TextColumnGutter="12" TextColumnFixedWidth="{num(w,4)}" UseFixedColumnWidth="false" '
            f'FirstBaselineOffset="AscentOffset" MinimumFirstBaselineOffset="0" VerticalJustification="{vj}" VerticalThreshold="0" IgnoreWrap="false">'
            f'<Properties><InsetSpacing type="list"><ListItem type="unit">0</ListItem><ListItem type="unit">0</ListItem><ListItem type="unit">0</ListItem><ListItem type="unit">0</ListItem></InsetSpacing></Properties>'
            f'</TextFramePreference>{WRAP}</TextFrame>')

# ------------------------------------------------------------------ pages
PAGE_ITEMS = {0: [], 1: [], 2: [], 3: []}
for p in range(4):
    # fond de page, débordant dans le fond perdu côté extérieur
    side = p % 2
    bx = [-BLEED / K if side == 0 else 0, -BLEED / K, (PW + BLEED) / K, (PH + 2 * BLEED) / K]
    PAGE_ITEMS[p].append(rect_xml(p, bx, fill=swatch('#F2EEE4'), name='Fond papier'))

for it in M['items']:
    p = it['page']; css = it['css']
    if it['type'] == 'img':
        PAGE_ITEMS[p].append(image_xml(p, it))
    elif it['type'] == 'rect':
        if it.get('swatch'):
            # nuancier : l'or est un dégradé à l'écran, une nuance unie ici
            fill = rgb(css['bg']) or '#B9893F'
            stroke = swatch('#DAD4C6') if fill == '#F2EEE4' else None
            PAGE_ITEMS[p].append(rect_xml(p, it['box'], fill=swatch(fill), stroke=stroke, sw=0.75, name='Nuance'))
        else:
            fill = swatch(rgb(css['bg'])) if rgb(css['bg']) else (swatch('#F2EEE4') if it.get('fill') == 'paper' else 'Swatch/None')
            bw, bc = css['bt'][0], rgb(css['bt'][1])
            stroke = swatch(bc) if bw > 0 and css['bt'][2] != 'none' and bc else None
            PAGE_ITEMS[p].append(rect_xml(p, it['box'], fill=fill, stroke=stroke, sw=bw * K))
    elif it['type'] == 'border':
        side = {'top': 'bt', 'bottom': 'bb', 'left': 'bl', 'right': 'br'}[it['side']]
        w, col, style = css[side]
        if w <= 0 or style == 'none' or not rgb(col): continue
        x, y, bw, bh = it['box']
        b = {'top': [x, y, bw, w], 'bottom': [x, y + bh - w, bw, w], 'left': [x, y, w, bh], 'right': [x + bw - w, y, w, bh]}[it['side']]
        PAGE_ITEMS[p].append(rect_xml(p, b, fill=swatch(rgb(col)), name='Filet'))
    elif it['type'] == 'text':
        if it.get('badge'):
            it['paras'] = it['paras'][:1]
            it['paras'][0]['css']['align'] = 'center'
            PAGE_ITEMS[p].append(text_xml(p, dict(it, paras=[dict(it['paras'][0], box=it['box'])]), center=True))
        else:
            PAGE_ITEMS[p].append(text_xml(p, it))
        if it.get('dot'):
            cq = M['pageW'] / 100
            b = it['box']
            PAGE_ITEMS[p].insert(len(PAGE_ITEMS[p]) - 1, oval_xml(p, b[0] + 0.45 * cq, b[1] + b[3] / 2, 0.9 * cq, swatch('#B9893F')))

# ------------------------------------------------------------------ assemblage
os.makedirs(os.path.join(OUT, 'pkg'), exist_ok=True)
PKG = os.path.join(OUT, 'pkg')
for sub in ('META-INF', 'Resources', 'MasterSpreads', 'Spreads', 'Stories', 'XML'):
    os.makedirs(os.path.join(PKG, sub), exist_ok=True)
def rd(p): return open(os.path.join(BASE, p), encoding='utf-8').read()
def wr(p, s): open(os.path.join(PKG, p), 'w', encoding='utf-8').write(s)

wr('mimetype', 'application/vnd.adobe.indesign-idml-package')
wr('META-INF/container.xml', rd('META-INF/container.xml'))
shutil.copy(os.path.join(BASE, 'Resources/Fonts.xml'), os.path.join(PKG, 'Resources/Fonts.xml'))
wr('XML/Tags.xml', rd('XML/Tags.xml'))
wr('XML/BackingStory.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
   '<idPkg:BackingStory xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">'
   '<XmlStory Self="u9c" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">'
   '<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle">'
   '<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]">'
   '<XMLElement Self="di2" MarkupTag="XMLTag/Root"/><Content>﻿</Content>'
   '</CharacterStyleRange></ParagraphStyleRange></XmlStory></idPkg:BackingStory>')

# Marges : 8 cqw en tête, 10 en pied, 9 au petit fond, 7 au grand fond (en pt)
cq = PW / 100
MT, MB, MI, MO = 8 * cq, 10 * cq, 9 * cq, 7 * cq
def margin_xml():
    return (f'<MarginPreference ColumnCount="1" ColumnGutter="12" Top="{num(MT,4)}" Bottom="{num(MB,4)}" Left="{num(MI,4)}" Right="{num(MO,4)}" '
            f'ColumnDirection="Horizontal" ColumnsPositions="0 {num(PW-MI-MO,4)}"/>')

# Préférences : A4, pages en vis-à-vis, fond perdu 3 mm, pas de remaniement des planches
pref = rd('Resources/Preferences.xml')
pref = re.sub(r'<DocumentPreference [^>]*>', lambda m: (m.group(0)
    .replace('PageHeight="759.6850393700788"', f'PageHeight="{PH}"').replace('PageWidth="566.9291338582677"', f'PageWidth="{PW}"')
    .replace('PagesPerDocument="1"', 'PagesPerDocument="4"')
    .replace('DocumentBleedTopOffset="0"', f'DocumentBleedTopOffset="{BLEED}"').replace('DocumentBleedBottomOffset="0"', f'DocumentBleedBottomOffset="{BLEED}"')
    .replace('DocumentBleedInsideOrLeftOffset="0"', f'DocumentBleedInsideOrLeftOffset="{BLEED}"').replace('DocumentBleedOutsideOrRightOffset="0"', f'DocumentBleedOutsideOrRightOffset="{BLEED}"')
    .replace('AllowPageShuffle="true"', 'AllowPageShuffle="false"')), pref, count=1)
assert f'PageWidth="{PW}"' in pref and 'AllowPageShuffle="false"' in pref
pref = re.sub(r'<MarginPreference [^>]*/>', lambda m: margin_xml().replace(f' ColumnsPositions="0 {num(PW-MI-MO,4)}"', ''), pref, count=1)
wr('Resources/Preferences.xml', pref)

# Nuances
g = rd('Resources/Graphic.xml')
colors = ''.join(f'<Color Self={quoteattr(s)} Model="Process" Space="CMYK" ColorValue="{v}" ColorOverride="Normal" AlternateSpace="NoAlternateColor" '
                 f'AlternateColorValue="" Name={quoteattr(n)} ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937"/>\n\t'
                 for (s, n, v) in COLORS.values())
i = g.index('<Ink ')
g = g[:i] + colors + g[i:]
wr('Resources/Graphic.xml', g)

# Styles
LANG = 'AppliedLanguage="$ID/French"'
def pstyle_xml(name, p):
    hy = 'true' if p['Justification'] == 'LeftJustified' else 'false'
    lead = f'<Leading type="unit">{p["Leading"]}</Leading>' if p['Leading'] != 'Auto' else '<Leading type="enumeration">Auto</Leading>'
    return (f'<ParagraphStyle Self={quoteattr("ParagraphStyle/" + name)} Name={quoteattr(name)} Imported="false" NextStyle={quoteattr("ParagraphStyle/" + name)} '
            f'FontStyle={quoteattr(p["FontStyle"])} PointSize="{p["PointSize"]}" Tracking="{p["Tracking"]}" Capitalization="{p["Capitalization"]}" '
            f'Justification="{p["Justification"]}" FillColor={quoteattr(p["FillColor"])} {LANG} Hyphenation="{hy}" KeyboardShortcut="0 0">'
            f'<Properties><BasedOn type="string">$ID/NormalParagraphStyle</BasedOn><PreviewColor type="enumeration">Nothing</PreviewColor>'
            f'{lead}<AppliedFont type="string">{p["font"]}</AppliedFont></Properties></ParagraphStyle>')
def cstyle_xml(name, d):
    attrs = ''.join(f' {k}={quoteattr(v)}' for k, v in d.items() if k not in ('font',))
    font = f'<Properties><AppliedFont type="string">{d["font"]}</AppliedFont></Properties>' if 'font' in d else ''
    return f'<CharacterStyle Self={quoteattr("CharacterStyle/" + name)} Imported="false" Name={quoteattr(name)}{attrs}>{font}</CharacterStyle>'
st = rd('Resources/Styles.xml')
st = st.replace('</RootCharacterStyleGroup>', ''.join(cstyle_xml(n, d) for n, d in CSTYLES.items()) + '</RootCharacterStyleGroup>', 1)
st = st.replace('</RootParagraphStyleGroup>', ''.join(pstyle_xml(n, p) for n, p in PSTYLES.items()) + '</RootParagraphStyleGroup>', 1)
wr('Resources/Styles.xml', st)

# Gabarit A
ms = rd('MasterSpreads/MasterSpread_uca.xml')
ms = ms.replace('GeometricBounds="0 0 759.6850393700788 566.9291338582677"', f'GeometricBounds="0 0 {PH} {PW}"')
ms = ms.replace('ItemTransform="1 0 0 1 -566.9291338582677 -379.8425196850394"', f'ItemTransform="1 0 0 1 {-PW} {-PH/2}"')
ms = ms.replace('ItemTransform="1 0 0 1 0 -379.8425196850394"', f'ItemTransform="1 0 0 1 0 {-PH/2}"')
ms = re.sub(r'<MarginPreference [^>]*/>', margin_xml(), ms)
wr('MasterSpreads/MasterSpread_uca.xml', ms)

# Planches
GRID = ('<GridDataInformation FontStyle="Regular" PointSize="12" CharacterAki="0" LineAki="9" HorizontalScale="100" VerticalScale="100" '
        'LineAlignment="LeftOrTopLineJustify" GridAlignment="AlignEmCenter" CharacterAlignment="AlignEmCenter">'
        '<Properties><AppliedFont type="string">Minion Pro</AppliedFont></Properties></GridDataInformation>')
PAGE_IDS = []
spreads = []
for s in range(2):
    sid = uid()
    pages = ''
    for side in range(2):
        pn = s * 2 + side + 2
        pid = uid(); PAGE_IDS.append(pid)
        tx = -PW if side == 0 else 0
        pages += (f'<Page Self="{pid}" GeometricBounds="0 0 {PH} {PW}" ItemTransform="1 0 0 1 {tx} {-PH/2}" Name="{pn}" '
                  f'AppliedTrapPreset="TrapPreset/$ID/kDefaultTrapStyleName" OverrideList="" AppliedMaster="uca" MasterPageTransform="1 0 0 1 0 0" '
                  f'TabOrder="" GridStartingPoint="TopOutside" UseMasterGrid="true">'
                  f'<Properties><PageColor type="enumeration">UseMasterColor</PageColor></Properties>{margin_xml()}{GRID}</Page>')
    items = ''.join(PAGE_ITEMS[s * 2]) + ''.join(PAGE_ITEMS[s * 2 + 1])
    xml = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
           f'<idPkg:Spread xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">'
           f'<Spread Self="{sid}" FlattenerOverride="Default" AllowPageShuffle="false" ItemTransform="1 0 0 1 0 {num(s * (PH + SPREAD_GAP),4)}" '
           f'ShowMasterItems="true" PageCount="2" BindingLocation="1" PageTransitionType="None" PageTransitionDirection="NotApplicable" PageTransitionDuration="Medium">'
           f'<FlattenerPreference LineArtAndTextResolution="300" GradientAndMeshResolution="150" ClipComplexRegions="false" ConvertAllStrokesToOutlines="false" ConvertAllTextToOutlines="false">'
           f'<Properties><RasterVectorBalance type="double">50</RasterVectorBalance></Properties></FlattenerPreference>'
           f'{pages}{items}</Spread></idPkg:Spread>')
    spreads.append((sid, xml))
    wr(f'Spreads/Spread_{sid}.xml', xml)
for sid, xml in STORIES:
    wr(f'Stories/Story_{sid}.xml', xml)

# designmap
dm = rd('designmap.xml')
dm = re.sub(r'StoryList="[^"]*"', 'StoryList="%s"' % ' '.join([s for s, _ in STORIES] + ['u9c']), dm, count=1)
dm = re.sub(r'\s*<idPkg:Spread src="[^"]*"/>', '', dm)
dm = re.sub(r'\s*<idPkg:Story src="[^"]*"/>', '', dm)
dm = dm.replace('<idPkg:MasterSpread src="MasterSpreads/MasterSpread_uca.xml"/>',
                '<idPkg:MasterSpread src="MasterSpreads/MasterSpread_uca.xml"/>' +
                ''.join(f'\n\t<idPkg:Spread src="Spreads/Spread_{sid}.xml"/>' for sid, _ in spreads))
dm = dm.replace('<idPkg:BackingStory src="XML/BackingStory.xml"/>',
                '<idPkg:BackingStory src="XML/BackingStory.xml"/>' +
                ''.join(f'\n\t<idPkg:Story src="Stories/Story_{sid}.xml"/>' for sid, _ in STORIES))
# Numérotation à partir de 2 : une page paire est une page de gauche, la première
# planche s'ouvre donc en double page dans n'importe quel logiciel, sans dépendre
# du réglage « autoriser le remaniement des pages ».
dm = re.sub(r'<Section Self="uc9" Length="4"([^>]*)ContinueNumbering="true"([^>]*)PageStart="ubb"',
            f'<Section Self="uc9" Length="4"\\1ContinueNumbering="false" PageNumberStart="2"\\2PageStart="{PAGE_IDS[0]}"', dm)
assert f'PageStart="{PAGE_IDS[0]}"' in dm
dm = dm.replace('Name="Layer 1"', 'Name="Calque 1"')
wr('designmap.xml', dm)

# Archive IDML : mimetype en premier, non compressé
idml = os.path.join(OUT, NAME + '.idml')
with zipfile.ZipFile(idml, 'w') as z:
    z.write(os.path.join(PKG, 'mimetype'), 'mimetype', compress_type=zipfile.ZIP_STORED)
    for root, _, files in os.walk(PKG):
        for f in sorted(files):
            full = os.path.join(root, f); rel = os.path.relpath(full, PKG)
            if rel != 'mimetype': z.write(full, rel, compress_type=zipfile.ZIP_DEFLATED)
shutil.rmtree(PKG)

# Dossier livré : l'IDML, ses liens, ses polices, un mode d'emploi ; puis le zip
DIR = os.path.join(OUT, NAME)
os.makedirs(DIR)
shutil.move(idml, os.path.join(DIR, NAME + '.idml'))
shutil.move(os.path.join(OUT, 'Links'), os.path.join(DIR, 'Links'))
shutil.copytree(os.path.join(HERE, 'polices'), os.path.join(DIR, 'Document fonts'))
shutil.copy(os.path.join(HERE, 'A LIRE.txt'), os.path.join(DIR, 'A LIRE.txt'))
if os.path.exists(ZIP): os.remove(ZIP)
with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(DIR):
        for f in sorted(files):
            full = os.path.join(root, f)
            z.write(full, os.path.relpath(full, OUT))
shutil.rmtree(OUT)
print(f'{ZIP}  ({os.path.getsize(ZIP) / 1048576:.1f} Mo)\n  {len(STORIES)} blocs de texte, {len(PSTYLES)} styles de paragraphe, '
      f'{len(CSTYLES)} styles de caractère, {len(COLORS)} nuances, '
      f'{sum(1 for i in M["items"] if i.get("file"))} visuels liés à {PPI:.0f} ppi')
