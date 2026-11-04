"""Agentic AI sistem: analiza konkurence + PowerPoint predstavitev.

Arhitektura (iz infografike):
  Goal -> Planner -> Executor(+tools) -> Critic (Author-Critic / Reflection loop)
       -> Memory (SQLite) -> Human check -> Output (.pptx)
"""
import argparse, json, re, sqlite3, sys
from pptx import Presentation
from pptx.util import Pt

MODEL = "claude-sonnet-5-5"
MAX_RETRIES = 2                      # rules/limits: koliko krat Critic lahko vrne delo
WEB_SEARCH = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 4}]


# ---------- LLM (ena sama točka dostopa; lahko jo zamenjaš v testih) ----------
def llm(system: str, user: str, tools=None, max_tokens: int = 3000) -> str:
    from anthropic import Anthropic
    client = Anthropic()             # bere ANTHROPIC_API_KEY iz okolja
    resp = client.messages.create(
        model=MODEL, max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": user}],
        **({"tools": tools} if tools else {}),
    )
    return "".join(b.text for b in resp.content if b.type == "text")


def parse_json(text: str):
    m = re.search(r"(\{.*\}|\[.*\])", text, re.S)
    if not m:
        raise ValueError(f"Ni JSON-a v odgovoru:\n{text[:300]}")
    return json.loads(m.group(1))


# ---------- MEMORY (kratkoročni, SQLite) ----------
class Memory:
    def __init__(self, path="memory.db"):
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS findings(competitor TEXT, question TEXT, answer TEXT)")
        self.db.execute("CREATE TABLE IF NOT EXISTS prefs(note TEXT)")

    def save_finding(self, c, q, a):
        self.db.execute("INSERT INTO findings VALUES(?,?,?)", (c, q, a)); self.db.commit()

    def save_pref(self, note):
        self.db.execute("INSERT INTO prefs VALUES(?)", (note,)); self.db.commit()

    def prefs(self) -> str:
        return "\n".join(r[0] for r in self.db.execute("SELECT note FROM prefs")) or "(ni)"

    def findings(self) -> list[dict]:
        return [dict(competitor=c, question=q, answer=a)
                for c, q, a in self.db.execute("SELECT * FROM findings")]


# ---------- PLANNER ----------
def plan(goal: str, company: str, competitors: list[str], mem: Memory) -> list[dict]:
    out = llm(
        "Si Planner. Razbij cilj na konkretne raziskovalne naloge. Vrni SAMO JSON: "
        '[{"competitor": "...", "question": "..."}]. Za vsakega konkurenta 3 vprašanja: '
        "produkt in cene, pozicioniranje in ciljna publika, prednosti/slabosti.",
        f"Cilj: {goal}\nNaše podjetje: {company}\nKonkurenti: {competitors}\n"
        f"Preference uporabnika iz prejšnjih zagonov:\n{mem.prefs()}",
    )
    return parse_json(out)


# ---------- EXECUTOR + CRITIC (Author-Critic z reflection loop) ----------
def execute(task: dict, feedback: str = "") -> str:
    return llm(
        "Si Executor. Uporabi web_search in odgovori jedrnato (max 120 besed), "
        "z dejstvi in navedbo vira (URL). Ne si izmišljaj številk.",
        f"Konkurent: {task['competitor']}\nVprašanje: {task['question']}\n"
        + (f"Popravi glede na kritiko: {feedback}" if feedback else ""),
        tools=WEB_SEARCH,
    )


def critique(task: dict, answer: str) -> dict:
    out = llm(
        "Si Critic. Oceni odgovor: ali je konkreten, podprt z virom in odgovarja na vprašanje? "
        'Vrni SAMO JSON: {"ok": true/false, "issue": "kaj manjka"}',
        f"Vprašanje: {task['question']}\nOdgovor: {answer}",
    )
    return parse_json(out)


def run_task(task: dict, mem: Memory) -> str:
    feedback = ""
    for attempt in range(MAX_RETRIES + 1):
        answer = execute(task, feedback)
        verdict = critique(task, answer)
        print(f"  [{task['competitor']}] poskus {attempt+1}: {'OK' if verdict['ok'] else verdict['issue']}")
        if verdict["ok"]:
            break
        feedback = verdict["issue"]
    mem.save_finding(task["competitor"], task["question"], answer)
    return answer


# ---------- SYNTHESIZER -> slides ----------
def synthesize(company: str, mem: Memory, human_feedback: str = "") -> list[dict]:
    out = llm(
        "Si analitik. Iz ugotovitev sestavi 6-8 slide-ov. Vrni SAMO JSON: "
        '[{"title": "...", "bullets": ["...", "..."]}]. Zadnji slide: priporočila. '
        "Max 4 bullets na slide.",
        f"Naše podjetje: {company}\nUgotovitve: {json.dumps(mem.findings(), ensure_ascii=False)}\n"
        f"Preference: {mem.prefs()}\nPovratna informacija človeka: {human_feedback or '(ni)'}",
        max_tokens=4000,
    )
    return parse_json(out)


def build_pptx(slides: list[dict], path: str):
    prs = Presentation()
    for s in slides:
        slide = prs.slides.add_slide(prs.slide_layouts[1])   # Title + Content
        slide.shapes.title.text = s["title"]
        tf = slide.placeholders[1].text_frame
        tf.text = s["bullets"][0]
        for b in s["bullets"][1:]:
            tf.add_paragraph().text = b
        for p in tf.paragraphs:
            p.font.size = Pt(20)
    prs.save(path)


# ---------- ORKESTRATOR ----------
def main(argv=None, ask=input):
    ap = argparse.ArgumentParser()
    ap.add_argument("--company", required=True)
    ap.add_argument("--competitors", nargs="+", required=True)
    ap.add_argument("--goal", default="Pripravi analizo konkurence in predstavitev za ponedeljek.")
    ap.add_argument("--out", default="analiza_konkurence.pptx")
    ap.add_argument("--db", default="memory.db")
    a = ap.parse_args(argv)

    mem = Memory(a.db)
    print("1) Planner ...")
    tasks = plan(a.goal, a.company, a.competitors, mem)
    print(f"   {len(tasks)} nalog")

    print("2) Executor + Critic ...")
    for t in tasks:
        run_task(t, mem)

    print("3) Synthesizer ...")
    slides = synthesize(a.company, mem)

    while True:                                   # 4) HUMAN CHECK
        print("\n--- Osnutek ---")
        for i, s in enumerate(slides, 1):
            print(f"{i}. {s['title']}")
            for b in s["bullets"]:
                print(f"   - {b}")
        ans = ask("\nOdobri? [y = da / ali napiši popravek]: ").strip()
        if ans.lower() in ("y", "yes", "da"):
            break
        mem.save_pref(ans)                        # learning: naslednjič se spomni
        slides = synthesize(a.company, mem, ans)

    build_pptx(slides, a.out)
    print(f"\nShranjeno: {a.out}")


if __name__ == "__main__":
    main()
