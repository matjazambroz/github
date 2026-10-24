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

    return [
        {"id": "k0", "naziv": "Korak 0: priprava datotek", "stanje": "konec" if k0_done else "tece",
         "opis": f"{k0_n} pretvorjenih datotek v besedilo/" if k0_done else "razpakiranje in pretvorba"},
        {"id": "analitik", "naziv": "analitik-razpisa", "stanje": state(z, k0_done, zahteve),
         "opis": "zahteve.md", "datoteka": "zahteve.md", "velikost": read_size(zahteve)},
        {"id": "pisec", "naziv": "pisec-prijave", "stanje": state(o, z, osnutek),
         "opis": "osnutek.md", "datoteka": "osnutek.md", "velikost": read_size(osnutek)},
        {"id": "kalkulant", "naziv": "kalkulant", "stanje": state(p, z, ponudba),
         "opis": "ponudba.md", "datoteka": "ponudba.md", "velikost": read_size(ponudba)},
        {"id": "pregled", "naziv": "pregledovalec", "stanje": "tece" if (o and p) else "caka",
         "opis": "poročilo o vrzelih je v konzoli (agent ne piše datotek)"},
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
:root{--bg:#f3f5f8;--s:#fff;--fg:#1b2433;--m:#5b6678;--l:#c9d0dc;--ok:#0d7a6b;--run:#3b64c4;--wait:#8a95a8}
@media(prefers-color-scheme:dark){:root{--bg:#11161f;--s:#1a212d;--fg:#e6ebf3;--m:#9aa6ba;--l:#2d3748;--ok:#4fd1bb;--run:#7aa2f0;--wait:#6f7b90}}
body{margin:0;padding:20px;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,Segoe UI,sans-serif}
main{max-width:900px;margin:auto;display:grid;gap:18px}h1{font-size:1.4rem;margin:0}h2{font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;color:var(--m);margin:0 0 8px}
.card{background:var(--s);border:1px solid var(--l);border-radius:10px;padding:14px}
.flow{display:grid;gap:10px}.row{display:flex;gap:10px;flex-wrap:wrap}.row>*{flex:1;min-width:200px}
.step{border:2px solid var(--wait);border-radius:8px;padding:10px;background:var(--s)}
.step b{font-family:ui-monospace,Consolas,monospace}.step small{display:block;color:var(--m)}
.step.konec{border-color:var(--ok)}.step.tece,.step.pise{border-color:var(--run)}
.step.tece,.step.pise{animation:p 1.4s ease-in-out infinite}@keyframes p{50%{box-shadow:0 0 0 4px color-mix(in srgb,var(--run) 25%,transparent)}}
@media(prefers-reduced-motion:reduce){.step{animation:none!important}}
.tag{float:right;font-size:.75rem;color:var(--m)}.arrow{text-align:center;color:var(--m)}
table{width:100%;border-collapse:collapse;font-size:.85rem}td{padding:4px 6px;border-bottom:1px solid var(--l);vertical-align:top}
td:first-child{color:var(--m);white-space:nowrap}code{font-family:ui-monospace,Consolas,monospace}
</style>
<main><h1>Nadzor razpisa: <span id=r></span></h1>
<div class=card><h2>Potek</h2><div class=flow id=flow></div></div>
<div class=card><h2>Zadnje spremenjene datoteke</h2><table id=files></table></div>
<div class=card><h2>Dogajanje agentov (zapis seje, približno)</h2><table id=ev></table></div></main>
<script>
const L={konec:"končano",tece:"v teku",pise:"piše",caka:"čaka"};
const el=(id)=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
const box=s=>`<div class="step ${s.stanje}"><span class=tag>${L[s.stanje]}</span><b>${esc(s.naziv)}</b><small>${esc(s.opis)}${s.velikost?" · "+(s.velikost/1024).toFixed(1)+" KB":""}</small></div>`;
async function tick(){try{const d=await (await fetch("/api/status")).json();const S=Object.fromEntries(d.koraki.map(s=>[s.id,s]));
el("r").textContent=d.razpis||"(ni imena)";
el("flow").innerHTML=box(S.k0)+'<div class=arrow>↓</div>'+box(S.analitik)+'<div class=arrow>↓</div><div class=row>'+box(S.pisec)+box(S.kalkulant)+'</div><div class=arrow>↓</div>'+box(S.pregled);
el("files").innerHTML=d.datoteke.map(f=>`<tr><td>pred ${f.pred} s</td><td><code>${esc(f.pot)}</code></td></tr>`).join("")||"<tr><td>Ni datotek.</td></tr>";
el("ev").innerHTML=d.dogodki.map(e=>`<tr><td>${esc(e.cas)}</td><td>${esc(e.kdo)}</td><td>${esc(e.kaj)}</td></tr>`).join("")||"<tr><td>Ni zapisa seje.</td></tr>";
}catch(e){}}
tick();setInterval(tick,2000);
</script></html>"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/status"):
            now = time.time()
            body = json.dumps({"razpis": RAZPIS, "koraki": steps(now), "datoteke": recent_files(now),
                               "dogodki": transcript_events()}, ensure_ascii=False).encode("utf-8")
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
