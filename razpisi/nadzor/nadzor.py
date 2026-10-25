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
ACTIVE_S = 180  # agent se šteje za aktivnega, če se je zapis njegove seje spremenil v tolikšnem času (dolgo razmišljanje)
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
    obrazci_dir = izhod / "obrazci"
    porocilo = obrazci_dir / "POROCILO.md"
    forms = [f for f in obrazci_dir.glob("*") if f.is_file() and f.suffix.lower() in (".docx", ".xlsx", ".xlsm")] if obrazci_dir.exists() else []
    pdfs = [f for f in obrazci_dir.glob("*.pdf")] if obrazci_dir.exists() else []
    tz, to, tp, tr = mt(zahteve), mt(osnutek), mt(ponudba), mt(pregled)
    ready = bool(o and p and state(o, z, osnutek) == "konec" and state(p, z, ponudba) == "konec")
    seen, last = agent_activity("pregledovalec")
    if tr is not None:
        pregled_state = state(True, ready, pregled)
    elif seen and last is not None and now - last < ACTIVE_S:
        pregled_state = "tece"
    elif seen and ready:
        pregled_state = "stop"
    elif ready:
        pregled_state = "pripr"
    else:
        pregled_state = "caka"
    form_seen, form_last = agent_activity("izpolnjevalec-obrazcev")
    tobr = mt(porocilo)
    newest_form = max([f.stat().st_mtime for f in forms], default=None)
    if tobr is not None:
        obrazci_state = state(True, True, porocilo)
    elif form_seen and form_last is not None and now - form_last < ACTIVE_S:
        obrazci_state = "tece"
    elif forms and newest_form is not None and now - newest_form < ACTIVE_S:
        obrazci_state = "tece"
    elif form_seen or forms:
        obrazci_state = "stop"
    elif tr is not None:
        obrazci_state = "pripr"
    else:
        obrazci_state = "caka"
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
        {"id": "obrazci", "naziv": "izpolnjevalec-obrazcev", "stanje": obrazci_state,
         "opis": f"{len(forms)} obrazcev · {len(pdfs)} PDF", "datoteka": "obrazci/", "velikost": read_size(porocilo),
         "zacetek": tr, "konec": tobr},
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
AGENTI = ("analitik-razpisa", "pisec-prijave", "kalkulant", "pregledovalec", "izpolnjevalec-obrazcev")


def _label_from(line):
    low = line.lower()
    found = [a for a in AGENTI if a in low]
    if len(found) == 1:
        return found[0]
    for kw, a in (("pregled", AGENTI[3]), ("analiz", AGENTI[0]), ("cenovn", AGENTI[2]),
                  ("kalkul", AGENTI[2]), ("izpolni", AGENTI[4]), ("osnutek", AGENTI[1])):
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;700&family=Figtree:wght@400;600&display=swap">
<style>
/* Izgled: Amidas (Outfit + Figtree, barve logotipa), enako kot v prezentaciji */
:root{--bg:#F8FAFC;--s:#FFFFFF;--fg:#0F172A;--m:#475569;--l:#DBE3EE;--acc:#2563EB;
--ok:#7FC31B;--okd:#3C6B0E;--okb:#EEF7DF;--run:#2563EB;--runb:#DBEAFE;--wait:#94A3B8;--waitb:#E8EDF4;--warn:#B63100;--warnb:#FFEDE5;
--d1:#00A0C6;--d2:#FFBF00;--d3:#FF4100;--d4:#7FC31B;--d5:#F0037F}
@media(prefers-color-scheme:dark){:root{--bg:#0B132B;--s:#1C2541;--fg:#F1F5F9;--m:#CBD5E1;--l:#33456F;--acc:#FFBF00;
--ok:#98D423;--okd:#98D423;--okb:#1E3320;--run:#60A5FA;--runb:#1E3566;--wait:#64748B;--waitb:#263354;--warn:#FD9565;--warnb:#3A2216;
--d1:#19C4EC;--d2:#FECD5C;--d3:#FD9565;--d4:#98D423;--d5:#FD6EAE}}
body{margin:0;padding:20px;background:var(--bg);color:var(--fg);font:14px/1.5 "Figtree",system-ui,Segoe UI,sans-serif}
main{max-width:1180px;margin:auto;display:grid;gap:16px}
header{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px 24px}.brand{display:flex;align-items:center;gap:20px;flex-wrap:wrap}.logo{height:34px;width:auto;min-width:0!important}.logo-w{display:none!important}@media(prefers-color-scheme:dark){.logo-d{display:none!important}.logo-w{display:block!important}}
h1{font:700 1.5rem/1.2 "Outfit",system-ui,sans-serif;margin:0}h2{display:flex;align-items:center;gap:10px;font:600 .8rem/1.3 "Figtree",system-ui,sans-serif;text-transform:uppercase;letter-spacing:.12em;color:var(--acc);margin:0 0 10px}h2::before{content:"";flex:none;width:12px;height:12px;border-radius:999px;background:var(--dot,var(--d1))}
.pill{font-size:.85rem;color:var(--m)}.pill b{color:var(--fg);font-variant-numeric:tabular-nums}
.card{background:var(--s);border:1px solid var(--l);border-radius:16px;padding:20px;min-width:0}
.scroll{overflow-x:auto}
.bar{height:10px;background:var(--waitb);border-radius:999px;overflow:hidden;margin-top:6px}.bar i{display:block;height:100%;background:var(--ok);transition:width .6s}
.scroll svg{display:block;width:100%;min-width:600px;height:auto;color:var(--fg);font-family:"Figtree",system-ui,sans-serif}
.n rect{fill:var(--waitb);stroke:var(--wait);stroke-width:1.5;transition:fill .4s,stroke .4s}
.n.stop rect{fill:var(--warnb);stroke:var(--warn);stroke-width:2}.n.konec rect{fill:var(--okb);stroke:var(--ok)}.n.tece rect,.n.pise rect{fill:var(--runb);stroke:var(--run);stroke-width:2.5}
.n.tece rect,.n.pise rect{animation:glow 1.4s ease-in-out infinite}
@keyframes glow{50%{stroke-width:5;stroke-opacity:.45}}
.nt{font:600 14px "Outfit",system-ui,sans-serif;fill:currentColor}.ns{font-size:11.5px;fill:var(--m)}
.f rect{fill:var(--s);stroke:var(--l);stroke-width:1.2;transition:all .4s}.f.on rect{fill:var(--okb);stroke:var(--ok)}
.ft{font:600 12.5px "Figtree",system-ui,sans-serif;fill:var(--m)}.f.on .ft{fill:currentColor}
.e{fill:none;stroke:var(--wait);stroke-width:1.4;opacity:.55}.e.konec{stroke:var(--ok);opacity:1}
.e.tece,.e.pise{stroke:var(--run);stroke-width:2.2;opacity:1;stroke-dasharray:7 6;animation:flow .7s linear infinite}
@keyframes flow{to{stroke-dashoffset:-13}}
.band{fill:none;stroke:var(--wait);stroke-opacity:.6;stroke-dasharray:5 4}
.ic .sp,.ic .ck,.ic .wt,.ic .wr{display:none}.n.stop .ic .wt{display:none}.n.stop .ic .wr{display:block}.n .ic .wt{display:block}.n.konec .ic .wt{display:none}.n.konec .ic .ck{display:block}.n.tece .ic .wt,.n.pise .ic .wt{display:none}.n.tece .ic .sp,.n.pise .ic .sp{display:block}.spin{animation:rot .9s linear infinite;transform-box:fill-box;transform-origin:center}@keyframes rot{to{transform:rotate(360deg)}}
#rs{float:right;font:inherit;font-size:.72rem;text-transform:none;letter-spacing:0;border:1px solid var(--l);background:var(--s);color:var(--fg);border-radius:8px;padding:4px 10px;cursor:pointer}#rs:hover{border-color:var(--run)}.tt{font:600 1.6rem "Outfit",system-ui,sans-serif;font-weight:600;font-variant-numeric:tabular-nums}.tt small{font-size:.8rem;font-weight:400;color:var(--m)}.tr{display:grid;grid-template-columns:110px 1fr 120px;gap:8px;align-items:center;font-size:.85rem;margin-top:6px}.tr span:first-child{font-weight:600}.tb{height:12px;background:var(--waitb);border-radius:999px;overflow:hidden;display:flex}.tb i{display:block;height:100%}.tb i.o{background:var(--ok)}.tb i.v{background:var(--run)}.tr .gd{text-align:right;color:var(--m);font-variant-numeric:tabular-nums}.lg{font-size:.78rem;color:var(--m);margin-top:8px}.gl{font-size:11.5px;fill:var(--m)}
.gantt{display:grid;gap:6px;position:relative}
.g{display:grid;grid-template-columns:110px 1fr 50px;gap:8px;align-items:center;font-size:.85rem}
.g span:first-child{font-weight:600}.gt{position:relative;height:16px;background:var(--waitb);border-radius:999px}
.gb{position:absolute;top:0;bottom:0;border-radius:999px;background:var(--ok);min-width:3px}.gb.tece,.gb.pise{background:var(--run);animation:pulse 1.2s ease-in-out infinite}
@keyframes pulse{50%{opacity:.55}}.gd{text-align:right;color:var(--m);font-variant-numeric:tabular-nums}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:760px){.cols{grid-template-columns:1fr}}
table{width:100%;border-collapse:collapse;font-size:.82rem}td{padding:4px 6px;border-bottom:1px solid var(--l);vertical-align:top;word-break:break-word}
td:first-child{color:var(--m);white-space:nowrap}th{text-align:left}code{font-family:ui-monospace,Consolas,monospace;font-size:.92em}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
.tt small{font-family:"Figtree",system-ui,sans-serif;font-weight:400}
</style>
<main>
<header><div class=brand><svg class="logo logo-d" viewBox="0 0 510 129" role="img" aria-label="Amidas"><path d="M29.1048 84.2609C25.5519 84.6021 22.6944 85.2978 20.5342 86.3659C18.3577 87.439 16.6677 88.7494 15.4529 90.3236C14.2283 91.8978 13.4233 93.6352 13.0347 95.5357C12.651 97.4511 12.4486 99.4077 12.4486 101.43C12.4486 103.342 12.651 105.274 13.0347 107.236C13.4233 109.202 14.2544 110.999 15.5264 112.624C16.8131 114.253 18.6157 115.573 20.9441 116.572C23.279 117.592 26.4385 118.094 30.4372 118.094C34.9911 118.094 38.8805 117.505 42.0971 116.33C45.3252 115.158 48.7051 113.493 52.2581 111.365V82.0818L29.1048 84.2609ZM51.3453 61.3058C50.7314 59.0624 49.6782 57.2146 48.1761 55.7558C46.6837 54.3069 44.6541 53.2519 42.1036 52.5711C39.5467 51.9019 36.3398 51.5607 32.4505 51.5607C26.7863 51.5607 22.0152 51.9794 18.134 52.8233C14.2495 53.6607 10.6933 54.6448 7.47665 55.7558V45.6529C11.1358 44.0854 15.2194 42.9332 19.7195 42.2013C24.2113 41.4744 28.4599 41.1035 32.4537 41.1035C38.6715 41.1035 43.8132 41.781 47.856 43.1293C51.9201 44.4711 55.1335 46.3997 57.5255 48.925C59.9094 51.442 61.5798 54.4173 62.5203 57.8327C63.4592 61.2547 63.9343 65.0888 63.9343 69.3416V126.825H57.4308L54.9261 120.11C51.151 122.933 47.1327 125.035 42.858 126.443C38.5931 127.852 34.3396 128.544 30.1286 128.544C24.6963 128.544 20.0868 127.794 16.3167 126.284C12.54 124.771 9.485 122.782 7.16315 120.309C4.82986 117.846 3.16766 114.958 2.17328 111.658C1.17564 108.342 0.672729 104.956 0.672729 101.478C0.672729 98.3363 1.05971 95.3132 1.83856 92.3973C2.61251 89.4862 4.05591 86.8489 6.16387 84.4901C8.27019 82.1329 11.2419 80.1433 15.0659 78.5213C18.8933 76.8977 23.857 75.7999 29.9621 75.2361L52.2581 73.9043V69.1932C52.2581 66.1701 51.9511 63.541 51.3453 61.3058Z" fill="#2E2E2E"></path><path d="M188.824 65.836C188.824 60.3502 187.38 56.6018 184.495 54.5842C181.603 52.5716 177.776 51.5611 172.994 51.5611C167.888 51.5611 163.665 52.0342 160.333 53.0002C157.003 53.9463 153.671 55.3145 150.338 57.1079C151.018 59.7898 151.352 62.7074 151.352 65.836V126.802H139.676V65.836C139.676 60.3502 138.236 56.6018 135.349 54.5842C132.457 52.5716 128.625 51.5611 123.853 51.5611C118.967 51.5611 114.942 51.9798 111.783 52.8221C108.615 53.6595 105.426 54.9221 102.205 56.6018V126.802H90.5269V42.8199H97.0304L99.5286 49.71C103.529 46.7891 107.618 44.6166 111.783 43.2155C115.943 41.8094 119.975 41.1039 123.856 41.1039C135.081 41.1039 142.857 44.2919 147.187 50.676C151.521 47.6529 155.857 45.3023 160.183 43.6243C164.51 41.9479 168.789 41.1039 173.018 41.1039C182.007 41.1039 188.837 43.2039 193.505 47.4073C198.165 51.6056 200.502 57.9057 200.502 66.3123V126.802H188.824V65.836Z" fill="#2E2E2E"></path><path d="M233.348 124.256C230.255 121.462 228.703 116.693 228.703 109.978V42.807H239.977V111.32C239.977 114.237 240.503 116.22 241.558 117.288C242.609 118.345 244.418 118.872 246.967 118.872V128.438C240.98 128.438 236.444 127.05 233.348 124.256Z" fill="#2E2E2E"></path><path d="M317.751 53.2505C314.09 52.123 309.329 51.561 303.454 51.561C298.479 51.561 294.509 52.517 291.572 54.4159C288.644 56.3214 286.373 58.8484 284.769 61.9786C283.158 65.1138 282.136 68.6693 281.688 72.6518C281.246 76.6243 281.022 80.6875 281.022 84.8266C281.022 88.9772 281.246 93.0305 281.688 97.0063C282.136 100.985 283.158 104.539 284.769 107.68C286.373 110.805 288.644 113.338 291.572 115.236C294.509 117.138 298.479 118.094 303.454 118.094C306.006 118.094 308.333 117.983 310.437 117.756C312.544 117.53 314.505 117.222 316.338 116.835C318.169 116.446 319.906 115.911 321.571 115.236C323.229 114.565 324.951 113.731 326.718 112.717V56.9363C325.279 56.1549 323.813 55.4824 322.314 54.922C320.828 54.3648 319.297 53.8011 317.751 53.2505ZM303.441 41.1037C311.085 41.1037 318.854 43.4114 326.718 48.0186V0.812768H338.399V126.866H331.914L329.414 119.98C325.092 122.782 320.828 124.907 316.606 126.364C312.384 127.826 308.008 128.544 303.454 128.544C296.805 128.544 291.252 127.401 286.82 125.099C282.387 122.803 278.888 119.694 276.334 115.773C273.779 111.848 271.985 107.225 270.935 101.89C269.88 96.5778 269.346 90.886 269.346 84.8266C269.346 78.7705 269.88 73.0853 270.935 67.7545C271.985 62.4385 273.779 57.8132 276.334 53.8851C278.882 49.9637 282.371 46.8499 286.807 44.5488C291.247 42.2526 296.789 41.1037 303.441 41.1037Z" fill="#2E2E2E"></path><path d="M390.822 84.2609C387.279 84.6021 384.418 85.2977 382.253 86.3659C380.088 87.4389 378.395 88.7494 377.17 90.3236C375.956 91.8978 375.154 93.6351 374.759 95.5357C374.37 97.4511 374.179 99.4077 374.179 101.43C374.179 103.342 374.37 105.274 374.759 107.236C375.154 109.202 375.977 110.999 377.265 112.624C378.532 114.253 380.336 115.573 382.671 116.572C385.005 117.592 388.169 118.094 392.164 118.094C396.722 118.094 400.603 117.505 403.824 116.33C407.039 115.158 410.429 113.493 413.982 111.365V82.0818L390.822 84.2609ZM413.073 61.3058C412.464 59.0624 411.396 57.2146 409.908 55.7558C408.408 54.3068 406.385 53.2519 403.828 52.5711C401.279 51.9019 398.059 51.5607 394.161 51.5607C388.504 51.5607 383.733 51.9793 379.848 52.8233C375.964 53.6607 372.416 54.6448 369.204 55.7558V45.6529C372.871 44.0853 376.943 42.9331 381.437 42.2012C385.934 41.4743 390.184 41.1034 394.184 41.1034C400.399 41.1034 405.537 41.7809 409.593 43.1293C413.641 44.471 416.857 46.3996 419.246 48.9249C421.632 51.442 423.3 54.4173 424.244 57.8327C425.188 61.2547 425.66 65.0888 425.66 69.3416V126.825H419.151L416.647 120.11C412.881 122.933 408.853 125.035 404.587 126.443C400.312 127.852 396.068 128.544 391.853 128.544C386.422 128.544 381.812 127.794 378.041 126.284C374.267 124.771 371.219 122.782 368.884 120.309C366.56 117.846 364.895 114.958 363.891 111.658C362.898 108.342 362.392 104.956 362.392 101.478C362.392 98.3363 362.787 95.3132 363.562 92.3972C364.343 89.4862 365.781 86.8488 367.889 84.49C369.994 82.1329 372.966 80.1433 376.803 78.5213C380.617 76.8977 385.583 75.7998 391.689 75.2361L413.982 73.9042V69.1932C413.982 66.1701 413.682 63.541 413.073 61.3058Z" fill="#2E2E2E"></path><path d="M461.837 70.8968C462.328 72.349 463.253 73.5886 464.583 74.5957C465.912 75.5979 467.829 76.4435 470.319 77.1111C472.818 77.7902 476.051 78.2913 480.056 78.6227C485.934 79.1831 490.778 80.1078 494.598 81.4018C498.425 82.6859 501.426 84.3375 503.591 86.3568C505.751 88.3727 507.24 90.7315 508.088 93.4134C508.901 96.1085 509.326 99.186 509.326 102.661C509.326 105.911 508.774 109.079 507.657 112.157C506.548 115.251 504.685 118.01 502.092 120.476C499.478 122.949 496.059 124.907 491.789 126.364C487.516 127.826 482.214 128.545 475.904 128.545C473.92 128.545 471.751 128.435 469.421 128.215C467.09 127.988 464.802 127.678 462.519 127.279C460.251 126.897 458.119 126.442 456.125 125.927C454.125 125.431 452.465 124.894 451.134 124.327V114.237C453.686 115.136 456.992 115.994 461.037 116.835C465.089 117.669 470.102 118.094 476.091 118.094C480.423 118.094 483.994 117.669 486.817 116.835C489.652 115.994 491.89 114.842 493.562 113.383C495.22 111.941 496.39 110.309 497.053 108.519C497.721 106.726 498.059 104.833 498.059 102.807C498.059 100.905 497.852 99.1448 497.468 97.5146C497.083 95.8992 496.226 94.47 494.892 93.2403C493.562 92.0008 491.645 90.9706 489.146 90.1266C486.657 89.2826 483.348 88.7008 479.246 88.3661C473.26 87.7991 468.345 86.8777 464.513 85.5936C460.689 84.2963 457.721 82.676 455.618 80.7128C453.503 78.7496 452.066 76.5375 451.291 74.0682C450.512 71.599 450.12 68.9105 450.12 65.9929C450.12 62.9665 450.649 59.9764 451.702 56.9945C452.757 54.0307 454.466 51.3604 456.868 49.0115C459.241 46.6576 462.43 44.7488 466.414 43.2933C470.416 41.8312 475.358 41.1043 481.227 41.1043C485.104 41.1043 489.154 41.4125 493.365 42.0306C497.584 42.6521 501.522 43.7499 505.18 45.3208V55.4236C501.958 54.3076 498.521 53.3829 494.867 52.6593C491.201 51.934 486.603 51.5615 481.06 51.5615C476.95 51.5615 473.601 51.934 470.999 52.6593C468.381 53.3895 466.36 54.3901 464.918 55.6758C463.473 56.9697 462.475 58.5077 461.914 60.3077C461.365 62.0978 461.094 64.0033 461.094 66.0193C461.094 67.8127 461.336 69.4347 461.837 70.8968Z" fill="#2E2E2E"></path><path d="M98.7175 34.9998L76.2468 15.5161L53.7679 34.9998H48.7698L69.5816 5.60944H82.9054L103.717 34.9998H98.7175Z" fill="#00ADEF"></path><path d="M356.209 34.9999L380.33 5.60961H364.523L351.211 34.9999H356.209Z" fill="#80CC28"></path><path d="M301.139 23.1232C299.363 24.91 297.211 25.8084 294.656 25.8084C292.102 25.8084 289.947 24.91 288.177 23.1232C286.41 21.3331 285.517 19.1473 285.517 16.5808C285.517 14.0061 286.41 11.8286 288.177 10.0335C289.947 8.24342 292.102 7.35496 294.656 7.35496C297.211 7.35496 299.363 8.24342 301.139 10.0335C302.906 11.8286 303.799 14.0061 303.799 16.5808C303.799 19.1473 302.906 21.3331 301.139 23.1232ZM267.824 23.1232C269.603 21.3331 270.492 19.1473 270.492 16.5808C270.492 14.0061 269.603 11.8286 267.824 10.0335C266.05 8.24342 263.892 7.35496 261.333 7.35496C258.786 7.35496 256.632 8.24342 254.849 10.0335C253.078 11.8286 252.191 14.0061 252.191 16.5808C252.191 19.1473 253.078 21.3331 254.849 23.1232C256.632 24.91 258.786 25.8084 261.333 25.8084C263.892 25.8084 266.05 24.91 267.824 23.1232Z" fill="#F1511B"></path><path d="M232.729 5.60936L210.27 25.0897L187.815 5.60936H182.83L203.624 35.0294H216.931L237.712 5.60936H232.729Z" fill="#FBBC09"></path><path d="M461.986 15.1614C460.657 13.8163 458.813 12.4762 456.428 11.1311C454.045 9.78439 451.413 9.11186 448.531 9.11186C445.434 9.11186 442.83 9.66901 440.725 10.7965C438.619 11.9091 436.734 13.1454 435.079 14.4921C433.412 15.8405 431.782 17.0768 430.172 18.1877C428.567 19.3152 426.709 19.874 424.609 19.874C422.282 19.874 420.148 19.5147 418.207 18.7762C416.274 18.0493 414.249 16.907 412.152 15.3328V24.0724C413.47 25.4191 415.333 26.7642 417.706 28.1093C420.101 29.456 422.731 30.1285 425.612 30.1285C428.707 30.1285 431.313 29.5681 433.412 28.4455C435.523 27.3246 437.404 26.0884 439.066 24.7449C440.725 23.4032 442.358 22.1603 443.961 21.046C445.565 19.9202 447.421 19.3663 449.519 19.3663C451.854 19.3663 453.991 19.7273 455.923 20.4542C457.86 21.1845 459.884 22.3383 461.986 23.9059V15.1614Z" fill="#EC008C"></path></svg><svg class="logo logo-w" viewBox="0 0 510 129" role="img" aria-label="Amidas"><path d="M29.1048 84.2609C25.5519 84.6021 22.6944 85.2978 20.5342 86.3659C18.3577 87.439 16.6677 88.7494 15.4529 90.3236C14.2283 91.8978 13.4233 93.6352 13.0347 95.5357C12.651 97.4511 12.4486 99.4077 12.4486 101.43C12.4486 103.342 12.651 105.274 13.0347 107.236C13.4233 109.202 14.2544 110.999 15.5264 112.624C16.8131 114.253 18.6157 115.573 20.9441 116.572C23.279 117.592 26.4385 118.094 30.4372 118.094C34.9911 118.094 38.8805 117.505 42.0971 116.33C45.3252 115.158 48.7051 113.493 52.2581 111.365V82.0818L29.1048 84.2609ZM51.3453 61.3058C50.7314 59.0624 49.6782 57.2146 48.1761 55.7558C46.6837 54.3069 44.6541 53.2519 42.1036 52.5711C39.5467 51.9019 36.3398 51.5607 32.4505 51.5607C26.7863 51.5607 22.0152 51.9794 18.134 52.8233C14.2495 53.6607 10.6933 54.6448 7.47665 55.7558V45.6529C11.1358 44.0854 15.2194 42.9332 19.7195 42.2013C24.2113 41.4744 28.4599 41.1035 32.4537 41.1035C38.6715 41.1035 43.8132 41.781 47.856 43.1293C51.9201 44.4711 55.1335 46.3997 57.5255 48.925C59.9094 51.442 61.5798 54.4173 62.5203 57.8327C63.4592 61.2547 63.9343 65.0888 63.9343 69.3416V126.825H57.4308L54.9261 120.11C51.151 122.933 47.1327 125.035 42.858 126.443C38.5931 127.852 34.3396 128.544 30.1286 128.544C24.6963 128.544 20.0868 127.794 16.3167 126.284C12.54 124.771 9.485 122.782 7.16315 120.309C4.82986 117.846 3.16766 114.958 2.17328 111.658C1.17564 108.342 0.672729 104.956 0.672729 101.478C0.672729 98.3363 1.05971 95.3132 1.83856 92.3973C2.61251 89.4862 4.05591 86.8489 6.16387 84.4901C8.27019 82.1329 11.2419 80.1433 15.0659 78.5213C18.8933 76.8977 23.857 75.7999 29.9621 75.2361L52.2581 73.9043V69.1932C52.2581 66.1701 51.9511 63.541 51.3453 61.3058Z" fill="white"></path><path d="M188.824 65.836C188.824 60.3502 187.38 56.6018 184.495 54.5842C181.603 52.5716 177.776 51.5611 172.994 51.5611C167.888 51.5611 163.665 52.0342 160.333 53.0002C157.003 53.9463 153.671 55.3145 150.338 57.1079C151.018 59.7898 151.352 62.7074 151.352 65.836V126.802H139.676V65.836C139.676 60.3502 138.236 56.6018 135.349 54.5842C132.457 52.5716 128.625 51.5611 123.853 51.5611C118.967 51.5611 114.942 51.9798 111.783 52.8221C108.615 53.6595 105.426 54.9221 102.205 56.6018V126.802H90.5269V42.8199H97.0304L99.5286 49.71C103.529 46.7891 107.618 44.6166 111.783 43.2155C115.943 41.8094 119.975 41.1039 123.856 41.1039C135.081 41.1039 142.857 44.2919 147.187 50.676C151.521 47.6529 155.857 45.3023 160.183 43.6243C164.51 41.9479 168.789 41.1039 173.018 41.1039C182.007 41.1039 188.837 43.2039 193.505 47.4073C198.165 51.6056 200.502 57.9057 200.502 66.3123V126.802H188.824V65.836Z" fill="white"></path><path d="M233.348 124.256C230.255 121.462 228.703 116.693 228.703 109.978V42.807H239.977V111.32C239.977 114.237 240.503 116.22 241.558 117.288C242.609 118.345 244.418 118.872 246.967 118.872V128.438C240.98 128.438 236.444 127.05 233.348 124.256Z" fill="white"></path><path d="M317.751 53.2505C314.09 52.123 309.329 51.561 303.454 51.561C298.479 51.561 294.509 52.517 291.572 54.4159C288.644 56.3214 286.373 58.8484 284.769 61.9786C283.158 65.1138 282.136 68.6693 281.688 72.6518C281.246 76.6243 281.022 80.6875 281.022 84.8266C281.022 88.9772 281.246 93.0305 281.688 97.0063C282.136 100.985 283.158 104.539 284.769 107.68C286.373 110.805 288.644 113.338 291.572 115.236C294.509 117.138 298.479 118.094 303.454 118.094C306.006 118.094 308.333 117.983 310.437 117.756C312.544 117.53 314.505 117.222 316.338 116.835C318.169 116.446 319.906 115.911 321.571 115.236C323.229 114.565 324.951 113.731 326.718 112.717V56.9363C325.279 56.1549 323.813 55.4824 322.314 54.922C320.828 54.3648 319.297 53.8011 317.751 53.2505ZM303.441 41.1037C311.085 41.1037 318.854 43.4114 326.718 48.0186V0.812768H338.399V126.866H331.914L329.414 119.98C325.092 122.782 320.828 124.907 316.606 126.364C312.384 127.826 308.008 128.544 303.454 128.544C296.805 128.544 291.252 127.401 286.82 125.099C282.387 122.803 278.888 119.694 276.334 115.773C273.779 111.848 271.985 107.225 270.935 101.89C269.88 96.5778 269.346 90.886 269.346 84.8266C269.346 78.7705 269.88 73.0853 270.935 67.7545C271.985 62.4385 273.779 57.8132 276.334 53.8851C278.882 49.9637 282.371 46.8499 286.807 44.5488C291.247 42.2526 296.789 41.1037 303.441 41.1037Z" fill="white"></path><path d="M390.822 84.2609C387.279 84.6021 384.418 85.2977 382.253 86.3659C380.088 87.4389 378.395 88.7494 377.17 90.3236C375.956 91.8978 375.154 93.6351 374.759 95.5357C374.37 97.4511 374.179 99.4077 374.179 101.43C374.179 103.342 374.37 105.274 374.759 107.236C375.154 109.202 375.977 110.999 377.265 112.624C378.532 114.253 380.336 115.573 382.671 116.572C385.005 117.592 388.169 118.094 392.164 118.094C396.722 118.094 400.603 117.505 403.824 116.33C407.039 115.158 410.429 113.493 413.982 111.365V82.0818L390.822 84.2609ZM413.073 61.3058C412.464 59.0624 411.396 57.2146 409.908 55.7558C408.408 54.3068 406.385 53.2519 403.828 52.5711C401.279 51.9019 398.059 51.5607 394.161 51.5607C388.504 51.5607 383.733 51.9793 379.848 52.8233C375.964 53.6607 372.416 54.6448 369.204 55.7558V45.6529C372.871 44.0853 376.943 42.9331 381.437 42.2012C385.934 41.4743 390.184 41.1034 394.184 41.1034C400.399 41.1034 405.537 41.7809 409.593 43.1293C413.641 44.471 416.857 46.3996 419.246 48.9249C421.632 51.442 423.3 54.4173 424.244 57.8327C425.188 61.2547 425.66 65.0888 425.66 69.3416V126.825H419.151L416.647 120.11C412.881 122.933 408.853 125.035 404.587 126.443C400.312 127.852 396.068 128.544 391.853 128.544C386.422 128.544 381.812 127.794 378.041 126.284C374.267 124.771 371.219 122.782 368.884 120.309C366.56 117.846 364.895 114.958 363.891 111.658C362.898 108.342 362.392 104.956 362.392 101.478C362.392 98.3363 362.787 95.3132 363.562 92.3972C364.343 89.4862 365.781 86.8488 367.889 84.49C369.994 82.1329 372.966 80.1433 376.803 78.5213C380.617 76.8977 385.583 75.7998 391.689 75.2361L413.982 73.9042V69.1932C413.982 66.1701 413.682 63.541 413.073 61.3058Z" fill="white"></path><path d="M461.837 70.8968C462.328 72.349 463.253 73.5886 464.583 74.5957C465.912 75.5979 467.829 76.4435 470.319 77.1111C472.818 77.7902 476.051 78.2913 480.056 78.6227C485.934 79.1831 490.778 80.1078 494.598 81.4018C498.425 82.6859 501.426 84.3375 503.591 86.3568C505.751 88.3727 507.24 90.7315 508.088 93.4134C508.901 96.1085 509.326 99.186 509.326 102.661C509.326 105.911 508.774 109.079 507.657 112.157C506.548 115.251 504.685 118.01 502.092 120.476C499.478 122.949 496.059 124.907 491.789 126.364C487.516 127.826 482.214 128.545 475.904 128.545C473.92 128.545 471.751 128.435 469.421 128.215C467.09 127.988 464.802 127.678 462.519 127.279C460.251 126.897 458.119 126.442 456.125 125.927C454.125 125.431 452.465 124.894 451.134 124.327V114.237C453.686 115.136 456.992 115.994 461.037 116.835C465.089 117.669 470.102 118.094 476.091 118.094C480.423 118.094 483.994 117.669 486.817 116.835C489.652 115.994 491.89 114.842 493.562 113.383C495.22 111.941 496.39 110.309 497.053 108.519C497.721 106.726 498.059 104.833 498.059 102.807C498.059 100.905 497.852 99.1448 497.468 97.5146C497.083 95.8992 496.226 94.47 494.892 93.2403C493.562 92.0008 491.645 90.9706 489.146 90.1266C486.657 89.2826 483.348 88.7008 479.246 88.3661C473.26 87.7991 468.345 86.8777 464.513 85.5936C460.689 84.2963 457.721 82.676 455.618 80.7128C453.503 78.7496 452.066 76.5375 451.291 74.0682C450.512 71.599 450.12 68.9105 450.12 65.9929C450.12 62.9665 450.649 59.9764 451.702 56.9945C452.757 54.0307 454.466 51.3604 456.868 49.0115C459.241 46.6576 462.43 44.7488 466.414 43.2933C470.416 41.8312 475.358 41.1043 481.227 41.1043C485.104 41.1043 489.154 41.4125 493.365 42.0306C497.584 42.6521 501.522 43.7499 505.18 45.3208V55.4236C501.958 54.3076 498.521 53.3829 494.867 52.6593C491.201 51.934 486.603 51.5615 481.06 51.5615C476.95 51.5615 473.601 51.934 470.999 52.6593C468.381 53.3895 466.36 54.3901 464.918 55.6758C463.473 56.9697 462.475 58.5077 461.914 60.3077C461.365 62.0978 461.094 64.0033 461.094 66.0193C461.094 67.8127 461.336 69.4347 461.837 70.8968Z" fill="white"></path><path d="M98.7175 34.9998L76.2468 15.5161L53.7679 34.9998H48.7698L69.5816 5.60944H82.9054L103.717 34.9998H98.7175Z" fill="#00ADEF"></path><path d="M356.209 34.9999L380.33 5.60961H364.523L351.211 34.9999H356.209Z" fill="#80CC28"></path><path d="M301.139 23.1232C299.363 24.91 297.211 25.8084 294.656 25.8084C292.102 25.8084 289.947 24.91 288.177 23.1232C286.41 21.3331 285.517 19.1473 285.517 16.5808C285.517 14.0061 286.41 11.8286 288.177 10.0335C289.947 8.24342 292.102 7.35496 294.656 7.35496C297.211 7.35496 299.363 8.24342 301.139 10.0335C302.906 11.8286 303.799 14.0061 303.799 16.5808C303.799 19.1473 302.906 21.3331 301.139 23.1232ZM267.824 23.1232C269.603 21.3331 270.492 19.1473 270.492 16.5808C270.492 14.0061 269.603 11.8286 267.824 10.0335C266.05 8.24342 263.892 7.35496 261.333 7.35496C258.786 7.35496 256.632 8.24342 254.849 10.0335C253.078 11.8286 252.191 14.0061 252.191 16.5808C252.191 19.1473 253.078 21.3331 254.849 23.1232C256.632 24.91 258.786 25.8084 261.333 25.8084C263.892 25.8084 266.05 24.91 267.824 23.1232Z" fill="#F1511B"></path><path d="M232.729 5.60936L210.27 25.0897L187.815 5.60936H182.83L203.624 35.0294H216.931L237.712 5.60936H232.729Z" fill="#FBBC09"></path><path d="M461.986 15.1614C460.657 13.8163 458.813 12.4762 456.428 11.1311C454.045 9.78439 451.413 9.11186 448.531 9.11186C445.434 9.11186 442.83 9.66901 440.725 10.7965C438.619 11.9091 436.734 13.1454 435.079 14.4921C433.412 15.8405 431.782 17.0768 430.172 18.1877C428.567 19.3152 426.709 19.874 424.609 19.874C422.282 19.874 420.148 19.5147 418.207 18.7762C416.274 18.0493 414.249 16.907 412.152 15.3328V24.0724C413.47 25.4191 415.333 26.7642 417.706 28.1093C420.101 29.456 422.731 30.1285 425.612 30.1285C428.707 30.1285 431.313 29.5681 433.412 28.4455C435.523 27.3246 437.404 26.0884 439.066 24.7449C440.725 23.4032 442.358 22.1603 443.961 21.046C445.565 19.9202 447.421 19.3663 449.519 19.3663C451.854 19.3663 453.991 19.7273 455.923 20.4542C457.86 21.1845 459.884 22.3383 461.986 23.9059V15.1614Z" fill="#EC008C"></path></svg><h1>Nadzor razpisa: <span id=r></span></h1></div><div class=pill>Pretečeno <b id=el>0:00</b> · končano <b id=pc>0/5</b> · žetoni <b id=tk>–</b> · strošek <b id=ec>–</b></div></header>
<div class=cols>
<div class=card style="--dot:var(--d1)"><h2>Časovnica</h2><div class=gantt id=gantt></div></div>
<div class=card style="--dot:var(--d2)"><h2>Porabljeni žetoni <button id=rs type=button>Ponastavi stroške</button></h2><div class=lg id=od></div><div id=tok></div></div>
</div>
<div class=card style="--dot:var(--d3)"><h2>Potek</h2><div class=bar><i id=pb style="width:0"></i></div>
<div class=scroll style="margin-top:10px">
<svg viewBox="0 0 800 700" role="img" aria-label="Živi diagram poteka agentov">
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
<g class="n konec" id=s-skill><rect x="255" y="14" width="300" height="48" rx="12"/><text class=nt x="405" y="35" text-anchor=middle>/priprava-prijave</text><text class=ns x="405" y="52" text-anchor=middle id=t-skill>zagnano</text><g transform="translate(279,38)" class=ic><g class=sp><circle r="9" fill="none" stroke="var(--wait)" stroke-opacity=".25" stroke-width="3"/><g class=spin><circle r="9" fill="none" stroke="var(--run)" stroke-width="3" stroke-dasharray="20 60" stroke-linecap="round"/></g></g><g class=ck><circle r="9" fill="var(--okd)"/><path d="M-4.5 0 L-1.2 3.6 L5 -3.8" fill="none" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g><g class=wr><circle r="9" fill="var(--warn)"/><path d="M0 -5 V1" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round"/><circle cy="5" r="1.4" fill="var(--s)"/></g><g class=wt><circle r="9" fill="none" stroke="var(--wait)" stroke-width="2"/><path d="M0 -5 V0 L3.5 2" fill="none" stroke="var(--wait)" stroke-width="2" stroke-linecap="round"/></g></g></g>
<g class="f on" data-f=vhod><rect x="10" y="118" width="150" height="40" rx="8"/><text class=ft x="85" y="142" text-anchor=middle>vhod/razpis/</text></g>
<g class=n id=s-analitik><rect x="285" y="110" width="240" height="56" rx="12"/><text class=nt x="405" y="133" text-anchor=middle>analitik-razpisa</text><text class=ns x="405" y="152" text-anchor=middle id=t-analitik>zahteve, merila, roki</text><g transform="translate(309,138)" class=ic><g class=sp><circle r="9" fill="none" stroke="var(--wait)" stroke-opacity=".25" stroke-width="3"/><g class=spin><circle r="9" fill="none" stroke="var(--run)" stroke-width="3" stroke-dasharray="20 60" stroke-linecap="round"/></g></g><g class=ck><circle r="9" fill="var(--okd)"/><path d="M-4.5 0 L-1.2 3.6 L5 -3.8" fill="none" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g><g class=wr><circle r="9" fill="var(--warn)"/><path d="M0 -5 V1" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round"/><circle cy="5" r="1.4" fill="var(--s)"/></g><g class=wt><circle r="9" fill="none" stroke="var(--wait)" stroke-width="2"/><path d="M0 -5 V0 L3.5 2" fill="none" stroke="var(--wait)" stroke-width="2" stroke-linecap="round"/></g></g></g>
<g class=f data-f=zahteve><rect x="600" y="118" width="170" height="40" rx="8"/><text class=ft x="685" y="142" text-anchor=middle>zahteve.md</text></g>
<g class="f on"><rect x="10" y="257" width="100" height="42" rx="8"/><text class=ft x="60" y="282" text-anchor=middle>viri/</text></g>
<g class=n id=s-pisec><rect x="150" y="250" width="230" height="56" rx="12"/><text class=nt x="265" y="273" text-anchor=middle>pisec-prijave</text><text class=ns x="265" y="292" text-anchor=middle id=t-pisec>osnutek odgovorov</text><g transform="translate(174,278)" class=ic><g class=sp><circle r="9" fill="none" stroke="var(--wait)" stroke-opacity=".25" stroke-width="3"/><g class=spin><circle r="9" fill="none" stroke="var(--run)" stroke-width="3" stroke-dasharray="20 60" stroke-linecap="round"/></g></g><g class=ck><circle r="9" fill="var(--okd)"/><path d="M-4.5 0 L-1.2 3.6 L5 -3.8" fill="none" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g><g class=wr><circle r="9" fill="var(--warn)"/><path d="M0 -5 V1" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round"/><circle cy="5" r="1.4" fill="var(--s)"/></g><g class=wt><circle r="9" fill="none" stroke="var(--wait)" stroke-width="2"/><path d="M0 -5 V0 L3.5 2" fill="none" stroke="var(--wait)" stroke-width="2" stroke-linecap="round"/></g></g></g>
<g class=n id=s-kalkulant><rect x="420" y="250" width="230" height="56" rx="12"/><text class=nt x="535" y="273" text-anchor=middle>kalkulant</text><text class=ns x="535" y="292" text-anchor=middle id=t-kalkulant>cenovna ponudba</text><g transform="translate(444,278)" class=ic><g class=sp><circle r="9" fill="none" stroke="var(--wait)" stroke-opacity=".25" stroke-width="3"/><g class=spin><circle r="9" fill="none" stroke="var(--run)" stroke-width="3" stroke-dasharray="20 60" stroke-linecap="round"/></g></g><g class=ck><circle r="9" fill="var(--okd)"/><path d="M-4.5 0 L-1.2 3.6 L5 -3.8" fill="none" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g><g class=wr><circle r="9" fill="var(--warn)"/><path d="M0 -5 V1" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round"/><circle cy="5" r="1.4" fill="var(--s)"/></g><g class=wt><circle r="9" fill="none" stroke="var(--wait)" stroke-width="2"/><path d="M0 -5 V0 L3.5 2" fill="none" stroke="var(--wait)" stroke-width="2" stroke-linecap="round"/></g></g></g>
<g class=f data-f=osnutek><rect x="190" y="352" width="150" height="34" rx="8"/><text class=ft x="265" y="374" text-anchor=middle>osnutek.md</text></g>
<g class=f data-f=ponudba><rect x="460" y="352" width="150" height="34" rx="8"/><text class=ft x="535" y="374" text-anchor=middle>ponudba.md</text></g>
<g class=n id=s-pregled><rect x="285" y="428" width="240" height="56" rx="12"/><text class=nt x="405" y="451" text-anchor=middle>pregledovalec</text><text class=ns x="405" y="470" text-anchor=middle id=t-pregled>vrzeli po merilih</text><g transform="translate(309,456)" class=ic><g class=sp><circle r="9" fill="none" stroke="var(--wait)" stroke-opacity=".25" stroke-width="3"/><g class=spin><circle r="9" fill="none" stroke="var(--run)" stroke-width="3" stroke-dasharray="20 60" stroke-linecap="round"/></g></g><g class=ck><circle r="9" fill="var(--okd)"/><path d="M-4.5 0 L-1.2 3.6 L5 -3.8" fill="none" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g><g class=wr><circle r="9" fill="var(--warn)"/><path d="M0 -5 V1" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round"/><circle cy="5" r="1.4" fill="var(--s)"/></g><g class=wt><circle r="9" fill="none" stroke="var(--wait)" stroke-width="2"/><path d="M0 -5 V0 L3.5 2" fill="none" stroke="var(--wait)" stroke-width="2" stroke-linecap="round"/></g></g></g>
<path class="e" data-d=obrazci d="M405 544 V570"/>
<g class=n id=s-obrazci><rect x="285" y="570" width="240" height="56" rx="12"/><text class=nt x="415" y="593" text-anchor=middle style="font-size:11.5px">izpolnjevalec-obrazcev</text><text class=ns x="405" y="612" text-anchor=middle id=t-obrazci>izvirni obrazci in predračun</text><g transform="translate(309,598)" class=ic><g class=sp><circle r="9" fill="none" stroke="var(--wait)" stroke-opacity=".25" stroke-width="3"/><g class=spin><circle r="9" fill="none" stroke="var(--run)" stroke-width="3" stroke-dasharray="20 60" stroke-linecap="round"/></g></g><g class=ck><circle r="9" fill="var(--okd)"/><path d="M-4.5 0 L-1.2 3.6 L5 -3.8" fill="none" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g><g class=wr><circle r="9" fill="var(--warn)"/><path d="M0 -5 V1" stroke="var(--s)" stroke-width="2.4" stroke-linecap="round"/><circle cy="5" r="1.4" fill="var(--s)"/></g><g class=wt><circle r="9" fill="none" stroke="var(--wait)" stroke-width="2"/><path d="M0 -5 V0 L3.5 2" fill="none" stroke="var(--wait)" stroke-width="2" stroke-linecap="round"/></g></g></g>
<path class="e" data-d=obrazci d="M405 626 V652"/>
<g class=f data-f=obrazci><rect x="330" y="652" width="150" height="34" rx="8"/><text class=ft x="405" y="674" text-anchor=middle>obrazci/</text></g>
<path class="e" data-d=pregled d="M405 484 V510"/>
<g class=f data-f=pregled><rect x="330" y="510" width="150" height="34" rx="8"/><text class=ft x="405" y="532" text-anchor=middle>pregled.md</text></g>
</svg></div></div>
<div class=cols>
<div class=card style="--dot:var(--d4)"><h2>Zadnje spremenjene datoteke</h2><table id=files></table></div>
<div class=card style="--dot:var(--d5)"><h2>Dogajanje agentov (približno)</h2><table id=ev></table></div></div>
</main>
<script>
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
const fmt=s=>{s=Math.max(0,Math.round(s));return Math.floor(s/60)+":"+String(s%60).padStart(2,"0")};
const NAZ={k0:"korak 0",analitik:"analitik",pisec:"pisec",kalkulant:"kalkulant",pregled:"pregledovalec",obrazci:"obrazci"};
let T0=null;
async function tick(){try{
 const d=await (await fetch("/api/status")).json();const S=Object.fromEntries(d.koraki.map(s=>[s.id,s]));
 $("r").textContent=d.razpis||"(ni imena)";
 for(const id of ["analitik","pisec","kalkulant","pregled","obrazci"]){const g=$("s-"+id);if(g)g.setAttribute("class","n "+S[id].stanje)}

 const TXT={konec:"končano",tece:"v teku",pise:"piše datoteko",caka:"čaka na prejšnji korak",pripr:"pripravljen, še ni zagnan",stop:"ni poročila (prekinjen?)"};
 for(const id of ["analitik","pisec","kalkulant","pregled","obrazci"]){const s=S[id],t=$("t-"+id);if(!t)continue;let x=TXT[s.stanje]||s.stanje;
  if(s.stanje==="konec"&&s.zacetek&&s.konec)x+=" · "+fmt(s.konec-s.zacetek);
  if((s.stanje==="tece"||s.stanje==="pise")&&s.zacetek)x+=" · "+fmt(d.zdaj-s.zacetek);t.textContent=x}
 document.querySelectorAll("#edges .e").forEach(e=>e.setAttribute("class","e "+S[e.dataset.d].stanje));
 document.querySelectorAll("[data-f]").forEach(g=>{const k=g.dataset.f;const s=k==="zahteve"?S.analitik:k==="osnutek"?S.pisec:k==="ponudba"?S.kalkulant:k==="pregled"?S.pregled:k==="obrazci"?S.obrazci:null;
  if(s)g.setAttribute("class","f"+(s.velikost>0?" on":""));});
 const done=d.koraki.filter(s=>s.stanje==="konec").length;const nk=d.koraki.length;$("pc").textContent=done+"/"+nk;$("pb").style.width=done/nk*100+"%";
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
