#!/usr/bin/env python3
"""Lokalna nadzorna stran za /priprava-prijave.

Zagon (v mapi razpisi):   python nadzor/nadzor.py <ime-razpisa>
Odpre http://localhost:8765 in vsaki 2 s osveži stanje. Samo bere datoteke, nič ne spreminja.
"""
import json, sys, time, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = 8765
RAZPIS = sys.argv[1] if len(sys.argv) > 1 else ""
SKIP = {".gitkeep"}


def newest(path):
    files = [p for p in path.rglob("*") if p.is_file() and p.name not in SKIP] if path.exists() else []
    return max((p.stat().st_mtime for p in files), default=None), len(files)


def read_size(p):
    return p.stat().st_size if p.exists() else 0


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

    tz, to, tp = mt(zahteve), mt(osnutek), mt(ponudba)
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
        {"id": "pregled", "naziv": "pregledovalec", "stanje": "tece" if (o and p and state(o, z, osnutek) == "konec" and state(p, z, ponudba) == "konec") else "caka",
         "opis": "poročilo o vrzelih je v konzoli (agent ne piše datotek)",
         "zacetek": max(to, tp) if (to and tp) else None, "konec": None},
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


PAGE = """<!doctype html><html lang="sl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nadzor razpisa</title>
<style>
:root{--bg:#f3f5f8;--s:#fff;--fg:#1b2433;--m:#5b6678;--l:#c9d0dc;--ok:#0d7a6b;--okb:#d6f0ea;--run:#3b64c4;--runb:#dfe9fb;--wait:#8a95a8;--waitb:#eef1f5}
@media(prefers-color-scheme:dark){:root{--bg:#11161f;--s:#1a212d;--fg:#e6ebf3;--m:#9aa6ba;--l:#2d3748;--ok:#4fd1bb;--okb:#15332e;--run:#7aa2f0;--runb:#22345a;--wait:#6f7b90;--waitb:#202938}}
body{margin:0;padding:20px;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,Segoe UI,sans-serif}
main{max-width:980px;margin:auto;display:grid;gap:16px}
header{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px}
h1{font-size:1.4rem;margin:0}h2{font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;color:var(--m);margin:0 0 8px}
.pill{font-size:.85rem;color:var(--m)}.pill b{color:var(--fg);font-variant-numeric:tabular-nums}
.card{background:var(--s);border:1px solid var(--l);border-radius:10px;padding:14px;min-width:0}
.scroll{overflow-x:auto}
.bar{height:10px;background:var(--waitb);border-radius:6px;overflow:hidden;margin-top:6px}.bar i{display:block;height:100%;background:var(--ok);transition:width .6s}
svg{display:block;width:100%;min-width:600px;height:auto;color:var(--fg);font-family:system-ui,Segoe UI,sans-serif}
.n rect{fill:var(--waitb);stroke:var(--wait);stroke-width:1.5;transition:fill .4s,stroke .4s}
.n.konec rect{fill:var(--okb);stroke:var(--ok)}.n.tece rect,.n.pise rect{fill:var(--runb);stroke:var(--run);stroke-width:2.5}
.n.tece rect,.n.pise rect{animation:glow 1.4s ease-in-out infinite}
@keyframes glow{50%{stroke-width:5;stroke-opacity:.45}}
.nt{font:600 13px ui-monospace,Consolas,monospace;fill:currentColor}.ns{font-size:11.5px;fill:var(--m)}
.f rect{fill:var(--s);stroke:var(--l);stroke-width:1.2;transition:all .4s}.f.on rect{fill:var(--okb);stroke:var(--ok)}
.ft{font:12px ui-monospace,Consolas,monospace;fill:var(--m)}.f.on .ft{fill:currentColor}
.e{fill:none;stroke:var(--wait);stroke-width:1.4;opacity:.55}.e.konec{stroke:var(--ok);opacity:.9}
.e.tece,.e.pise{stroke:var(--run);stroke-width:2.2;opacity:1;stroke-dasharray:7 6;animation:flow .7s linear infinite}
@keyframes flow{to{stroke-dashoffset:-13}}
.band{fill:none;stroke:var(--l);stroke-dasharray:5 4}
.gl{font-size:11.5px;fill:var(--m)}
.gantt{display:grid;gap:6px;position:relative}
.g{display:grid;grid-template-columns:130px 1fr 60px;gap:8px;align-items:center;font-size:.85rem}
.g span:first-child{font-family:ui-monospace,Consolas,monospace}.gt{position:relative;height:16px;background:var(--waitb);border-radius:4px}
.gb{position:absolute;top:0;bottom:0;border-radius:4px;background:var(--ok);min-width:3px}.gb.tece,.gb.pise{background:var(--run);animation:pulse 1.2s ease-in-out infinite}
@keyframes pulse{50%{opacity:.55}}.gd{text-align:right;color:var(--m);font-variant-numeric:tabular-nums}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:760px){.cols{grid-template-columns:1fr}}
table{width:100%;border-collapse:collapse;font-size:.82rem}td{padding:4px 6px;border-bottom:1px solid var(--l);vertical-align:top;word-break:break-word}
td:first-child{color:var(--m);white-space:nowrap}code{font-family:ui-monospace,Consolas,monospace}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
</style>
<main>
<header><h1>Nadzor razpisa: <span id=r></span></h1><div class=pill>Pretečeno <b id=el>0:00</b> · končano <b id=pc>0/5</b></div></header>
<div class=card><h2>Potek</h2><div class=bar><i id=pb style="width:0"></i></div>
<div class=scroll style="margin-top:10px">
<svg viewBox="0 0 800 500" role="img" aria-label="Živi diagram poteka agentov">
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
<g class="n konec" id=s-skill><rect x="255" y="14" width="300" height="48" rx="6"/><text class=nt x="405" y="35" text-anchor=middle>/priprava-prijave</text><text class=ns x="405" y="52" text-anchor=middle id=t-skill>zagnano</text></g>
<g class="f on" data-f=vhod><rect x="10" y="118" width="150" height="40" rx="4"/><text class=ft x="85" y="142" text-anchor=middle>vhod/razpis/</text></g>
<g class=n id=s-analitik><rect x="285" y="110" width="240" height="56" rx="6"/><text class=nt x="405" y="133" text-anchor=middle>analitik-razpisa</text><text class=ns x="405" y="152" text-anchor=middle>zahteve, merila, roki</text></g>
<g class=f data-f=zahteve><rect x="600" y="118" width="170" height="40" rx="4"/><text class=ft x="685" y="142" text-anchor=middle>zahteve.md</text></g>
<g class="f on"><rect x="10" y="257" width="100" height="42" rx="4"/><text class=ft x="60" y="282" text-anchor=middle>viri/</text></g>
<g class=n id=s-pisec><rect x="150" y="250" width="230" height="56" rx="6"/><text class=nt x="265" y="273" text-anchor=middle>pisec-prijave</text><text class=ns x="265" y="292" text-anchor=middle>osnutek odgovorov</text></g>
<g class=n id=s-kalkulant><rect x="420" y="250" width="230" height="56" rx="6"/><text class=nt x="535" y="273" text-anchor=middle>kalkulant</text><text class=ns x="535" y="292" text-anchor=middle>cenovna ponudba</text></g>
<g class=f data-f=osnutek><rect x="190" y="352" width="150" height="34" rx="4"/><text class=ft x="265" y="374" text-anchor=middle>osnutek.md</text></g>
<g class=f data-f=ponudba><rect x="460" y="352" width="150" height="34" rx="4"/><text class=ft x="535" y="374" text-anchor=middle>ponudba.md</text></g>
<g class=n id=s-pregled><rect x="285" y="428" width="240" height="56" rx="6"/><text class=nt x="405" y="451" text-anchor=middle>pregledovalec</text><text class=ns x="405" y="470" text-anchor=middle>poročilo o vrzelih v konzoli</text></g>
<g id=s-k0 class=n><rect x="285" y="508" width="240" height="0" rx="6" style="display:none"/></g>
</svg></div></div>
<div class=card><h2>Časovnica</h2><div class=gantt id=gantt></div></div>
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
 document.querySelectorAll("#edges .e").forEach(e=>e.setAttribute("class","e "+S[e.dataset.d].stanje));
 document.querySelectorAll("[data-f]").forEach(g=>{const k=g.dataset.f;const s=k==="zahteve"?S.analitik:k==="osnutek"?S.pisec:k==="ponudba"?S.kalkulant:null;
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
}catch(e){}}
tick();setInterval(tick,2000);
</script></html>"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/status"):
            now = time.time()
            body = json.dumps({"razpis": RAZPIS, "koraki": steps(now), "datoteke": recent_files(now),
                               "dogodki": transcript_events(), "zdaj": now}, ensure_ascii=False).encode("utf-8")
            ctype = "application/json; charset=utf-8"
        else:
            body, ctype = PAGE.encode("utf-8"), "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print(f"Nadzor razpisa '{RAZPIS}': http://localhost:{PORT}  (Ctrl+C za konec)")
    webbrowser.open(f"http://localhost:{PORT}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
