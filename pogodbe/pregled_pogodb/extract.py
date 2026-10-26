"""Izluščanje podatkov iz besedila pogodbe (lokalno, na podlagi pravil).

Vsaka najdena vrednost ima svoj "dokaz" (odlomek besedila), da jo uporabnik lahko
preveri, ter oceno zanesljivosti (visoka / srednja / nizka).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional

MESECI = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "maj": 5, "may": 5, "jun": 6, "jul": 7,
    "avg": 8, "aug": 8, "sep": 9, "okt": 10, "oct": 10, "nov": 11, "dec": 12,
}
_MES_RE = (
    r"januar\w*|februar\w*|marc\w*|marec|april\w*|maj\w*|junij\w*|julij\w*|avgust\w*|"
    r"septembr\w*|september|oktobr\w*|oktober|novembr\w*|november|decembr\w*|december|"
    r"january|february|march|may|june|july|august"
)
D_NUM = re.compile(r"(?<!\d)(\d{1,2})\s*[.\-/]\s*(\d{1,2})\s*[.\-/]\s*(\d{4})(?!\d)")
D_ISO = re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")
D_TXT = re.compile(rf"(?<!\d)(\d{{1,2}})\s*\.?\s*({_MES_RE})\s*,?\s*(\d{{4}})", re.I)
D_EN = re.compile(rf"({_MES_RE})\s+(\d{{1,2}})(?:st|nd|rd|th)?\s*,\s*(\d{{4}})", re.I)

STEVILKE = {
    "en": 1, "ena": 1, "eno": 1, "ene": 1, "enega": 1, "dve": 2, "dva": 2, "dveh": 2, "tri": 3,
    "treh": 3, "štiri": 4, "štirih": 4, "pet": 5, "petih": 5, "šest": 6, "šestih": 6,
    "sedem": 7, "osem": 8, "devet": 9, "deset": 10, "dvanajst": 12, "one": 1, "two": 2,
    "three": 3, "four": 4, "five": 5, "six": 6, "twelve": 12,
}
_NUM_RE = r"\d+|" + "|".join(sorted(STEVILKE, key=len, reverse=True))
_UNIT_RE = r"let\w*|leto|mesec\w*|dni|dneh|dan|dneva|teden|tednov|tedn\w*|years?|months?|days?|weeks?"


def _unit(u: str) -> str:
    u = u.lower()
    if u.startswith(("let", "year")):
        return "let"
    if u.startswith(("mesec", "month")):
        return "mesecev"
    if u.startswith(("ted", "week")):
        return "tednov"
    return "dni"


def _num(tok: str) -> int:
    tok = tok.lower()
    return int(tok) if tok.isdigit() else STEVILKE.get(tok, 0)


def add_months(d: date, months: int) -> date:
    m = d.month - 1 + months
    y, m = d.year + m // 12, m % 12 + 1
    dim = [31, 29 if (y % 4 == 0 and (y % 100 or y % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return date(y, m, min(d.day, dim))


def add_duration(start: date, n: int, unit: str) -> date:
    """Konec obdobja (zadnji dan), npr. 1. 1. 2024 + 1 leto = 31. 12. 2024."""
    if unit == "let":
        end = add_months(start, 12 * n)
    elif unit == "mesecev":
        end = add_months(start, n)
    elif unit == "tednov":
        end = start + timedelta(weeks=n)
    else:
        end = start + timedelta(days=n)
    return end - timedelta(days=1)


def find_dates(text: str) -> list[tuple[int, int, date]]:
    out: list[tuple[int, int, date]] = []
    taken: list[tuple[int, int]] = []

    def add(m, y, mo, d):
        if any(not (m.end() <= a or m.start() >= b) for a, b in taken):
            return
        try:
            out.append((m.start(), m.end(), date(int(y), int(mo), int(d))))
            taken.append((m.start(), m.end()))
        except ValueError:
            pass

    for m in D_ISO.finditer(text):
        add(m, m[1], m[2], m[3])
    for m in D_TXT.finditer(text):
        add(m, m[3], MESECI.get(m[2][:3].lower(), 0), m[1])
    for m in D_EN.finditer(text):
        add(m, m[3], MESECI.get(m[1][:3].lower(), 0), m[2])
    for m in D_NUM.finditer(text):
        add(m, m[3], m[2], m[1])
    out = [x for x in out if 1990 <= x[2].year <= 2100]
    return sorted(out)


def parse_amount(s: str) -> Optional[float]:
    s = s.replace(" ", "").replace(" ", "")
    if not s:
        return None
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".") if re.search(r",\d{1,2}$", s) else s.replace(",", "")
    elif "." in s and re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


@dataclass
class Evidence:
    text: str
    confidence: str = "srednja"  # visoka / srednja / nizka


@dataclass
class Party:
    name: str
    role: str = ""
    reg_no: str = ""
    vat_id: str = ""


@dataclass
class Article:
    num: int
    title: str
    body: str
    kind: str = "člen"  # uvod / člen / priloga


@dataclass
class Extracted:
    title: str = ""
    number: str = ""
    doc_type: str = ""
    parties: list[Party] = field(default_factory=list)
    sign_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    indefinite: bool = False
    auto_renew: bool = False
    notice_period: str = ""
    duration: str = ""
    value: Optional[float] = None
    currency: str = ""
    value_period: str = ""  # "", mesečno, letno
    vat_note: str = ""
    payment_term_days: Optional[int] = None
    subject: str = ""
    articles: list[Article] = field(default_factory=list)
    all_amounts: list[tuple[float, str]] = field(default_factory=list)
    evidence: dict[str, Evidence] = field(default_factory=dict)


def norm(text: str) -> str:
    """Besedilo v eni vrstici (za regexe, ki prečkajo prelome vrstic)."""
    return re.sub(r"\s+", " ", text.replace(" ", " ")).strip()


def _ctx(t: str, a: int, b: int, pad: int = 70) -> str:
    return "…" + t[max(0, a - pad):min(len(t), b + pad)].strip() + "…"


# --------------------------------------------------------------------- vrsta, naslov
_TYPES = [
    (r"aneks|annex|dodatek\s+št|amendment", "Aneks"),
    (r"zaupnost|nda|non-?disclosure|confidential", "Pogodba o zaupnosti (NDA)"),
    (r"prevaj|prevod|lokalizacij|lektor|translation", "Prevajalske storitve"),
    (r"licenc|licence", "Licenčna"),
    (r"najem|najemn|lease|rent", "Najemna"),
    (r"vzdrževan|servis|maintenance|support", "Vzdrževalna / podpora"),
    (r"kupoprodaj|dobav|nakup|prodaj|supply|sale", "Dobava / kupoprodaja"),
    (r"podjemn", "Podjemna"),
    (r"zaposlitv|o delu|employment", "Delovna"),
    (r"sodelovanj|partner|cooperation", "Sodelovanje"),
    (r"storit|svetovanj|izvajanj|service|consult", "Storitvena"),
    (r"okvirn|framework", "Okvirna"),
]


def detect_title(lines: list[str]) -> str:
    head = [l.strip() for l in lines[:60] if l.strip()]
    pat = re.compile(r"^(pogodba|aneks|dogovor|sporazum|annex|agreement|contract|dodatek)\b", re.I)
    for i, l in enumerate(head):
        if pat.match(l) and len(l) < 140:
            nxt = head[i + 1] if i + 1 < len(head) else ""
            # naslov se včasih razteza čez dve vrstici ("POGODBA\no sodelovanju")
            if len(l.split()) <= 2 and nxt and len(nxt) < 80 and re.match(r"^(o|za|na)\b", nxt, re.I):
                return f"{l} {nxt}"
            return l
    return ""


def detect_type(title: str, text: str) -> str:
    probe = (title or text[:400]).lower()
    for pat, name in _TYPES:
        if re.search(pat, probe):
            return name
    return ""


def detect_number(text: str) -> str:
    head = text[:1500]
    m = re.search(
        r"(?:številka|štev\.|št\.|ref\.?\s*št\.?|no\.|ref\.?|contract\s+no\.?)\s*(?:pogodbe)?\s*[:.]?\s*"
        r"([A-Z0-9][A-Za-z0-9\-_/.]{2,30})", head, re.I)
    if m:
        val = m[1].rstrip(".")
        if re.search(r"\d", val):
            return val
    return ""


# --------------------------------------------------------------------- stranke
_LEGAL = (r"d\.\s?o\.\s?o\.|d\.\s?d\.|d\.\s?n\.\s?o\.|k\.\s?d\.|s\.\s?p\.|GmbH|Ltd\.?|Limited|Inc\.?|"
          r"LLC|AG|S\.A\.|B\.V\.|SE|zavod|z\.o\.o\.")
_NAME = re.compile(
    rf"((?:[A-ZČŠŽĐ0-9][\w&.\-'’]*\s+){{0,6}}?[A-ZČŠŽĐ][\w&.\-'’]*)\s*,?\s*({_LEGAL})(?![\w])")
_STOP = {
    "pogodba", "o", "med", "in", "ter", "between", "and", "naročnik", "izvajalec", "kupec",
    "prodajalec", "podjetje", "družba", "stranki", "stranka", "pogodbeni", "sklenjena", "sklenili",
    "sklepata", "aneks", "k", "za",
}


def detect_parties(text: str) -> list[Party]:
    t = norm(text[:6000])
    parties: list[Party] = []
    spans: list[int] = []
    starts: list[int] = []
    for m in _NAME.finditer(t):
        toks = m[1].split()
        low = [x.lower().strip(":,.") for x in toks]
        cut = max((i for i, w in enumerate(low) if w in _STOP), default=-1)
        toks = toks[cut + 1:] or toks
        name = f"{' '.join(toks)} {m[2]}".strip()
        if any(p.name.lower() == name.lower() for p in parties):
            continue
        parties.append(Party(name=name))
        spans.append(m.end())
        starts.append(m.start())
    for i, p in enumerate(parties):
        end = starts[i + 1] if i + 1 < len(parties) else spans[i] + 600
        seg = t[spans[i]:end]
        r = re.search(r"v\s+nadaljevanju[:\s]*[„\"“'»]?\s*([A-Za-zČŠŽčšžĆć]{3,25})", seg, re.I)
        if r:
            p.role = r[1].strip().capitalize()
        r = re.search(r"matičn\w*\s*št\w*\.?\s*:?\s*(\d{7,10})", seg, re.I)
        if r:
            p.reg_no = r[1]
        r = re.search(r"(?:ID\s*(?:št\.?)?\s*za\s*DDV|davčn\w*\s*št\w*|VAT)\.?\s*:?\s*(?:SI)?\s*(\d{8})", seg, re.I)
        if r:
            p.vat_id = "SI" + r[1]
    return parties[:6]


# --------------------------------------------------------------------- veljavnost
_START_PRE = re.compile(
    r"(začne\s+veljati|prične\s+veljati|stopi\s+v\s+veljavo|velja\s+od|veljavna?\s+od|začetek\s+veljavnosti|"
    r"z\s+dnem|effective|commenc\w+|valid\s+from|from|od)\s*(?:dne\s*)?$", re.I)
_END_PRE = re.compile(
    r"(velja|veljav\w*|traja|trajanje|valid|until|expir\w*|konča|poteče|do\s+dne|do\s+vključno)"
    r"[^.;]{0,70}?\b(do|until|to|dne)\s*(?:vključno\s*)?(?:dne\s*)?$", re.I)
_SIGN_PRE = re.compile(r"(dne|datum\w*[^.\n]{0,20}:?|dated?|sklenjena\s+dne|v\s+\w+,\s*dne|on)\s*:?\s*$", re.I)
_NOTICE = re.compile(
    rf"(?:odpovedn\w*\s+rok\w*|odpov\w+|notice)[^.\d]{{0,80}}?({_NUM_RE})\s*(?:\(\s*\w+\s*\)\s*)?({_UNIT_RE})", re.I)
_DUR = re.compile(
    rf"(?:za\s+(?:dobo|obdobje|čas)|v\s+trajanju|traja|trajanje|duration|term\s+of|for\s+a\s+(?:period|term)\s+of)"
    rf"[^.\d]{{0,30}}?({_NUM_RE})\s*(?:\(\s*\w+\s*\)\s*)?({_UNIT_RE})", re.I)
_INDEF = re.compile(r"nedoločen\w*\s+(?:čas|obdobj)|indefinite|unlimited\s+term|until\s+terminated|do\s+preklica", re.I)
_RENEW = re.compile(
    r"(?:samodejn\w*|avtomatsk\w*|tiho\w*)\s+(?:se\s+)?(?:podaljš\w*|obnov\w*)|podaljša\s+se\s+(?:za\s+)?(?:vsakokrat|samodejno|avtomatsko)|"
    r"automatic\w*\s+(?:ly\s+)?renew|auto-?renew|renew\w*\s+automatically|prolong\w*", re.I)
_FROM_SIGN = re.compile(
    r"(?:z\s+dnem|od\s+dneva|od\s+dne|ob)\s+(?:podpisa|sklenitve)|date\s+of\s+(?:signature|signing)", re.I)


def detect_validity(ex: Extracted, text: str) -> None:
    t = norm(text)
    dates = find_dates(t)
    roles: dict[int, str] = {}

    # območje "od X do Y"
    for i in range(len(dates) - 1):
        a, b = dates[i], dates[i + 1]
        between = t[a[1]:b[0]]
        if re.fullmatch(r"\s*(?:do|to|until|–|-|—)\s*(?:vključno\s*)?(?:dne\s*)?", between, re.I) and \
                re.search(r"(od|from|veljav\w*|velja|traja)\s*(?:dne\s*)?$", t[max(0, a[0] - 40):a[0]], re.I):
            ex.start_date, ex.end_date = a[2], b[2]
            roles[i], roles[i + 1] = "start", "end"
            ex.evidence["start_date"] = Evidence(_ctx(t, a[0], b[1]), "visoka")
            ex.evidence["end_date"] = Evidence(_ctx(t, a[0], b[1]), "visoka")
            break

    for i, (s, e, d) in enumerate(dates):
        if i in roles:
            continue
        pre = t[max(0, s - 90):s]
        if ex.end_date is None and _END_PRE.search(pre):
            ex.end_date, roles[i] = d, "end"
            ex.evidence["end_date"] = Evidence(_ctx(t, s, e), "visoka")
        elif ex.start_date is None and _START_PRE.search(pre[-70:]):
            ex.start_date, roles[i] = d, "start"
            ex.evidence["start_date"] = Evidence(_ctx(t, s, e), "srednja")

    for i, (s, e, d) in enumerate(dates):
        if i not in roles and _SIGN_PRE.search(t[max(0, s - 60):s]):
            ex.sign_date = d
            roles[i] = "sign"
            ex.evidence["sign_date"] = Evidence(_ctx(t, s, e), "srednja")
            break
    if ex.sign_date is None:
        for i, (s, e, d) in enumerate(dates):
            if i not in roles and s < 2500:
                ex.sign_date = d
                ex.evidence["sign_date"] = Evidence(_ctx(t, s, e), "nizka")
                break
    if ex.sign_date is None and dates:
        s, e, d = dates[-1]
        ex.sign_date = d
        ex.evidence["sign_date"] = Evidence(_ctx(t, s, e), "nizka")

    if ex.start_date is None and ex.sign_date and (m := _FROM_SIGN.search(t)):
        ex.start_date = ex.sign_date
        ex.evidence["start_date"] = Evidence(_ctx(t, m.start(), m.end()) + " (izpeljano iz datuma podpisa)", "nizka")

    if m := _DUR.search(t):
        n, unit = _num(m[1]), _unit(m[2])
        if n:
            ex.duration = f"{n} {unit}"
            ex.evidence["duration"] = Evidence(_ctx(t, m.start(), m.end()), "srednja")
            if ex.end_date is None and ex.start_date:
                ex.end_date = add_duration(ex.start_date, n, unit)
                ex.evidence["end_date"] = Evidence(
                    f"Izračunano: začetek + {n} {unit}. {_ctx(t, m.start(), m.end())}", "srednja")

    if m := _INDEF.search(t):
        if ex.end_date is None:
            ex.indefinite = True
            ex.evidence["indefinite"] = Evidence(_ctx(t, m.start(), m.end()), "srednja")
    if m := _RENEW.search(t):
        ex.auto_renew = True
        ex.evidence["auto_renew"] = Evidence(_ctx(t, m.start(), m.end()), "srednja")
    if m := _NOTICE.search(t):
        n = _num(m[1])
        if n:
            ex.notice_period = f"{n} {_unit(m[2])}"
            ex.evidence["notice_period"] = Evidence(_ctx(t, m.start(), m.end()), "srednja")


# --------------------------------------------------------------------- vrednost
_AMT = r"(?<![\d.,])(\d{1,3}(?:[.  ]\d{3})+(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?)"
_CUR = r"(EUR|€|evrov|evra|evri|evro|USD|\$|GBP|£|CHF)"
_AMT_RE = re.compile(rf"{_AMT}\s*{_CUR}(?![A-Za-z])|{_CUR}\s*{_AMT}", re.I)
_STRONG = re.compile(
    r"skupn\w*\s+(?:pogodben\w*\s+)?(?:vrednost|cena)|vrednost\s+(?:te\s+)?pogodbe|pogodben\w*\s+(?:vrednost|cena)|"
    r"celotn\w*\s+(?:vrednost|cena)|total\s+(?:contract\s+)?(?:value|price|amount)|contract\s+(?:value|price)", re.I)
_WEAK = re.compile(r"vrednost|cena|znaša|znesek|plačil|nadomestil|price|fee|amount|najemnin|honorar", re.I)
_NEG = re.compile(r"kazen|penal|obresti|odškodnin|garancij|jamstv|zavarovan|depozit|varščin|zamudn|penalty|damages", re.I)
_PAYTERM = re.compile(
    r"(?:plačilni\s+rok|rok\s+plačila|plačilo\s+(?:v|v\s+roku)|plačati\s+v\s+roku|payment\s+term|within)"
    r"[^.\d]{0,40}?(\d{1,3})\s*(?:\(\s*\w+\s*\)\s*)?(?:dni|dneh|dan|days)", re.I)


def _cur(c: str) -> str:
    c = c.lower()
    if c in ("€",) or c.startswith(("eur", "evr")):
        return "EUR"
    return {"$": "USD", "£": "GBP"}.get(c, c.upper())


def detect_value(ex: Extracted, text: str) -> None:
    t = norm(text)
    cands = []
    for m in _AMT_RE.finditer(t):
        raw = m[1] or m[4]
        cur = _cur(m[2] or m[3])
        val = parse_amount(raw)
        if val is None or val <= 0:
            continue
        before = t[max(0, m.start() - 160):m.start()]
        score = 0
        if _STRONG.search(before):
            score += 5
        if _WEAK.search(before[-90:]):
            score += 3
        if _NEG.search(before[-100:]):
            score -= 6
        cands.append((score, -m.start(), val, cur, m))
        ex.all_amounts.append((val, cur))
    if not cands:
        return
    good = [c for c in cands if c[0] >= 3]
    if good:
        score, _, val, cur, m = max(good, key=lambda c: (c[0], c[1]))
        conf = "visoka" if score >= 5 else "srednja"
    else:
        score, _, val, cur, m = max(cands, key=lambda c: c[2])
        conf = "nizka"
    ex.value, ex.currency = val, cur
    after = t[m.end():m.end() + 70].lower()
    around = (t[max(0, m.start() - 60):m.start()] + " " + after).lower()
    if re.search(r"brez\s+ddv|\+\s*ddv|neto|excl\w*\s+vat|plus\s+vat", around):
        ex.vat_note = "brez DDV"
    elif re.search(r"z\s+ddv|vključno\s+z\s+ddv|bruto|incl\w*\s+vat", around):
        ex.vat_note = "z DDV"
    if re.search(r"mesečn|na\s+mesec|/\s*mesec|per\s+month|monthly", around):
        ex.value_period = "mesečno"
    elif re.search(r"letn|na\s+leto|/\s*leto|per\s+year|annual", around):
        ex.value_period = "letno"
    ex.evidence["value"] = Evidence(_ctx(t, m.start(), m.end()), conf)
    if pm := _PAYTERM.search(t):
        ex.payment_term_days = int(pm[1])
        ex.evidence["payment_term_days"] = Evidence(_ctx(t, pm.start(), pm.end()), "srednja")


# --------------------------------------------------------------------- struktura
_ART_PATTERNS = [
    ("člen", re.compile(r"^\s*(\d{1,3})\s*\.?\s*(?:člen|čl\.|ČLEN)\b[.:\-–]?\s*(.*)$")),
    ("člen", re.compile(r"^\s*(?:člen|čl\.|ČLEN)\s*(\d{1,3})\b\.?[:\-–]?\s*(.*)$", re.I)),
    ("člen", re.compile(r"^\s*(?:article|section|clause)\s+(\d{1,3})\b[.:\-–]?\s*(.*)$", re.I)),
    ("člen", re.compile(r"^\s*§\s*(\d{1,3})\.?\s*(.*)$")),
    ("člen", re.compile(r"^\s*(\d{1,2})\.\s+([A-ZČŠŽ][A-ZČŠŽ0-9 ,.\-/]{3,70})$")),
    ("člen", re.compile(r"^\s*(\d{1,2})\.\s+([A-ZČŠŽ][^\n.]{2,70})$")),
]
_ANNEX = re.compile(r"^\s*(priloga|aneks|annex|appendix|příloha)\s*(?:št\.?)?\s*([0-9A-Z]{0,3})\b[.:\-–]?\s*(.*)$", re.I)


def _sequence(hits: list[tuple[int, int, str]]) -> list[tuple[int, int, str]]:
    out, prev = [], 0
    for idx, num, rest in hits:
        if prev < num <= prev + 3 or (not out and num <= 3):
            out.append((idx, num, rest))
            prev = num
    return out


def _clean_title(s: str) -> str:
    return re.sub(r"^[\s(\[„\"“\-–:]+|[\s)\]”\"“.:]+$", "", s).strip()


def parse_articles(text: str) -> list[Article]:
    lines = text.replace("\f", "\n").split("\n")
    best: list[tuple[int, int, str]] = []
    for _, pat in _ART_PATTERNS:
        hits = []
        for i, l in enumerate(lines):
            m = pat.match(l)
            if m:
                hits.append((i, int(m[1]), (m[2] or "").strip()))
        seq = _sequence(hits)
        if len(seq) > len(best) and len(seq) >= 2:
            best = seq
            if len(seq) >= 3:
                break
    arts: list[Article] = []
    first = best[0][0] if best else len(lines)
    intro = "\n".join(lines[:first]).strip()
    if intro:
        arts.append(Article(0, "Uvod (stranke)", intro, "uvod"))
    annex_at = len(lines)
    for i in range(best[-1][0] + 1 if best else 0, len(lines)):
        if _ANNEX.match(lines[i]) and not lines[i].strip().lower().startswith("aneks k"):
            annex_at = i
            break
    for k, (idx, num, rest) in enumerate(best):
        end = best[k + 1][0] if k + 1 < len(best) else annex_at
        body_start = idx + 1
        title = _clean_title(rest)
        if not title:
            j = idx + 1
            while j < end and not lines[j].strip():
                j += 1
            if j < end:
                cand = lines[j].strip()
                words = len(cand.split())
                if len(cand) <= 80 and words <= 9 and not cand.endswith((".", ";", ",")) or \
                        (cand.startswith("(") and cand.endswith(")")):
                    title = _clean_title(cand)
                    body_start = j + 1
        arts.append(Article(num, title, "\n".join(lines[body_start:end]).strip()))
    # priloge
    j = annex_at
    n = 0
    while j < len(lines):
        m = _ANNEX.match(lines[j])
        if m:
            k = j + 1
            while k < len(lines) and not _ANNEX.match(lines[k]):
                k += 1
            n += 1
            label = f"{m[1].capitalize()} {m[2]}".strip()
            arts.append(Article(n, f"{label} {_clean_title(m[3])}".strip(), "\n".join(lines[j + 1:k]).strip(), "priloga"))
            j = k
        else:
            j += 1
    if not best and text.strip():
        arts = [Article(0, "Celotno besedilo", text.strip(), "uvod")]
    return arts


# --------------------------------------------------------------------- vse skupaj
def extract(text: str) -> Extracted:
    ex = Extracted()
    lines = text.replace("\f", "\n").split("\n")
    ex.title = detect_title(lines)
    ex.doc_type = detect_type(ex.title, text)
    ex.number = detect_number(text)
    ex.parties = detect_parties(text)
    detect_validity(ex, text)
    detect_value(ex, text)
    ex.articles = parse_articles(text)
    for a in ex.articles:
        if re.search(r"predmet|subject|scope", a.title, re.I) and a.body:
            ex.subject = norm(a.body)[:400]
            break
    return ex


def status_of(end: Optional[date], indefinite: bool, today: Optional[date] = None, warn_days: int = 90) -> str:
    today = today or date.today()
    if end:
        if end < today:
            return "Pretečena"
        if (end - today).days <= warn_days:
            return "Poteče kmalu"
        return "Veljavna"
    return "Nedoločen čas" if indefinite else "Neznano"
