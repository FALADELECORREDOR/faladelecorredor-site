#!/usr/bin/env python3
"""Gera o site estático do FALA DELE CORREDOR em dist/.
Uso: python3 build.py            -> dist/ (produção, Vercel)
     python3 build.py --preview  -> preview/ (para prévia em artifact: sem scripts externos)
Conteúdo: data.json, strava.json e content/diario/*.md."""
import json, os, re, shutil, sys, html, datetime as dt
import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
PREVIEW = '--preview' in sys.argv
OUT = os.path.join(ROOT, 'preview' if PREVIEW else 'dist')
D = json.load(open(os.path.join(ROOT, 'data.json'), encoding='utf-8'))
STRAVA = json.load(open(os.path.join(ROOT, 'strava.json'), encoding='utf-8'))
S = D['site']
e = html.escape
MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

NAV = [('index.html', 'Início'), ('marcas.html', 'Para marcas'), ('parceiros.html', 'Parceiros e cupons'),
       ('provas.html', 'Provas 2027'), ('marcos.html', 'Marcos'), ('diario.html', 'Diário'), ('conteudo.html', 'Conteúdo')]


def img(name, alt, cls='', eager=False, sizes=''):
    return f'<img src="img/{name}.jpg" alt="{e(alt)}"{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} loading="{"eager" if eager else "lazy"}" decoding="async">'


def page(fname, title, desc, body, og='hero-desk'):
    nav = ''.join(f'<a href="{h}"{" aria-current=page" if h == fname or (fname.startswith("diario-") and h == "diario.html") else ""}>{t}</a>' for h, t in NAV)
    promos = json.dumps(D['promobar'], ensure_ascii=False)
    first = D['promobar'][0]
    full_title = 'FALA DELE CORREDOR' if fname == 'index.html' else f'{title} · FALA DELE CORREDOR'
    ext = '' if PREVIEW else '<script async src="https://www.instagram.com/embed.js"></script><script async src="https://www.tiktok.com/embed.js"></script>'
    footer_nav = ''.join(f'<a href="{h}">{t}</a>' for h, t in NAV[1:])
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(full_title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{S['url']}/img/{og}.jpg"><meta property="og:type" content="website"><meta property="og:locale" content="pt_BR">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preload" href="fonts/barlow-condensed-latin-800-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="site.css">
</head><body>
<a class="sr" href="#main">Pular para o conteúdo</a>
<div class="promo" aria-live="polite"><p id="promo">{e(first['text'])} <a href="{first['link']}">{e(first['cta'])}</a></p></div>
<header class="hdr"><div class="wrap">
  <a class="logo" href="index.html" aria-label="FALA DELE CORREDOR, início"><span class="mono">FDC</span><span class="word">Fala dele<br><span>corredor</span></span></a>
  <nav class="nav" id="nav" aria-label="Principal">{nav}</nav>
  <a class="btn sm cta" href="marcas.html">Mídia kit</a>
  <button class="menu-btn" aria-label="Abrir menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
</div></header>
<main id="main">{body}</main>
<footer class="ftr"><div class="wrap">
  <div><p class="big">Amador<br>pra amador.</p><p>Ex-120 kg, ex-fumante e rumo à primeira meia maratona. Rio de Janeiro.</p></div>
  <div><h4>Site</h4>{footer_nav}</div>
  <div><h4>Redes</h4><a href="{S['instagram']}" target="_blank" rel="noopener">Instagram</a><a href="{S['tiktok']}" target="_blank" rel="noopener">TikTok</a><a href="{S['strava']}" target="_blank" rel="noopener">Strava</a></div>
  <div><h4>Contato</h4><a href="mailto:{S['email']}">{S['email']}</a><a href="marcas.html">Para marcas</a></div>
  <div class="bottom"><span>© 2026 FALA DELE CORREDOR · Jorge Henrique</span><span>Posts com parceiros são publicidade.</span></div>
</div></footer>
<script>window.PROMOS={promos};</script>
<script src="site.js" defer></script>{ext}
</body></html>'''


def sec_hd(title, rail_id=None, link=None):
    right = ''
    if rail_id:
        right = f'<div class="arrows"><button data-rail="{rail_id}" data-dir="-1" aria-label="Anterior">&#8592;</button><button data-rail="{rail_id}" data-dir="1" aria-label="Próximo">&#8594;</button></div>'
    elif link:
        right = f'<a class="btn ghost sm" href="{link[0]}">{link[1]}</a>'
    return f'<div class="sec-hd"><h2 class="h3">{title}</h2>{right}</div>'


def post_card(p):
    return f'''<a class="card" href="{p['url']}" target="_blank" rel="noopener"><div class="ph">{img(p['img'], p['title'])}</div>
<div class="meta"><div class="kicker">{e(p['type'])} · {e(p['date'])}</div><div class="t">{e(p['title'])}</div>
<div class="big">{e(p['big'])}<small>{e(p['bigLabel'])}</small></div><div class="muted">{e(p['note'])}</div></div></a>'''


def partner_card(p):
    return f'''<a class="card" href="{p['url']}" target="_blank" rel="noopener"><div class="ph">{img(p['img'], p['title'])}</div>
<div class="meta"><div class="kicker">{e(p['brand'])} · {e(p['type'])}</div><div class="t">{e(p['title'])}</div><div class="muted">{e(p['note'])}</div></div></a>'''


def fmt_date(s):
    p = s.split('-')
    if len(p) == 2:
        return f'{MESES[int(p[1]) - 1]} {p[0]}'
    return f'{int(p[2]):02d} {MESES[int(p[1]) - 1]}'


# ---------- diário ----------
def load_posts():
    out = []
    for f in sorted(os.listdir(os.path.join(ROOT, 'content', 'diario')), reverse=True):
        if not f.endswith('.md'):
            continue
        raw = open(os.path.join(ROOT, 'content', 'diario', f), encoding='utf-8').read()
        m = re.match(r'---\n(.*?)\n---\n(.*)', raw, re.S)
        meta = dict(l.split(': ', 1) for l in m.group(1).splitlines() if ': ' in l)
        n = f[11:-3]; meta['slug'] = n if n.startswith('diario') else 'diario-' + n
        meta['html'] = markdown.markdown(m.group(2))
        out.append(meta)
    return out


POSTS = load_posts()


def post_tile(p):
    d = dt.date.fromisoformat(p['date'])
    return f'''<a class="card post-card" href="{p['slug']}.html"><div class="ph">{img(p['cover'], p['title'])}</div>
<div class="meta"><div class="kicker">{d.day:02d} {MESES[d.month - 1]} {d.year}</div><div class="t">{e(p['title'])}</div><div class="muted">{e(p['excerpt'])}</div></div></a>'''


def coupon(b):
    until = f' data-until="{b["codeUntil"]}"' if b.get('codeUntil') else ''
    return f'<div class="coupon"{until}><code{" class=long" if len(b["code"])>16 else ""}>{e(b["code"])}</code><span class="off">{e(b["off"])}</span><button class="copy" data-code="{e(b["code"])}">Copiar</button></div>'


def promo_pills(b):
    return ''.join(f'<span class="promo-pill"{f" data-until={chr(34)}{p["until"]}{chr(34)}" if p["until"] else ""}>{e(p["text"])}{f"<i>até {fmt_date(p[chr(117)+chr(110)+chr(116)+chr(105)+chr(108)])}</i>" if p["until"] else ""}</span>' for p in b['promos'])


def ig_embed(url):
    return f'<blockquote class="instagram-media" data-instgrm-permalink="{url}" data-instgrm-version="14" style="margin:0;min-width:0;width:100%;max-width:540px"><a href="{url}" target="_blank" rel="noopener">Ver no Instagram</a></blockquote>'


# ---------- páginas ----------
def home():
    nums = ''.join(f'<div><b>{e(n["value"])}</b><span>{e(n["label"])}</span></div>' for n in D['numbers'])
    brands = ''.join(f'<a href="parceiros.html" style="font:800 clamp(34px,5vw,56px)/1 var(--display);text-decoration:none">{e(b["short"])}</a>' for b in D['brands'])
    next_races = [r for r in D['races'] if r['status'] != 'feita'][:3]
    races = ''.join(f'<div class="race"><div class="d">{fmt_date(r["date"])}</div><div class="n">{e(r["name"])}<span class="tag {"meta" if r["status"] == "meta" else ""}">{e(r["status"])}</span><small>{e(r["result"])}</small></div><div class="dist">{r["distance"]}</div></div>' for r in next_races)
    body = f'''
<picture><source media="(max-width:760px)" srcset="img/hero-mob.jpg">{img("hero-desk", "Jorge sorrindo de óculos de corrida durante um treino", "hero-img", True)}</picture>
<section class="wrap hero-copy">
  <p class="eyebrow">Ex-120 kg · ex-fumante · Rio de Janeiro</p>
  <h1 class="display">Amador pra amador.<br><em>Rumo aos 21K.</em></h1>
  <p class="sub lead">Sou o Jorge. Comecei a correr em abril de 2026 e conto a jornada inteira até a minha primeira meia maratona, em maio de 2027.</p>
  <div class="btns"><a class="btn" href="marcas.html">Sou marca</a><a class="btn ghost" href="provas.html">Sou corredor</a></div>
</section>
<section class="wrap"><div class="nums">{nums}</div></section>
<section class="wrap sec">{sec_hd("Em destaque", "r-posts")}<div class="rail" id="r-posts">{"".join(post_card(p) for p in D["posts"])}</div></section>
<section class="wrap"><div class="tiles">
  <a class="tile" href="marcas.html">{img("rua-3", "Jorge correndo no meio do pelotão de uma prova")}<div class="ov"><p>Para marcas e parceiros</p><h2 class="h2">Corre junto<br>com a gente</h2><span class="btn white">Ver mídia kit</span></div></a>
  <a class="tile" href="parceiros.html">{img("hound-corrida", "Jorge correndo de regata e short da Hound")}<div class="ov"><p>Black Friday</p><h2 class="h2">Cupons<br>dos parceiros</h2><span class="btn white">Ver cupons</span></div></a>
</div></section>
<section class="wrap sec">{sec_hd("Marcas que correm comigo", link=("parceiros.html", "Parceiros"))}<div style="display:flex;gap:clamp(24px,6vw,96px);flex-wrap:wrap;align-items:center;border-block:1px solid var(--line);padding-block:28px">{brands}<span class="muted">+ assessoria Hope</span></div></section>
<section class="wrap sec">{sec_hd("Próximas provas", link=("provas.html", "Plano completo"))}<div class="races">{races}</div></section>
<section class="band"><div class="wrap"><p class="eyebrow" style="color:#bdbdbd">Diário do 21</p><h2 class="display">Corri 0 km<br>e treinei todo dia</h2><p style="max-width:52ch;margin:20px auto 28px;color:#cfcfcf">A recuperação da lesão, semana a semana, até a Meia do Rio.</p><a class="btn white" href="{POSTS[-1]['slug'] if False else [p for p in POSTS if 'ep01' in p['slug']][0]['slug']}.html">Ler o episódio 1</a></div></section>
<section class="wrap sec">{sec_hd("Do diário", link=("diario.html", "Ver tudo"))}<div class="posts">{"".join(post_tile(p) for p in POSTS[:3])}</div></section>
<section class="wrap sec" style="padding-top:0">{sec_hd("No Instagram", link=(S["instagram"], "@faladelecorredor"))}<div class="embeds">{"".join(ig_embed(p["url"]) for p in D["posts"][:3])}</div></section>
'''
    return page('index.html', 'Início', 'Jorge Henrique, ex-120 kg e ex-fumante, rumo à primeira meia maratona. Corrida amador pra amador no Rio de Janeiro.', body)


def marcas():
    ig, tt, au = D['instagram'], D['tiktok'], D['audience']
    def bars(rows):
        mx = max(v for _, v in rows)
        return '<div class="bars">' + ''.join(f'<div class="bar"><span>{e(k)}</span><span class="tr"><i style="width:{v / mx * 100:.0f}%"></i></span><b>{str(v).replace(".", ",")}%</b></div>' for k, v in rows) + '</div>'
    packs = ''.join(f'<div class="pack"><h3>{e(p["name"])}</h3><p style="margin:0">{e(p["body"])}</p><span class="for">Ideal para: {e(p["for"])}</span></div>' for p in D['packs'])
    body = f'''
<section class="phero"><div class="txt"><p class="eyebrow">Mídia kit · novembro de 2026</p><h1 class="display">Corre junto<br>com a gente</h1>
<p class="lead">Publicitário, pós-graduado em influência digital e corredor amador. Penso a peça com olhar de marca e entrego com cara de quem usa de verdade.</p>
<div class="btns" style="justify-content:flex-start"><a class="btn" href="#contato">Falar comigo</a><a class="btn ghost" href="#numeros">Ver números</a></div></div>
{img("prova-rua", "Jorge correndo em prova de rua com regata preta", eager=True)}</section>
<section class="wrap sec"><div class="nums">{''.join(f'<div><b>{e(n["value"])}</b><span>{e(n["label"])}</span></div>' for n in D["numbers"])}</div></section>
<section class="wrap sec" id="numeros" style="padding-top:0">{sec_hd("Números")}<div class="split">
  <div class="panel"><h3>Instagram</h3><p class="muted" style="margin:0">@faladelecorredor · {e(ig["period"])}</p><dl class="kv">
    <dt>Seguidores</dt><dd>{ig["followers"]}</dd><dt>Visualizações</dt><dd>{ig["views"]}</dd><dt>Visualizações de não seguidores</dt><dd>{ig["nonFollowers"]}</dd>
    <dt>Contas com interação</dt><dd>{ig["engaged"]}</dd><dt>Interações</dt><dd>{ig["interactions"]}</dd><dt>Novos seguidores</dt><dd>{ig["newFollowers"]}</dd></dl></div>
  <div class="panel"><h3>TikTok</h3><p class="muted" style="margin:0">@faladelecorredor · {e(tt["period"])}</p><dl class="kv">
    <dt>Visualizações de vídeo</dt><dd>{tt["views"]}</dd><dt>Crescimento das visualizações</dt><dd>{tt["growth"]}</dd><dt>Seguidores</dt><dd>{tt["followers"]}</dd><dt>Vídeo mais visto</dt><dd>{tt["best"]}</dd></dl></div>
</div></section>
<section class="wrap sec" style="padding-top:0">{sec_hd("Quem acompanha")}<div class="split">
  <div class="panel"><h3>Idade</h3>{bars(au["ages"])}</div>
  <div class="panel"><h3>Gênero e cidades</h3>{bars(au["gender"])}<div style="height:16px"></div>{bars(au["cities"])}</div>
</div></section>
<section class="wrap sec" style="padding-top:0">{sec_hd("Cases", "r-cases")}<div class="rail" id="r-cases">{"".join(post_card(p) for p in D["posts"])}</div></section>
<section class="wrap sec" style="padding-top:0">{sec_hd("Com parceiros", "r-part")}<div class="rail" id="r-part">{"".join(partner_card(p) for p in D["partnerPosts"])}</div>
<p class="muted" style="margin-top:20px">Hound Running: {e(D["brands"][0]["result"])}</p></section>
<section class="wrap sec" style="padding-top:0">{sec_hd("Como podemos trabalhar juntos")}<div class="packs">{packs}</div>
<p class="muted" style="margin-top:16px">Valores sob consulta. Cada proposta é montada para o objetivo da marca.</p></section>
<section class="band" id="contato"><div class="wrap"><p class="eyebrow" style="color:#bdbdbd">Contato</p><h2 class="display">Bora correr<br>juntos?</h2>
<div class="contact" style="margin-top:28px;color:var(--paper)"><span class="mail">{S["email"]}</span><button class="btn white copy-mail" data-code="{S["email"]}">Copiar e-mail</button></div></div></section>
'''
    return page('marcas.html', 'Para marcas', 'Mídia kit do FALA DELE CORREDOR: números, público, cases e formatos de parceria.', body, og='prova-rua')


def parceiros():
    cards = ''.join(f'''<article class="brand"><div class="ph">{img(b["img"], "Foto de " + b["name"])}<span class="name">{e(b["short"])}</span></div>
<div class="body"><p class="muted" style="margin:0">{e(b["segment"])}</p>{coupon(b)}{promo_pills(b)}<a class="btn" href="{b["url"]}" target="_blank" rel="noopener">Comprar na {e(b["name"])}</a></div></article>''' for b in D['brands'])
    t = D['team']
    body = f'''
<section class="wrap hero-copy" style="padding-block:56px 40px"><p class="eyebrow">Black Friday</p><h1 class="display">Se for comprar,<br>usa meu <em>cupom</em></h1>
<p class="sub lead">Marcas que eu uso de verdade, no treino e na recuperação. O cupom vale direto no site de cada uma.</p></section>
<section class="wrap"><div class="brand-grid">{cards}</div><p class="muted" style="margin-top:16px">Promoções valem até a data indicada ou enquanto durarem os estoques de cada marca. Posts com parceiros são publicidade.</p></section>
<section class="wrap sec"><div class="tiles">
  <div class="tile" style="color:var(--paper)">{img(t["img"], "Jorge correndo com a regata da Hope")}<div class="ov"><p>{e(t["segment"])}</p><h2 class="h2">{e(t["name"])}</h2><p style="max-width:40ch">{e(t["text"])}</p></div></div>
  <a class="tile" href="marcas.html">{img("orla", "Jorge correndo na orla")}<div class="ov"><p>Sua marca aqui</p><h2 class="h2">Quer ser<br>parceira?</h2><span class="btn white">Ver mídia kit</span></div></a>
</div></section>'''
    return page('parceiros.html', 'Parceiros e cupons', 'Cupons de desconto da Hound Running, Viggi e Dobro, e as promoções que estão valendo.', body, og='hound-corrida')


def provas():
    races = ''.join(f'<div class="race" data-date="{r["date"]}"><div class="d">{fmt_date(r["date"])}<br><span class="muted" style="font-size:.6em">{r["date"][:4]}</span></div><div class="n">{e(r["name"])}<span class="tag {r["status"].replace(" ", "-")}">{e(r["status"])}</span><small>{e(r["result"])}</small></div><div class="dist">{r["distance"]}</div></div>' for r in D['races'])
    prs = ''.join(f'<div><b>{k}</b><span>{v}</span></div>' for k, v in D['prs'])
    body = f'''
<section class="phero"><div class="txt"><p class="eyebrow">Plano de provas</p><h1 class="display">Rumo<br>aos 21K</h1>
<p class="lead">Cada prova até a Meia Maratona do Rio, em maio de 2027. Depois da lesão de novembro, o calendário anda junto com o joelho.</p></div>
{img("continencia", "Jorge batendo continência durante uma prova", eager=True)}</section>
<section class="wrap sec">{sec_hd("Calendário")}<div class="races">{races}</div></section>
<section class="wrap sec" style="padding-top:0">{sec_hd("Recordes pessoais")}<div class="prs">{prs}</div></section>'''
    return page('provas.html', 'Provas 2027', 'Plano de provas do FALA DELE CORREDOR até a Meia Maratona do Rio 2027 e recordes pessoais.', body, og='continencia')


def marcos():
    items = ''.join(f'<div class="ms{" next" if m.get("next") else ""}"><div><div class="w">{e(m["when"])}</div><h3>{e(m["title"])}</h3><p>{e(m["text"])}</p></div>{img(m["img"], m["title"]) if m["img"] else "<span></span>"}</div>' for m in D['milestones'])
    body = f'''
<section class="wrap hero-copy" style="padding-block:56px 32px"><p class="eyebrow">De 120 kg à primeira meia</p><h1 class="display">Marcos</h1>
<p class="sub lead">Os momentos que mudaram a jornada, inclusive os que doeram.</p></section>
<section class="wrap sec" style="padding-top:16px"><div class="tl">{items}</div></section>'''
    return page('marcos.html', 'Marcos', 'Linha do tempo do FALA DELE CORREDOR: de 120 kg e fumante à primeira meia maratona.', body, og='chegada')


def diario():
    body = f'''
<section class="wrap hero-copy" style="padding-block:56px 32px"><p class="eyebrow">Blog</p><h1 class="display">Diário</h1>
<p class="sub lead">O que não cabe num post: treinos, provas, recuperação e bastidores.</p></section>
<section class="wrap sec" style="padding-top:0"><div class="posts">{"".join(post_tile(p) for p in POSTS)}</div></section>'''
    return page('diario.html', 'Diário', 'Diário do FALA DELE CORREDOR: treinos, provas e recuperação.', body, og='grupo')


def artigo(p):
    d = dt.date.fromisoformat(p['date'])
    body = f'''<article class="wrap article"><a href="diario.html" class="muted" style="text-decoration:none">&#8592; Diário</a>
<p class="eyebrow" style="margin-top:24px">{d.day:02d} {MESES[d.month - 1]} {d.year}</p><h1 class="h2">{e(p["title"])}</h1>
{img(p["cover"], p["title"], "cover", True)}<div class="prose">{p["html"]}</div>
<p style="margin-top:40px"><a class="btn ghost" href="{S["instagram"]}" target="_blank" rel="noopener">Acompanhar no Instagram</a></p></article>'''
    return page(p['slug'] + '.html', p['title'], p['excerpt'], body, og=p['cover'])


def conteudo():
    acts = ''
    for a in STRAVA:
        stats = ''.join(f'<div><b>{v}</b><span>{l}</span></div>' for v, l in ((a.get('dist'), 'distância'), (a.get('time'), 'tempo'), (a.get('pace'), 'pace')) if v)
        d = dt.date.fromisoformat(a['date'])
        acts += f'<div class="act"><span class="ty">{e(a["type"])} · {d.day:02d} {MESES[d.month - 1]}</span><span class="nm">{e(a["name"])}</span>{f"<span class=muted>{e(a[chr(100)+chr(101)+chr(115)+chr(99)])}</span>" if a.get("desc") else ""}<div class="st">{stats}</div></div>'
    tiktok = f'<blockquote class="tiktok-embed" cite="{S["tiktok"]}" data-unique-id="faladelecorredor" data-embed-type="creator" style="max-width:780px;min-width:288px;margin:0"><section><a target="_blank" rel="noopener" href="{S["tiktok"]}">@faladelecorredor no TikTok</a></section></blockquote>'
    body = f'''
<section class="wrap hero-copy" style="padding-block:56px 32px"><p class="eyebrow">Instagram · TikTok · Strava</p><h1 class="display">Conteúdo</h1>
<p class="sub lead">O que sai nas redes, num lugar só.</p><div class="btns"><a class="btn" href="{S["instagram"]}" target="_blank" rel="noopener">Instagram</a><a class="btn ghost" href="{S["tiktok"]}" target="_blank" rel="noopener">TikTok</a><a class="btn ghost" href="{S["strava"]}" target="_blank" rel="noopener">Strava</a></div></section>
<section class="wrap sec" style="padding-top:16px">{sec_hd("Instagram", link=(S["instagram"], "Ver perfil"))}<div class="embeds">{"".join(ig_embed(p["url"]) for p in D["posts"] + D["partnerPosts"][:3])}</div></section>
<section class="wrap sec" style="padding-top:0">{sec_hd("TikTok", link=(S["tiktok"], "Ver perfil"))}{tiktok}</section>
<section class="wrap sec" style="padding-top:0">{sec_hd("Últimos treinos no Strava", link=(S["strava"], "Seguir no Strava"))}<div class="strava">{acts}</div></section>'''
    return page('conteudo.html', 'Conteúdo', 'Espelho do Instagram, TikTok e Strava do FALA DELE CORREDOR.', body, og='grupo')


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(os.path.join(ROOT, 'static'), OUT)
    pages = {'index.html': home(), 'marcas.html': marcas(), 'parceiros.html': parceiros(), 'provas.html': provas(),
             'marcos.html': marcos(), 'diario.html': diario(), 'conteudo.html': conteudo()}
    for p in POSTS:
        pages[p['slug'] + '.html'] = artigo(p)
    for name, content in pages.items():
        open(os.path.join(OUT, name), 'w', encoding='utf-8').write(content)
    urls = ''.join(f'<url><loc>{S["url"]}/{"" if n == "index.html" else n[:-5]}</loc></url>' for n in pages)
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {S["url"]}/sitemap.xml\n')
    print('ok', len(pages), 'páginas ->', OUT)


main()
