from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.33), Inches(7.5)
DARK, ACC, GREY = RGBColor(0x22, 0x2B, 0x3A), RGBColor(0xC8, 0x55, 0x2D), RGBColor(0x66, 0x66, 0x66)

def bullets(title, items, note=None):
    s = prs.slides.add_slide(prs.slide_layouts[5])
    s.shapes.title.text = title
    s.shapes.title.text_frame.paragraphs[0].font.size = Pt(32)
    s.shapes.title.text_frame.paragraphs[0].font.color.rgb = DARK
    tb = s.shapes.add_textbox(Inches(0.7), Inches(1.6), Inches(12), Inches(5))
    tf = tb.text_frame; tf.word_wrap = True
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = "• " + it; p.font.size = Pt(20); p.space_after = Pt(10)
    if note:
        n = s.shapes.add_textbox(Inches(0.7), Inches(6.7), Inches(12), Inches(0.5))
        n.text_frame.text = note; n.text_frame.paragraphs[0].font.size = Pt(12)
        n.text_frame.paragraphs[0].font.color.rgb = GREY
    return s

def table(title, rows, widths):
    s = prs.slides.add_slide(prs.slide_layouts[5])
    s.shapes.title.text = title
    s.shapes.title.text_frame.paragraphs[0].font.size = Pt(28)
    s.shapes.title.text_frame.paragraphs[0].font.color.rgb = DARK
    t = s.shapes.add_table(len(rows), 3, Inches(0.5), Inches(1.5), Inches(12.3), Inches(5)).table
    for j, w in enumerate(widths): t.columns[j].width = Inches(w)
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            c = t.cell(i, j); c.text = v
            for p in c.text_frame.paragraphs:
                p.font.size = Pt(14 if i else 15); p.font.bold = (i == 0)


s = prs.slides.add_slide(prs.slide_layouts[0])
s.shapes.title.text = "Analiza konkurence v EU"
s.placeholders[1].text = "AMIDAS d.o.o. · faza 2 (EU) · segment: mednarodne stranke v slovenščini"

bullets("Obseg in omejitve", [
    "Cilj: kdo v EU konkurira AMIDAS (slovenščina, EU institucije, mednarodne stranke) in kako se razlikuje od domačih konkurentov.",
    "Viri: lastne spletne strani, Nimdzi 100 (povzetki), javna naročila TED; finančni podatki za EU podjetja so redki in iz različnih let.",
    "Nismo pridobili: Nimdzi lestvice po imenih (plačljivo/blokirano), TED obvestila (odgovor prazen), Summa Linguae (blokiran dostop).",
    "Vse številke iz virov so označene z letom; neprimerljivih ne primerjamo neposredno.",
], "Prvi osnutek – za odločitev, katera EU podjetja poglobiti.")

bullets("EU trg: kontekst", [
    "Nimdzi 100 (2025, prihodki 2024): 42 od 100 največjih ponudnikov ima sedež v Evropi, 34 v Severni Ameriki.",
    "Rast med največjimi: Azija 7,2 %, Severna Amerika 6,0 %, Evropa le 0,7 %.",
    "Top 100 skupaj predstavlja ≈19,8 % celotne industrije – trg je razdrobljen tudi na ravni EU.",
    "Največji: TransPerfect (1,23 mrd. $ v 2024), LanguageLine (nad 1 mrd. $) – oba nista evropska.",
], "Vir: multilingual.com – povzetek Nimdzi 100 (2025).")

table("EU konkurenti: prvi pregled", [
    ["Podjetje", "Kar je potrjeno", "Za preveriti"],
    ["Translated (Italija)", "200+ jezikov; AI-first prevajanje s človeško revizijo (Lara AI), API-ji; 74,1 mio. $ prihodkov 2025 (predhodni Nimdzi 2026)", "Slovenščina, cene, slovenski naročniki"],
    ["Acolad (Francija)", "Po lastni spletni strani »del RWS«; AI-lokalizacija, tolmačenje, samopostrežno AI prevajanje (24 €/mesec); 333,3 mio. $ v 2022 (Nimdzi 2023)", "Trenutna velikost po prevzemu, slovenski tim"],
    ["RWS / SDL", "SDL d.o.o. Ljubljana: 1,26 mio. €, 16,3 zaposlenih, bonit. ocena 10 (ebonitete, 2025) – globalna mreža z lokalno prisotnostjo", "Ali je SDL d.o.o. neposredno prevajalska agencija ali tehnološki ponudnik"],
    ["Skrivanek (Češka)", "30+ let; ISO 13485 (medicina); lokalizacija SaaS in fintech; slovenščina prek poljske enote", "Slovenska prisotnost, certifikati ISO 17100"],
    ["Summa Linguae (Poljska)", "Nimdzi: ≈30–33 mio. $ (2022, različni viri)", "Spletna stran nedostopna; slovenščina"],
    ["Ciklopea (Hrvaška)", "Podružnica v Ljubljani od 2018; ISO 17100, 18587, 9001, 13485, 27001 (lastna navedba)", "Slovenska pravna oseba, velikost"],
], [2.6, 6.6, 3.1])

bullets("Javna naročila EU: kaj smo našli", [
    "Evropski parlament in Komisija (DGT) oddajata okvirne pogodbe po lotih (jezikovne kombinacije); okvirna pogodba TM11/SL (2011) je pokrivala prevode v slovenščino – zastarelo.",
    "V iskanju se je pojavilo obvestilo TED iz 2026, kjer je med zmagovalci okvirnega sporazuma omenjena Prevajalska agencija GORR (največ ≈4.350,94 €). NI preverjeno (obvestilo se ni naložilo), institucija in jezik neznana.",
    "Za AMIDAS (naročniki: država, ustanove) je to ključna smer faze 2: ugotoviti, kdo ima slovenske lote (npr. TRA/EU19) in kakšne so vrednosti.",
], "Vir: TED / Publications Office (povzetki iskanja). Za preverjanje je potreben dostop do ted.europa.eu.")

bullets("Opažanja (hipoteze)", [
    "AI-first postaja standard: Translated (Lara), Acolad (Lia, samopostrežna ponudba), IOLAR (AI/podatki). AMIDAS ima Amidas MT – priložnost za jasnejše pozicioniranje (varnost, post-editing).",
    "Certifikati: Skrivanek in Ciklopea imata ISO 13485 (medicina); Ciklopea in Julija tudi ISO 18587. AMIDAS ima ISO 17100 in 9001.",
    "Cenovni signal: Acolad javno objavlja samopostrežno ceno (24 €/mesec) – pritisk na enostavna besedila.",
    "Konsolidacija: Acolad je po lastnih navedbah del RWS; SDL v Ljubljani kaže, da globalni igralci držijo lokalne enote.",
], "Opažanja iz lastnih strani in povzetkov; niso ocena kakovosti.")

bullets("Izbran segment: mednarodne stranke v slovenščini", [
    "Kdo išče: tuja podjetja, ki potrebujejo prevode v slovenščino (EN→SL) ali iz nje (SL→EN, SL→druge), vključno z lokalizacijo in tolmačenjem.",
    "Konkurenčni sloji: (1) mednarodne agencije in mreže, (2) slovenske agencije z izvozom, (3) neodvisni prevajalci (ProZ), (4) AI-samopostrežne rešitve.",
    "Mednarodne agencije slovenščino pogosto oddajo naprej partnerjem – lokalna agencija z naravnimi govorci je zanje tudi potencialni partner, ne le konkurent.",
    "AMIDAS ima po lastnih navedbah ISO 17100 in 9001, mrežo 300+ prevajalcev, vse tri vrste tolmačenja in angleško različico spletne strani.",
], "Zadnja trditev je iz navedb na amidas.si; mednarodno delitev dela (partnerstva) je hipoteza za preverjanje.")

table("Cene za slovenščino: kaj je javno", [
    ["Vir", "Cena", "Opombe"],
    ["Alphatrad (Francija, mreža 80+ agencij)", "»od 0,04 € na besedo«", "Marketinška spodnja meja (»od«), obseg in pogoji niso navedeni"],
    ["Fasttranslator (VB)", "od 0,084 £/besedo; certificirani prevod od 0,099 £", "10.000 besed, dostava 38 ur; podatek iz povzetka iskanja"],
    ["Julija (Slovenija)", "0,064 € (osnovni) / 0,078 € (premium) na besedo", "Jezikovni par ni naveden; DDV ni naveden"],
    ["Neodvisni prevajalci (ProZ)", "0,06–0,10 € na besedo; specialisti do 0,15 €", "EN→SL, posamezni profili, ne agencije"],
    ["Acolad (AI samopostrežno)", "24 €/mesec", "AI prevod, ni neposredno primerljivo s človeškim"],
], [3.6, 3.8, 4.9])

table("Ponudba za slovenščino pri mednarodnih agencijah", [
    ["Podjetje", "Kar navajajo", "Za preveriti"],
    ["Skrivanek (PL/CZ)", "Posebna stran za slovenščino; prevodi v slovenščino in iz slovenščine v poljščino; ponudba v 30 minutah; 100+ drugih jezikov", "Ali imajo slovenske prevajalce v hiši"],
    ["Alphatrad (FR)", "Slovenščina s prevajalci naravnimi govorci; spletna ponudba; mreža agencij po Evropi", "Kdo dejansko prevaja (partnerji)"],
    ["Baltic Media (Severna Evropa)", "ISO 9001:2015; 30 let; stran »Slovenian Translation Services« z omembo cene na besedo", "Konkretna cena, ISO 17100"],
    ["Translinguo Global (Španija)", "Slovenščina↔španščina, francoščina, angleščina; navedene ISO certifikacije; 10+ let", "Katere ISO, velikost"],
    ["Translated (IT)", "200+ jezikov; AI-first z revizijo; takojšnja ponudba", "Lastna ponudba za slovenščino"],
], [3.0, 6.4, 2.9])

bullets("Opažanja za AMIDAS (hipoteze)", [
    "Cene: tuje spletne agencije in Julija objavljajo cene ali »od« cene; AMIDAS ne – za mednarodne stranke je hitra ponudba (v 30 minutah, spletni izračun) pogosto odločilna.",
    "Cenovni pas za slovenščino je približno 0,06–0,10 €/besedo (neodvisni prevajalci, Julija); »od 0,04 €« pri Alphatrad je spodnja meja.",
    "Diferenciacija: naravni govorci v obe smeri (SL→EN je jedro AMIDAS), tolmačenje, sodni prevodi, ISO 17100 – a so vidni samo v tekstu na strani.",
    "Priložnost: partnerstvo z mednarodnimi agencijami za slovenščino (white-label), kjer so cene pritisk navzdol, kakovost pa se prodaja prek zaupanja.",
], "Hipoteze iz javnih virov; cene niso neposredno primerljive (različni obsegi, valute, roki).")

bullets("Predlagani naslednji koraki", [
    "1. Mystery shopping EN→SL: isto besedilo (npr. 1.000 besed) pri Alphatrad, Skrivanek, Translated, Baltic Media in Juliji → cena, čas, ponudba.",
    "2. Preveriti, ali je angleška stran amidas.si/en dovolj za mednarodne stranke (cene, ISO, hitro povpraševanje).",
    "3. Ugotoviti, katere mednarodne agencije oddajajo slovenščino partnerjem, in pripraviti partnersko ponudbo.",
    "4. Finančni podatki izbranih EU agencij: Nimdzi 100 poročilo ali Orbis.",
    "5. Po odločitvi: poglobiti 3–5 podjetij po postopku iz faze 1.",
])

bullets("Viri", [
    "multilingual.com – Charting the Nimdzi 100 (2025)",
    "Nimdzi 100 povzetki (Acolad, Translated, Summa Linguae – prihodki po letih različni)",
    "Spletne strani: acolad.com, translated.com, skrivanek.com/skrivanek.pl, alphatrad.com, balticmedia.com, translinguoglobal.com, ciklopea.com, iolar.com, julija.si; fasttranslator.com in ProZ (povzetek iskanja)",
    "TED / Publications Office EU (povzetki iskanja); ebonitete.si (SDL d.o.o.)",
])
for sl in prs.slides:
    t = sl.shapes.title
    t.left, t.width = Inches(0.7), Inches(11.9)
    if sl.slide_layout != prs.slide_layouts[0]: t.top, t.height = Inches(0.4), Inches(1.0)
    else: t.height = Inches(1.2)
    for p in t.text_frame.paragraphs:
        p.alignment = 1
    if sl.placeholders and len(sl.placeholders) > 1 and sl.slide_layout == prs.slide_layouts[0]:
        sub = sl.placeholders[1]; sub.left, sub.width, sub.height = Inches(0.7), Inches(11.9), Inches(1.2)
        t.top = Inches(2.3); sub.top = Inches(3.9)
prs.save("analiza_konkurence_EU.pptx")
