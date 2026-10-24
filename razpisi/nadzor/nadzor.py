#!/usr/bin/env python3
"""Lokalna nadzorna stran za /priprava-prijave.

Zagon (v mapi razpisi):   python nadzor/nadzor.py <ime-razpisa>
Odpre http://localhost:8765 in vsaki 2 s osveži stanje. Samo bere datoteke, nič ne spreminja.
"""
import json, sys, time, webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = 8765
RAZPIS = next((a for a in sys.argv[1:] if not a.startswith("--")), "")
SKIP = {".gitkeep"}

# Cene v USD na 1M žetonov: (vhod, izhod, branje iz predpomnilnika). Vir: cenik modelov Anthropic (stanje 2026-10).
# Pisanje v predpomnilnik je ocenjeno kot 1,25 x cena vhoda (5 min). Spremeni, če se cene spremenijo.
PRICES = {
    "fable-5-1": (10.0, 50.0, 0.25), "fable-5": (10.0, 50.0, 0.25),
    "opus-5-5": (4.0, 20.0, 0.20), "opus-5": (5.0, 25.0, 0.50), "opus-4": (5.0, 25.0, 0.50),
    "sonnet-5-5": (2.0, 10.0, 0.20), "sonnet-5": (2.0, 10.0, 0.20), "sonnet-4": (3.0, 15.0, 0.30),
    "haiku-5-5": (0.10, 0.50, 0.01), "haiku-4": (1.0, 5.0, 0.10),
}
CACHE_WRITE_X = 1.25
import os
EUR_PER_USD = float(os.environ.get("EUR_PER_USD", "0.90"))  # približen tečaj; nastavi z okoljsko spremenljivko


def _price(model):
    m = (model or "").lower()
    for key in sorted(PRICES, key=len, reverse=True):
        if key in m:
            return PRICES[key]
    return None



def newest(path):
    files = [p for p in path.rglob("*") if p.is_file() and p.name not in SKIP] if path.exists() else []
    return max((p.stat().st_mtime for p in files), default=None), len(files)


def read_size(p):
    return p.stat().st_size if p.exists() else 0


def agent_activity(label):
    """(obstaja, čas zadnje spremembe) zapisa seje agenta s to oznako; best-effort."""
    base = Path.home() / ".claude" / "projects"
    if not base.exists():
        return False, None
    newest, found = None, False
    for d in base.iterdir():
        if d.is_dir() and d.name.lower().endswith("razpisi"):
            files = sorted(d.glob("*/subagents/*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)[:12]
            for f in files:
                if _file_tokens(f)[1] == label:
                    found = True
                    t = f.stat().st_mtime
                    newest = t if newest is None else max(newest, t)
    return found, newest


def steps(now):
    vhod, viri = ROOT / "vhod" / RAZPIS, ROOT / "viri"
    izhod = ROOT / "izhod" / RAZPIS
    zahteve, osnutek, ponudba = izhod / "zahteve.md", izhod / "osnutek.md", izhod / "ponudba.md"
    k0_t, k0_n = newest(vhod / "besedilo")
    k0_done = (vhod / "besedilo").exists() or (vhod / "razpakirano").exists()
    z, o, p = read_size(zahteve) > 0, read_size(osnutek) > 0, read_size(ponudba) > 0

    def state(done, ready, path):
        if done:
            recent = path.exists() and now - path.stat().st_mtime < 20
            return "pise" if recent else "konec"
        return "tece" if ready else "caka"

    def mt(path):
        return path.stat().st_mtime if path.exists() and path.stat().st_size > 0 else None

    pregled = izhod / "pregled.md"
    tz, to, tp, tr = mt(zahteve), mt(osnutek), mt(ponudba), mt(pregled)
    ready = bool(o and p and state(o, z, osnutek) == "konec" and state(p, z, ponudba) == "konec")
    seen, last = agent_activity("pregledovalec")
    if tr is not None:
        pregled_state = state(True, ready, pregled)
    elif seen and last is not None and now - last < 45:
        pregled_state = "tece"
    elif seen and ready:
        pregled_state = "stop"
    elif ready:
        pregled_state = "pripr"
    else:
        pregled_state = "caka"
    return [
        {"id": "k0", "naziv": "Korak 0: priprava datotek", "stanje": "konec" if k0_done else "tece",
         "opis": f"{k0_n} pretvorjenih datotek v besedilo/" if k0_done else "razpakiranje in pretvorba",
         "zacetek": None, "konec": k0_t if k0_done else None},
        {"id": "analitik", "naziv": "analitik-razpisa", "stanje": state(z, k0_done, zahteve),
         "opis": "zahteve.md", "datoteka": "zahteve.md", "velikost": read_size(zahteve),
         "zacetek": k0_t if k0_done else None, "konec": tz},
        {"id": "pisec", "naziv": "pisec-prijave", "stanje": state(o, z, osnutek),
         "opis": "osnutek.md", "datoteka": "osnutek.md", "velikost": read_size(osnutek),
         "zacetek": tz, "konec": to},
        {"id": "kalkulant", "naziv": "kalkulant", "stanje": state(p, z, ponudba),
         "opis": "ponudba.md", "datoteka": "ponudba.md", "velikost": read_size(ponudba),
         "zacetek": tz, "konec": tp},
        {"id": "pregled", "naziv": "pregledovalec", "stanje": pregled_state,
         "opis": "pregled.md", "datoteka": "pregled.md", "velikost": read_size(pregled),
         "zacetek": max(to, tp) if (to and tp) else None, "konec": tr},
    ]


def recent_files(now, limit=15):
    out = []
    for sub in ("vhod", "viri", "izhod"):
        base = ROOT / sub
        if base.exists():
            for f in base.rglob("*"):
                if f.is_file() and f.name not in SKIP:
                    out.append((f.stat().st_mtime, f))
    out.sort(reverse=True)
    return [{"pot": str(f.relative_to(ROOT)).replace("\\", "/"), "pred": int(now - t)} for t, f in out[:limit]]


def transcript_events(limit=25):
    """Best-effort: zadnji dogodki iz zapisov seje Claude Code (~/.claude/projects/*razpisi*)."""
    base = Path.home() / ".claude" / "projects"
    if not base.exists():
        return []
    dirs = [d for d in base.iterdir() if d.is_dir() and d.name.lower().endswith("razpisi")]
    files = [f for d in dirs for f in d.rglob("*.jsonl")]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    events = []
    for f in files[:4]:
        who = "glavna seja" if f.parent == dirs[0] or f.parent in dirs else "agent"
        try:
            lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()[-60:]
        except OSError:
            continue
        for line in lines:
            try:
                e = json.loads(line)
                msg = e.get("message", {})
                content = msg.get("content", [])
                if isinstance(content, str):
                    content = [{"type": "text", "text": content}]
                for c in content:
                    if c.get("type") == "tool_use":
                        inp = c.get("input", {})
                        arg = inp.get("file_path") or inp.get("pattern") or inp.get("command") or ""
                        events.append((e.get("timestamp", ""), who, f"{c.get('name')} {str(arg)[:90]}"))
                    elif c.get("type") == "text" and msg.get("role") == "assistant" and c.get("text", "").strip():
                        events.append((e.get("timestamp", ""), who, c["text"].strip().replace("\n", " ")[:140]))
            except (ValueError, AttributeError):
                continue
    events.sort(key=lambda x: x[0], reverse=True)
    return [{"cas": t[11:19], "kdo": w, "kaj": s} for t, w, s in events[:limit]]


MARKER = Path(__file__).resolve().parent / ".stroski_od.json"


def get_od():
    """Čas (epoch), od katerega se šteje strošek za ta razpis; 0 = vse."""
    try:
        return float(json.loads(MARKER.read_text(encoding="utf-8")).get(RAZPIS, 0))
    except (OSError, ValueError):
        return 0.0


def set_od(t):
    try:
        data = json.loads(MARKER.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    data[RAZPIS] = t
    MARKER.write_text(json.dumps(data), encoding="utf-8")


def _ts(e, fallback):
    try:
        return datetime.fromisoformat(str(e.get("timestamp")).replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError):
        return fallback


_TOK_CACHE = {}
AGENTI = ("analitik-razpisa", "pisec-prijave", "kalkulant", "pregledovalec")


def _label_from(line):
    low = line.lower()
    found = [a for a in AGENTI if a in low]
    if len(found) == 1:
        return found[0]
    for kw, a in (("pregled", AGENTI[3]), ("analiz", AGENTI[0]), ("cenovn", AGENTI[2]),
                  ("kalkul", AGENTI[2]), ("osnutek", AGENTI[1])):
        if kw in low:
            return a
    return ""


def _label_from_meta(f):
    """Tip agenta iz datoteke agent-<id>.meta.json (zapis ob transkriptu); ime polja ni predpostavljeno."""
    meta = f.with_name(f.stem + ".meta.json")
    try:
        data = json.loads(meta.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, ValueError):
        return None

    def values(x):
        if isinstance(x, dict):
            for v in x.values():
                yield from values(v)
        elif isinstance(x, list):
            for v in x:
                yield from values(v)
        elif isinstance(x, str):
            yield x

    for v in values(data):
        if v in AGENTI:
            return v
    return None


def _file_tokens(f, od=0.0):
    """Seštevek žetonov iz zapisa seje (sporočila od časa `od`); vsako sporočilo (message.id) se šteje enkrat."""
    key = (str(f), f.stat().st_mtime, f.stat().st_size, od)
    if key in _TOK_CACHE:
        return _TOK_CACHE[key]
    msgs, label = {}, _label_from_meta(f)
    try:
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines()):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if not label and e.get("type") == "user":
                label = _label_from(line)
            m = e.get("message") or {}
            u = m.get("usage")
            if isinstance(u, dict) and m.get("role") == "assistant" and _ts(e, f.stat().st_mtime) >= od:
                mid = m.get("id") or f"{f.name}:{i}"
                prev = msgs.get(mid)
                if prev is None or u.get("output_tokens", 0) >= prev[0].get("output_tokens", 0):
                    msgs[mid] = (u, m.get("model"))
    except OSError:
        pass
    t = {"vhod": 0, "izhod": 0, "cache_beri": 0, "cache_pisi": 0, "usd": 0.0, "brez_cene": 0}
    for u, model in msgs.values():
        vh, iz = u.get("input_tokens", 0) or 0, u.get("output_tokens", 0) or 0
        cr, cw = u.get("cache_read_input_tokens", 0) or 0, u.get("cache_creation_input_tokens", 0) or 0
        t["vhod"] += vh
        t["izhod"] += iz
        t["cache_beri"] += cr
        t["cache_pisi"] += cw
        pr = _price(model)
        if pr:
            t["usd"] += (vh * pr[0] + iz * pr[1] + cr * pr[2] + cw * pr[0] * CACHE_WRITE_X) / 1e6
        else:
            t["brez_cene"] += vh + iz + cr + cw
    res = (t, label)
    _TOK_CACHE[key] = res
    return res


def tokens():
    base = Path.home() / ".claude" / "projects"
    if not base.exists():
        return {"skupaj": None, "viri": []}
    dirs = [d for d in base.iterdir() if d.is_dir() and d.name.lower().endswith("razpisi")]
    mains = sorted((f for d in dirs for f in d.glob("*.jsonl")), key=lambda f: f.stat().st_mtime)
    if not mains:
        return {"skupaj": None, "viri": []}
    # privzeto vse seje v mapi razpisi; NADZOR_OD=razpis šteje samo seje od začetka dela na razpisu
    sel = mains
    if os.environ.get("NADZOR_OD") == "razpis":
        starts = []
        for sub in (ROOT / "vhod" / RAZPIS / "besedilo", ROOT / "vhod" / RAZPIS / "razpakirano", ROOT / "izhod" / RAZPIS):
            if sub.exists():
                starts += [f.stat().st_mtime for f in sub.rglob("*") if f.is_file()]
        if starts:
            thr = min(starts) - 120
            sel = [f for f in mains if f.stat().st_mtime >= thr] or [mains[-1]]
    files = []
    for m in sel:
        files.append(m)
        files += sorted(m.parent.glob(f"{m.stem}/**/*.jsonl"))
    mains_set = set(sel)
    od = get_od()
    names = {}
    viri, total, n = [], {"vhod": 0, "izhod": 0, "cache_beri": 0, "cache_pisi": 0, "usd": 0.0, "brez_cene": 0}, 0
    for f in files:
        t, label = _file_tokens(f, od)
        if od and not (t["vhod"] or t["izhod"] or t["cache_beri"] or t["cache_pisi"]):
            continue
        if f in mains_set:
            label = None
            ime = "glavna seja" if len(mains_set) == 1 else f"glavna seja {sorted(mains_set).index(f) + 1}"
        else:
            n += 1
            ime = label or f"agent {n}"
            if label:
                names[label] = names.get(label, 0) + 1
        viri.append({"ime": ime, "_k": label, **t})
        for k in total:
            total[k] += t[k]
    # združi vrstice po agentu; glavne seje v eno vrstico
    groups = {}
    for v in viri:
        k = v.pop("_k")
        name = k or ("glavna seja" if v["ime"].startswith("glavna seja") else v["ime"])
        g = groups.setdefault(name, {"ime": name, "zagoni": 0, "vhod": 0, "izhod": 0, "cache_beri": 0,
                                     "cache_pisi": 0, "usd": 0.0, "brez_cene": 0})
        g["zagoni"] += 1
        for key in ("vhod", "izhod", "cache_beri", "cache_pisi", "usd", "brez_cene"):
            g[key] += v[key]
    order = {a: i for i, a in enumerate(AGENTI)}
    viri = sorted(groups.values(), key=lambda g: (order.get(g["ime"], 99), g["ime"]))
    return {"skupaj": total, "viri": viri, "eur_na_usd": EUR_PER_USD, "od": od}


PAGE = """<!doctype html><html lang="sl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nadzor razpisa</title>
<style>
:root{--bg:#f3f5f8;--s:#fff;--fg:#1b2433;--m:#5b6678;--l:#c9d0dc;--ok:#0d7a6b;--okb:#d6f0ea;--run:#3b64c4;--runb:#dfe9fb;--wait:#8a95a8;--waitb:#eef1f5;--warn:#b4551a;--warnb:#fbe9dc}
@media(prefers-color-scheme:dark){:root{--bg:#11161f;--s:#1a212d;--fg:#e6ebf3;--m:#9aa6ba;--l:#2d3748;--ok:#4fd1bb;--okb:#15332e;--run:#7aa2f0;--runb:#22345a;--wait:#6f7b90;--waitb:#202938;--warn:#f0a46b;--warnb:#3a2a1d}}
body{margin:0;padding:20px;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,Segoe UI,sans-serif}
main{max-width:1180px;margin:auto;display:grid;gap:16px}
header{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px}
h1{font-size:1.4rem;margin:0}h2{font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;color:var(--m);margin:0 0 8px}
.pill{font-size:.85rem;color:var(--m)}.pill b{color:var(--fg);font-variant-numeric:tabular-nums}
.card{background:var(--s);border:1px solid var(--l);border-radius:10px;padding:14px;min-width:0}
.scroll{overflow-x:auto}
.bar{height:10px;background:var(--waitb);border-radius:6px;overflow:hidden;margin-top:6px}.bar i{display:block;height:100%;background:var(--ok);transition:width .6s}
svg{display:block;width:100%;min-width:600px;height:auto;color:var(--fg);font-family:system-ui,Segoe UI,sans-serif}
.n rect{fill:var(--waitb);stroke:var(--wait);stroke-width:1.5;transition:fill .4s,stroke .4s}
.n.stop rect{fill:var(--warnb);stroke:var(--warn);stroke-width:2}.n.konec rect{fill:var(--okb);stroke:var(--ok)}.n.tece rect,.n.pise rect{fill:var(--runb);stroke:var(--run);stroke-width:2.5}
.n.tece rect,.n.pise rect{animation:glow 1.4s ease-in-out infinite}
@keyframes glow{50%{stroke-width:5;stroke-opacity:.45}}
.nt{font:600 13px ui-monospace,Consolas,monospace;fill:currentColor}.ns{font-size:11.5px;fill:var(--m)}
.f rect{fill:var(--s);stroke:var(--l);stroke-width:1.2;transition:all .4s}.f.on rect{fill:var(--okb);stroke:var(--ok)}
.ft{font:12px ui-monospace,Consolas,monospace;fill:var(--m)}.f.on .ft{fill:currentColor}
.e{fill:none;stroke:var(--wait);stroke-width:1.4;opacity:.55}.e.konec{stroke:var(--ok);opacity:.9}
.e.tece,.e.pise{stroke:var(--run);stroke-width:2.2;opacity:1;stroke-dasharray:7 6;animation:flow .7s linear infinite}
@keyframes flow{to{stroke-dashoffset:-13}}
.band{fill:none;stroke:var(--l);stroke-dasharray:5 4}
.ic .sp,.ic .ck,.ic .wt,.ic .wr{display:none}.n.stop .ic .wt{display:none}.n.stop .ic .wr{display:block}.n .ic .wt{display:block}.n.konec .ic .wt{display:none}.n.konec .ic .ck{display:block}.n.tece .ic .wt,.n.pise .ic .wt{display:none}.n.tece .ic .sp,.n.pise .ic .sp{display:block}.spin{animation:rot .9s linear infinite;transform-box:fill-box;transform-origin:center}@keyframes rot{to{transform:rotate(360deg)}}
#rs{float:right;font:inherit;font-size:.72rem;text-transform:none;letter-spacing:0;border:1px solid var(--l);background:var(--s);color:var(--fg);border-radius:6px;padding:2px 8px;cursor:pointer}#rs:hover{border-color:var(--run)}.tt{font-size:1.6rem;font-weight:600;font-variant-numeric:tabular-nums}.tt small{font-size:.8rem;font-weight:400;color:var(--m)}.tr{display:grid;grid-template-columns:110px 1fr 120px;gap:8px;align-items:center;font-size:.85rem;margin-top:6px}.tr span:first-child{font-family:ui-monospace,Consolas,monospace}.tb{height:12px;background:var(--waitb);border-radius:4px;overflow:hidden;display:flex}.tb i{display:block;height:100%}.tb i.o{background:var(--ok)}.tb i.v{background:var(--run)}.tr .gd{text-align:right;color:var(--m);font-variant-numeric:tabular-nums}.lg{font-size:.78rem;color:var(--m);margin-top:8px}.gl{font-size:11.5px;fill:var(--m)}
.gantt{display:grid;gap:6px;position:relative}
.g{display:grid;grid-template-columns:110px 1fr 50px;gap:8px;align-items:center;font-size:.85rem}
.g span:first-child{font-family:ui-monospace,Consolas,monospace}.gt{position:relative;height:16px;background:var(--waitb);border-radius:4px}
.gb{position:absolute;top:0;bottom:0;border-radius:4px;background:var(--ok);min-width:3px}.gb.tece,.gb.pise{background:var(--run);animation:pulse 1.2s ease-in-out infinite}
@keyframes pulse{50%{opacity:.55}}.gd{text-align:right;color:var(--m);font-variant-numeric:tabular-nums}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:760px){.cols{grid-template-columns:1fr}}
table{width:100%;border-collapse:collapse;font-size:.82rem}td{padding:4px 6px;border-bottom:1px solid var(--l);vertical-align:top;word-break:break-word}
td:first-child{color:var(--m);white-space:nowrap}code{font-family:ui-monospace,Consolas,monospace}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
</style>
<main>
<header><h1>Nadzor razpisa: <span id=r></span></h1><div class=pill>Pretečeno <b id=el>0:00</b> · končano <b id=pc>0/5</b> · žetoni <b id=tk>–</b> · strošek <b id=ec>–</b></div></header>
<div class=cols>
<div class=card><h2>Časovnica</h2><div class=gantt id=gantt></div></div>
<div class=card><h2>Porabljeni žetoni <button id=rs type=button>Ponastavi stroške</button></h2><div class=lg id=od></div><div id=tok></div></div>
</div>
<div class=card><h2>Potek</h2><div class=bar><i id=pb style="width:0"></i></div>
<div class=scroll style="margin-top:10px">
<svg viewBox="0 0 800 560" role="img" aria-label="Živi diagram poteka agentov">
<defs></defs>
<g id=edges>
 <path class=e data-d=k0 d="M405 62 V110"/>
 <path class=e data-d=analitik d="M160 138 H285"/>
 <path class=e data-d=analitik d="M525 138 H600"/>
 <path class=e data-d=pisec d="M405 166 V208 H265 V250"/>
 <path class=e data-d=kalkulant d="M405 208 H535 V250"/>
 <path class=e data-d=pisec d="M110 278 H135"/>
 <path class=e data-d=pisec d="M265 306 V352"/>
 <path class=e data-d=kalkulant d="M535 306 V352"/>
 <path class=e data-d=pregled d="M265 386 V412 H405 V428"/>
 <path class=e data-d=pregled d="M535 386 V412 H405"/>
</g>
<rect class=band x="135" y="236" width="530" height="96" rx="8"/><text class=gl x="145" y="230">vzporedno</text>
<g class="n konec" id=s-skill><rect x="255" y="14" width="300" height="48" rx="6"/><text class=nt x="405" y="35" text-anchor=middle>/priprava-prijave</text><text class=ns x="405" y="52" text-anchor=middle id=t-skill>zagnano</text><g transform="translate(279,38)" class=ic><g class=sp><circle r="9" fill="none" stroke="var(--wait)" stroke-opacity=".25" stroke-width="3"/><g class=spin><circle r="9" fill="none" stroke="var(--run)" stroke-width="3" stroke-dasharray="20 60" stroke-linecap="round"/></g></g><g class=ck><circle r="9" fill="var(--ok)"/><path d="M-4.5 0 L-1.2 3.6 L5 -3.8" fill="none" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g><g class=wr><circle r="9" fill="var(--warn)"/><path d="M0 -5 V1" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round"/><circle cy="5" r="1.4" fill="var(--s)"/></g><g class=wt><circle r="9" fill="none" stroke="var(--wait)" stroke-width="2"/><path d="M0 -5 V0 L3.5 2" fill="none" stroke="var(--wait)" stroke-width="2" stroke-linecap="round"/></g></g></g>
<g class="f on" data-f=vhod><rect x="10" y="118" width="150" height="40" rx="4"/><text class=ft x="85" y="142" text-anchor=middle>vhod/razpis/</text></g>
<g class=n id=s-analitik><rect x="285" y="110" width="240" height="56" rx="6"/><text class=nt x="405" y="133" text-anchor=middle>analitik-razpisa</text><text class=ns x="405" y="152" text-anchor=middle id=t-analitik>zahteve, merila, roki</text><g transform="translate(309,138)" class=ic><g class=sp><circle r="9" fill="none" stroke="var(--wait)" stroke-opacity=".25" stroke-width="3"/><g class=spin><circle r="9" fill="none" stroke="var(--run)" stroke-width="3" stroke-dasharray="20 60" stroke-linecap="round"/></g></g><g class=ck><circle r="9" fill="var(--ok)"/><path d="M-4.5 0 L-1.2 3.6 L5 -3.8" fill="none" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g><g class=wr><circle r="9" fill="var(--warn)"/><path d="M0 -5 V1" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round"/><circle cy="5" r="1.4" fill="var(--s)"/></g><g class=wt><circle r="9" fill="none" stroke="var(--wait)" stroke-width="2"/><path d="M0 -5 V0 L3.5 2" fill="none" stroke="var(--wait)" stroke-width="2" stroke-linecap="round"/></g></g></g>
<g class=f data-f=zahteve><rect x="600" y="118" width="170" height="40" rx="4"/><text class=ft x="685" y="142" text-anchor=middle>zahteve.md</text></g>
<g class="f on"><rect x="10" y="257" width="100" height="42" rx="4"/><text class=ft x="60" y="282" text-anchor=middle>viri/</text></g>
<g class=n id=s-pisec><rect x="150" y="250" width="230" height="56" rx="6"/><text class=nt x="265" y="273" text-anchor=middle>pisec-prijave</text><text class=ns x="265" y="292" text-anchor=middle id=t-pisec>osnutek odgovorov</text><g transform="translate(174,278)" class=ic><g class=sp><circle r="9" fill="none" stroke="var(--wait)" stroke-opacity=".25" stroke-width="3"/><g class=spin><circle r="9" fill="none" stroke="var(--run)" stroke-width="3" stroke-dasharray="20 60" stroke-linecap="round"/></g></g><g class=ck><circle r="9" fill="var(--ok)"/><path d="M-4.5 0 L-1.2 3.6 L5 -3.8" fill="none" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g><g class=wr><circle r="9" fill="var(--warn)"/><path d="M0 -5 V1" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round"/><circle cy="5" r="1.4" fill="var(--s)"/></g><g class=wt><circle r="9" fill="none" stroke="var(--wait)" stroke-width="2"/><path d="M0 -5 V0 L3.5 2" fill="none" stroke="var(--wait)" stroke-width="2" stroke-linecap="round"/></g></g></g>
<g class=n id=s-kalkulant><rect x="420" y="250" width="230" height="56" rx="6"/><text class=nt x="535" y="273" text-anchor=middle>kalkulant</text><text class=ns x="535" y="292" text-anchor=middle id=t-kalkulant>cenovna ponudba</text><g transform="translate(444,278)" class=ic><g class=sp><circle r="9" fill="none" stroke="var(--wait)" stroke-opacity=".25" stroke-width="3"/><g class=spin><circle r="9" fill="none" stroke="var(--run)" stroke-width="3" stroke-dasharray="20 60" stroke-linecap="round"/></g></g><g class=ck><circle r="9" fill="var(--ok)"/><path d="M-4.5 0 L-1.2 3.6 L5 -3.8" fill="none" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g><g class=wr><circle r="9" fill="var(--warn)"/><path d="M0 -5 V1" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round"/><circle cy="5" r="1.4" fill="var(--s)"/></g><g class=wt><circle r="9" fill="none" stroke="var(--wait)" stroke-width="2"/><path d="M0 -5 V0 L3.5 2" fill="none" stroke="var(--wait)" stroke-width="2" stroke-linecap="round"/></g></g></g>
<g class=f data-f=osnutek><rect x="190" y="352" width="150" height="34" rx="4"/><text class=ft x="265" y="374" text-anchor=middle>osnutek.md</text></g>
<g class=f data-f=ponudba><rect x="460" y="352" width="150" height="34" rx="4"/><text class=ft x="535" y="374" text-anchor=middle>ponudba.md</text></g>
<g class=n id=s-pregled><rect x="285" y="428" width="240" height="56" rx="6"/><text class=nt x="405" y="451" text-anchor=middle>pregledovalec</text><text class=ns x="405" y="470" text-anchor=middle id=t-pregled>vrzeli po merilih</text><g transform="translate(309,456)" class=ic><g class=sp><circle r="9" fill="none" stroke="var(--wait)" stroke-opacity=".25" stroke-width="3"/><g class=spin><circle r="9" fill="none" stroke="var(--run)" stroke-width="3" stroke-dasharray="20 60" stroke-linecap="round"/></g></g><g class=ck><circle r="9" fill="var(--ok)"/><path d="M-4.5 0 L-1.2 3.6 L5 -3.8" fill="none" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g><g class=wr><circle r="9" fill="var(--warn)"/><path d="M0 -5 V1" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round"/><circle cy="5" r="1.4" fill="var(--s)"/></g><g class=wt><circle r="9" fill="none" stroke="var(--wait)" stroke-width="2"/><path d="M0 -5 V0 L3.5 2" fill="none" stroke="var(--wait)" stroke-width="2" stroke-linecap="round"/></g></g></g>
<path class="e" data-d=pregled d="M405 484 V510"/>
<g class=f data-f=pregled><rect x="330" y="510" width="150" height="34" rx="4"/><text class=ft x="405" y="532" text-anchor=middle>pregled.md</text></g>
</svg></div></div>
<div class=cols>
<div class=card><h2>Zadnje spremenjene datoteke</h2><table id=files></table></div>
<div class=card><h2>Dogajanje agentov (približno)</h2><table id=ev></table></div></div>
</main>
<script>
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
const fmt=s=>{s=Math.max(0,Math.round(s));return Math.floor(s/60)+":"+String(s%60).padStart(2,"0")};
const NAZ={k0:"korak 0",analitik:"analitik",pisec:"pisec",kalkulant:"kalkulant",pregled:"pregledovalec"};
let T0=null;
async function tick(){try{
 const d=await (await fetch("/api/status")).json();const S=Object.fromEntries(d.koraki.map(s=>[s.id,s]));
 $("r").textContent=d.razpis||"(ni imena)";
 for(const id of ["analitik","pisec","kalkulant","pregled"]){const g=$("s-"+id);if(g)g.setAttribute("class","n "+S[id].stanje)}

 const TXT={konec:"končano",tece:"v teku",pise:"piše datoteko",caka:"čaka na prejšnji korak",pripr:"pripravljen, še ni zagnan",stop:"ni poročila (prekinjen?)"};
 for(const id of ["analitik","pisec","kalkulant","pregled"]){const s=S[id],t=$("t-"+id);if(!t)continue;let x=TXT[s.stanje]||s.stanje;
  if(s.stanje==="konec"&&s.zacetek&&s.konec)x+=" · "+fmt(s.konec-s.zacetek);
  if((s.stanje==="tece"||s.stanje==="pise")&&s.zacetek)x+=" · "+fmt(d.zdaj-s.zacetek);t.textContent=x}
 document.querySelectorAll("#edges .e").forEach(e=>e.setAttribute("class","e "+S[e.dataset.d].stanje));
 document.querySelectorAll("[data-f]").forEach(g=>{const k=g.dataset.f;const s=k==="zahteve"?S.analitik:k==="osnutek"?S.pisec:k==="ponudba"?S.kalkulant:k==="pregled"?S.pregled:null;
  if(s)g.setAttribute("class","f"+(s.velikost>0?" on":""));});
 const done=d.koraki.filter(s=>s.stanje==="konec").length;$("pc").textContent=done+"/5";$("pb").style.width=done*20+"%";
 const starts=d.koraki.map(s=>s.zacetek||s.konec).filter(Boolean);
 if(starts.length){const t=Math.min(...starts);if(T0===null||t<T0)T0=t}
 const now=d.zdaj;$("el").textContent=T0?fmt(now-T0):"0:00";
 const span=Math.max(10,now-(T0||now));
 $("gantt").innerHTML=d.koraki.filter(s=>s.id!=="k0"||s.konec).map(s=>{
  const a=s.zacetek||(s.id==="k0"?T0:null);const b=s.konec||(s.stanje==="tece"||s.stanje==="pise"?now:null);
  if(!a||!b)return `<div class=g><span>${NAZ[s.id]}</span><div class=gt></div><span class=gd>čaka</span></div>`;
  const l=(a-T0)/span*100,w=Math.max(.5,(b-a)/span*100);
  return `<div class=g><span>${NAZ[s.id]}</span><div class=gt><div class="gb ${s.stanje}" style="left:${l}%;width:${w}%"></div></div><span class=gd>${fmt(b-a)}</span></div>`}).join("");
 $("files").innerHTML=d.datoteke.map(f=>`<tr><td>pred ${f.pred} s</td><td><code>${esc(f.pot)}</code></td></tr>`).join("")||"<tr><td>Ni datotek.</td></tr>";
 $("ev").innerHTML=d.dogodki.map(e=>`<tr><td>${esc(e.cas)}</td><td>${esc(e.kdo)}</td><td>${esc(e.kaj)}</td></tr>`).join("")||"<tr><td>Ni zapisa seje.</td></tr>";

 const Z=d.zetoni||{},K=Z.skupaj;if(Z.od)$("od").textContent="šteto od "+new Date(Z.od*1000).toLocaleString("sl-SI");else $("od").textContent="";
 if(K){const nf=n=>n>=1e6?(n/1e6).toFixed(2)+" M":n>=1e3?(n/1e3).toFixed(1)+" k":String(n);
  const tot=K.vhod+K.izhod+K.cache_pisi;$("tk").textContent=nf(tot);const R=Z.eur_na_usd||0.9;const eur=x=>(x*R).toLocaleString("sl-SI",{style:"currency",currency:"EUR",minimumFractionDigits:2});$("ec").textContent="≈ "+eur(K.usd);
  const mx=Math.max(1,...Z.viri.map(v=>v.vhod+v.izhod+v.cache_pisi));
  $("tok").innerHTML=`<div class=tt>${nf(tot)} <small>žetonov (vhod ${nf(K.vhod+K.cache_pisi)} · izhod ${nf(K.izhod)}) + ${nf(K.cache_beri)} prebranih iz predpomnilnika</small></div><div class=tt>≈ ${eur(K.usd)} <small>ocenjen strošek po cenah API (vse seje v mapi razpisi) (${(R).toFixed(2)} EUR za 1 USD)${K.brez_cene?" · "+nf(K.brez_cene)+" žetonov brez znane cene ni všteto":""}</small></div>`
   +Z.viri.map(v=>{const vh=v.vhod+v.cache_pisi,t=vh+v.izhod;return `<div class=tr><span>${esc(v.ime)}${v.zagoni>1?" ×"+v.zagoni:""}</span><div class=tb><i class=v style="width:${vh/mx*100}%"></i><i class=o style="width:${v.izhod/mx*100}%"></i></div><span class=gd>${nf(t)} · ${eur(v.usd)}</span></div>`}).join("")
   +'<div class=lg><i style="color:var(--run)">■</i> vhod &nbsp; <i style="color:var(--ok)">■</i> izhod · strošek vključuje tudi predpomnilnik po njegovi ceni</div>';
 }else{$("tok").innerHTML="<div class=lg>Ni zapisa seje (~/.claude/projects/…razpisi).</div>"}
}catch(e){}}
$("rs").addEventListener("click",async()=>{if($("rs").dataset.sure!=="1"){$("rs").dataset.sure="1";$("rs").textContent="Klikni še enkrat za potrditev";setTimeout(()=>{$("rs").dataset.sure="";$("rs").textContent="Ponastavi stroške"},4000);return}
 $("rs").dataset.sure="";$("rs").textContent="Ponastavi stroške";try{await fetch("/api/reset",{method:"POST"})}catch(e){}tick()});
tick();setInterval(tick,2000);
</script></html>"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/status"):
            now = time.time()
            body = json.dumps({"razpis": RAZPIS, "koraki": steps(now), "datoteke": recent_files(now),
                               "dogodki": transcript_events(), "zetoni": tokens(), "zdaj": now}, ensure_ascii=False).encode("utf-8")
            ctype = "application/json; charset=utf-8"
        else:
            body, ctype = PAGE.encode("utf-8"), "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path.startswith("/api/reset"):
            set_od(time.time())
            body = b'{"ok": true}'
        else:
            body = b'{"ok": false}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    if "--ponastavi" in sys.argv:
        RAZPIS = next((a for a in sys.argv[1:] if not a.startswith("--")), "")
        set_od(time.time())
        print(f"Stroški za '{RAZPIS}' se štejejo od zdaj.")
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print(f"Nadzor razpisa '{RAZPIS}': http://localhost:{PORT}  (Ctrl+C za konec)")
    webbrowser.open(f"http://localhost:{PORT}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
