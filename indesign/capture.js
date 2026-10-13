// Mesure la page HTML et exporte les visuels, pour reconstruire l'étude en IDML.
// Appelé par build.py : node capture.js <spec.json> <html> <dossier-sortie>
const fs = require('fs');
const path = require('path');
let chromium;
try { ({ chromium } = require('playwright')); }
catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }

const [specPath, htmlPath, outDir] = process.argv.slice(2);
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
const PAGE_W = 1000;          // largeur de page en px CSS
const DSF = spec.dsf || 2.5;  // 1000 px × 2,5 = 2500 px pour 210 mm ≈ 302 ppi

const CAPTURE_CSS = `
.barre,.legende-ecran{display:none!important}
html,body{background:transparent!important}
.livre{padding:60px!important;gap:0!important;display:block!important}
.spread{display:block!important;width:${PAGE_W}px!important;box-shadow:none!important}
.page{width:${PAGE_W}px!important;box-shadow:none!important}
.page::before,.page::after{display:none!important}
.iso .page{background:transparent!important}
.iso .page *{visibility:hidden!important}
.iso [data-iso],.iso [data-iso] *{visibility:visible!important}
[data-hide],[data-hide] *,.iso [data-hide],.iso [data-hide] *{visibility:hidden!important}
`;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: PAGE_W + 120, height: 1500 }, deviceScaleFactor: DSF });
  await page.goto('file://' + path.resolve(htmlPath));
  await page.addStyleTag({ content: CAPTURE_CSS });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500);

  const results = [];
  for (const item of spec.items) {
    // Mesures et textes, dans le contexte de la page
    const found = await page.evaluate(({ item }) => {
      const pages = [...document.querySelectorAll('.page')];
      const pg = pages[item.page];
      const pr = pg.getBoundingClientRect();
      const box = el => { const r = el.getBoundingClientRect(); return [r.left - pr.left, r.top - pr.top, r.width, r.height]; };
      const cbox = el => { const r = el.getBoundingClientRect(); const c = getComputedStyle(el);
        const pl = parseFloat(c.paddingLeft) + parseFloat(c.borderLeftWidth), pr_ = parseFloat(c.paddingRight) + parseFloat(c.borderRightWidth);
        const pt = parseFloat(c.paddingTop) + parseFloat(c.borderTopWidth), pb = parseFloat(c.paddingBottom) + parseFloat(c.borderBottomWidth);
        return [r.left - pr.left + pl, r.top - pr.top + pt, r.width - pl - pr_, r.height - pt - pb]; };
      const css = el => {
        const c = getComputedStyle(el);
        return { family: c.fontFamily, weight: c.fontWeight, style: c.fontStyle, size: parseFloat(c.fontSize),
          ls: c.letterSpacing, lh: c.lineHeight, tt: c.textTransform, align: c.textAlign, color: c.color,
          va: c.verticalAlign, bg: c.backgroundColor, bgimg: c.backgroundImage, mt: parseFloat(c.marginTop),
          bt: [parseFloat(c.borderTopWidth), c.borderTopColor, c.borderTopStyle],
          bb: [parseFloat(c.borderBottomWidth), c.borderBottomColor, c.borderBottomStyle],
          bl: [parseFloat(c.borderLeftWidth), c.borderLeftColor, c.borderLeftStyle],
          br: [parseFloat(c.borderRightWidth), c.borderRightColor, c.borderRightStyle],
          outline: [parseFloat(c.outlineWidth), c.outlineColor, c.outlineStyle] };
      };
      const els = [...pg.querySelectorAll(item.sel)];
      const excl = item.exclude || [];
      const paras = root => {
        const out = []; let cur = null; let closed = true;
        const INLINE_TAGS = ['SPAN', 'B', 'EM', 'I', 'STRONG', 'SMALL', 'SUP', 'A'];
        const isBlock = el => {
          const d = getComputedStyle(el).display;
          const pd = el.parentElement ? getComputedStyle(el.parentElement).display : '';
          // un span enfant d'un flex est « blockifié » par CSS : on le garde en ligne
          if (INLINE_TAGS.includes(el.tagName) && (pd.includes('flex') || pd.includes('grid')) && el.tagName !== 'SMALL' && !el.matches('.reperes span, .reperes b')) return false;
          return !(d.startsWith('inline') || d === 'contents');
        };
        const isFlex = el => { const d = getComputedStyle(el).display; return d.includes('flex') || d.includes('grid'); };
        const push = (t, el, blockEl) => {
          if (closed) { cur = { tag: blockEl.tagName.toLowerCase(), cls: blockEl.className || '', box: cbox(blockEl), css: css(blockEl), runs: [] }; out.push(cur); closed = false; }
          cur.runs.push({ t, css: css(el), tag: el.tagName.toLowerCase(), cls: el.className || '' });
        };
        const walk = (node, blockEl) => {
          let first = true;
          for (const ch of node.childNodes) {
            if (ch.nodeType === 3) {
              let t = ch.textContent.replace(/[\t\n\r ]+/g, ' ');
              if (!t.trim() && closed) continue;
              // texte qui suit un élément dans un flex : le « gap » devient une espace demi-cadratin
              if (t.trim() && !first && isFlex(node) && !closed) t = '\u2002' + t.replace(/^ +/, '');
              if (t) { push(t, ch.parentElement, blockEl); first = false; }
            } else if (ch.nodeType === 1) {
              if (excl.some(s => ch.matches(s))) continue;
              const c = getComputedStyle(ch);
              if (c.display === 'none' || c.visibility === 'hidden') continue;
              if (ch.tagName === 'BR') { if (!closed) push(' ', ch.parentElement, blockEl); continue; }
              if (['svg', 'SVG'].includes(ch.tagName)) continue;
              if (isBlock(ch)) { closed = true; walk(ch, ch); closed = true; }
              else {
                // enfants inline d'un conteneur flex : le « gap » CSS devient une espace demi-cadratin
                if (!first && isFlex(node) && !closed) push(' ', node, blockEl);
                walk(ch, blockEl);
              }
              first = false;
            }
          }
        };
        walk(root, root);
        for (const p of out) {
          // espaces de bord et doubles espaces, comme le rendu CSS
          p.runs = p.runs.filter(r => r.t.length);
          if (p.runs.length) { p.runs[0].t = p.runs[0].t.replace(/^ +/, ''); const l = p.runs[p.runs.length - 1]; l.t = l.t.replace(/ +$/, ''); }
          for (let i = 1; i < p.runs.length; i++) if (p.runs[i - 1].t.endsWith(' ') && p.runs[i].t.startsWith(' ')) p.runs[i].t = p.runs[i].t.slice(1);
          p.runs = p.runs.filter(r => r.t.length);
        }
        return out.filter(p => p.runs.length);
      };
      return els.map(el => ({ box: box(el), css: css(el), paras: item.type === 'text' ? paras(el) : null }));
    }, { item });

    if (!found.length) { console.error('INTROUVABLE', item.id, item.sel); process.exit(2); }
    const list = item.all ? found : [found[0]];

    for (let k = 0; k < list.length; k++) {
      const res = Object.assign({}, item, list[k], { id: item.all ? `${item.id}-${k + 1}` : item.id });
      if (item.type === 'img') {
        // Isoler l'élément, appliquer le fond perdu éventuel, capturer
        const cap = await page.evaluate(({ item, k, PAGE_W }) => {
          const pg = [...document.querySelectorAll('.page')][item.page];
          const el = [...pg.querySelectorAll(item.sel)][k];
          el.setAttribute('data-iso', '');
          for (const s of item.hide || []) el.querySelectorAll(s).forEach(h => h.setAttribute('data-hide', ''));
          document.body.classList.add('iso');
          const b = item.bleed || {};
          const mm3 = PAGE_W * 3 / 210;  // 3 mm en px
          if (b.l || b.t || b.r || b.b) {
            el.dataset.saved = el.getAttribute('style') || '';
            const s = getComputedStyle(el);
            const st = el.style;
            if (b.l) st.left = (parseFloat(s.left) - mm3) + 'px';
            if (b.r) st.right = (parseFloat(s.right) - mm3) + 'px';
            if (b.t) { st.top = (parseFloat(s.top) - mm3) + 'px'; st.height = (parseFloat(s.height) + mm3) + 'px'; }
            if (b.b) { st.bottom = (parseFloat(s.bottom) - mm3) + 'px'; st.height = (parseFloat(s.height) + mm3) + 'px'; }
          }
          return true;
        }, { item, k, PAGE_W });
        await page.waitForTimeout(150);
        const geo = await page.evaluate(({ item, k }) => {
          const pg = [...document.querySelectorAll('.page')][item.page];
          const el = [...pg.querySelectorAll(item.sel)][k];
          const pr = pg.getBoundingClientRect(); const r = el.getBoundingClientRect();
          return { page: [pr.left, pr.top], box: [r.left - pr.left, r.top - pr.top, r.width, r.height], abs: [r.left + scrollX, r.top + scrollY] };
        }, { item, k });
        const pad = item.pad || 0;
        // Le cadre du fond perdu déborde de la page : on capture en coordonnées document
        const clip = { x: geo.abs[0] - pad, y: geo.abs[1] - pad, width: geo.box[2] + 2 * pad, height: geo.box[3] + 2 * pad };
        // La page est en overflow:hidden : on la libère le temps de la capture du fond perdu
        await page.evaluate(({ item, on }) => { const pg = [...document.querySelectorAll('.page')][item.page]; pg.style.overflow = on ? 'visible' : ''; pg.style.contain = on ? 'none' : ''; }, { item, on: true });
        const file = (item.name ? (item.all ? `${item.name}-${k + 1}` : item.name) : res.id) + '.png';
        await page.screenshot({ path: path.join(outDir, 'Links', file), clip, fullPage: true, omitBackground: !!item.alpha });
        await page.evaluate(({ item, on }) => { const pg = [...document.querySelectorAll('.page')][item.page]; pg.style.overflow = ''; pg.style.contain = ''; }, { item, on: false });
        res.box = [geo.box[0] - pad, geo.box[1] - pad, geo.box[2] + 2 * pad, geo.box[3] + 2 * pad];
        res.file = file;
        res.px = [Math.round(clip.width * DSF), Math.round(clip.height * DSF)];
        await page.evaluate(({ item, k }) => {
          const pg = [...document.querySelectorAll('.page')][item.page];
          const el = [...pg.querySelectorAll(item.sel)][k];
          el.removeAttribute('data-iso');
          el.querySelectorAll('[data-hide]').forEach(h => h.removeAttribute('data-hide'));
          document.body.classList.remove('iso');
          if ('saved' in el.dataset) { el.setAttribute('style', el.dataset.saved); delete el.dataset.saved; }
        }, { item, k });
      }
      results.push(res);
    }
  }
  fs.writeFileSync(path.join(outDir, 'mesures.json'), JSON.stringify({ pageW: PAGE_W, dsf: DSF, items: results }, null, 1));
  console.log(results.length, 'éléments mesurés,', results.filter(r => r.file).length, 'visuels');
  await browser.close();
})();
