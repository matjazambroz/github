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

# 1 naslov
s = prs.slides.add_slide(prs.slide_layouts[0])
s.shapes.title.text = "Analiza konkurence v Sloveniji"
s.placeholders[1].text = "AMIDAS d.o.o. · faza 1 (Slovenija) · osnutek na podlagi javnih virov"

bullets("Obseg in omejitve", [
    "Cilj: pregled slovenskih konkurentov AMIDAS in izhodišče za razširitev na EU (faza 2).",
    "Viri: javni spletni viri (poslovni register bizi.si, ELIA, Clutch, akademski članek, mediji).",
    "Česa NI: cene, prihodki, število zaposlenih in certifikati večine podjetij niso javno potrjeni.",
    "Vse, kar ni potrjeno, je na diapozitivih označeno z »za preveriti«. Številk nismo ugibali.",
], "Raziskava je narejena z javnim spletnim iskanjem; strani amidas.si, clutch.co in milengo.com niso bile dostopne.")

bullets("Slovenski trg prevajalskih storitev", [
    "Prva prevajalska podjetja so nastala 1990–1991; po vstopu v EU (2004) se je število podjetij močno povečalo.",
    "Trg je razdrobljen: v raziskavi iz 2008 je imelo 8 od 10 najuspešnejših podjetij le 4–17 zaposlenih.",
    "Mednarodni igralci z lokalnimi podružnicami (Star, Skrivanek) so bili takrat med prvimi desetimi po tržnem deležu.",
    "Podatek je star 17 let (Fišer, JoSTrans 2008) – nujno ga je osvežiti z AJPES-om.",
], "Vir: Fišer, »Recent trends in the translation industry in Slovenia«, JoSTrans.")

bullets("Izhodišče: AMIDAS", [
    "Sedež v Ljubljani, ustanovljen 1991; opisan kot prva zasebna prevajalska agencija v Sloveniji.",
    "Deluje mednarodno (Total Slovenia News).",
    "V poslovnem registru nismo našli vpisa točno »Amidas d.o.o.« – pravno ime za preveriti pri AJPES.",
    "Notranji podatki (cene, stranke, certifikati, jeziki) niso del te raziskave – potrebni za SWOT.",
])

table("Konkurenti (1/2): večji in mednarodno povezani", [
    ["Podjetje", "Kar je potrjeno", "Za preveriti"],
    ["Ciklopea (Ljubljana, Zagreb, Beograd)", "Podružnica v Ljubljani od 2018; lokalizacija in prevajanje; panoge: medicina, farmacija, tehnologija, proizvodnja", "Pravna oseba v SI (ime v registru se je spremenilo), velikost, cene"],
    ["STAR Prevajalske storitve d.o.o.", "Ljubljana, ustanovljen 2000; del mednarodne skupine STAR (po članku iz 2008)", "Certifikati, obseg, cene"],
    ["Skrivanek", "Češka skupina (1994), 300+ zaposlenih; slovenščino ponuja prek poljske enote", "Slovenske pisarne nismo našli"],
    ["Leemeta (Celje)", "Na Clutch med slovenskimi ponudniki; listinga navajata ISO 17100/9001 (nasprotujoče si navedbe)", "Dejanski certifikati"],
], [3.3, 5.6, 3.4])

table("Konkurenti (2/2): lokalne agencije", [
    ["Podjetje", "Kar je potrjeno", "Za preveriti"],
    ["Birotranslations (BIRO 2000 d.o.o.)", "Ljubljana, Stegne 7; deluje od 1992; ustanovni član Združenja slovenskih prevajalskih podjetij; 3–4 zaposleni", "Specializacije, cene"],
    ["Translat d.o.o.", "Član združenja; po lastnih navedbah dela »v skladu z ISO 17100« (ni trditve o certifikatu)", "Formalni certifikat"],
    ["Prevajalska agencija Julija d.o.o.", "Ljubljana, Barjanska cesta 80", "Velikost, storitve, cene"],
    ["ATE Globalis / Adriatiqa Translations", "Ljubljana, Štihova 13", "Velikost, storitve"],
    ["Trans Linguis, Slavna, TAIA INT, Eurotranslate, M prevodi", "Vpisani v poslovni register kot prevajalska podjetja v Ljubljani; Trans Linguis ima 2 zaposlena", "Vse ostalo"],
], [3.6, 5.6, 3.1])

bullets("Kaj vemo o cenah", [
    "Tržnih cenikov konkurentov v javnih virih nismo našli.",
    "Edino referenco daje javni razpis iz 2020: 25,80 EUR bruto na obračunsko stran (1.500 znakov brez presledkov) – to NI tržna cena.",
    "Sodni prevodi imajo z Pravilnikom omejeno ceno (v razpisu omenjeno do 41,00 EUR).",
    "Predlog: povpraševanje pri 3–5 agencijah (isto besedilo, isti jezikovni par) za pošteno primerjavo.",
])

bullets("Priporočeni naslednji koraki", [
    "1. AJPES: prihodki, zaposleni in dobiček za vsa našteta podjetja → tržna lestvica.",
    "2. Mystery shopping: ista ponudba pri 3–5 agencijah → cene, odzivni čas, ponudba.",
    "3. Preveriti certifikate (ISO 17100, ISO 18587, ISO 9001) pri izdajateljih.",
    "4. SWOT za AMIDAS z notranjimi podatki (ni v javnih virih).",
    "5. Faza 2 – EU: isti postopek z agentom (--scope eu), ločen memory.",
])

bullets("Viri", [
    "bizi.si – poslovni register (Julija, Trans Linguis, Eurotranslate, M prevodi, ATE Globalis, Slavna, TAIA INT, Translat, BIRO 2000)",
    "ELIA – profila Birotranslations in Translat",
    "Ciklopea – ciklopea.com (podružnica Ljubljana, 2018); AmCham Croatia",
    "Fišer (2008), Recent trends in the translation industry in Slovenia, JoSTrans",
    "Total Slovenia News – Amidas, Slovenia's first private translation agency",
    "skrivanek.pl / skrivanek.com; WPML (Leemeta); gov.si – razpis 2021 (cene)",
])
for sl in prs.slides:
    t = sl.shapes.title
    t.left, t.width = Inches(0.7), Inches(11.9)
    for p in t.text_frame.paragraphs:
        p.alignment = 1
    if sl.placeholders and len(sl.placeholders) > 1 and sl.slide_layout == prs.slide_layouts[0]:
        sub = sl.placeholders[1]; sub.left, sub.width = Inches(0.7), Inches(11.9)
        t.top = Inches(2.3); sub.top = Inches(3.9)
prs.save("analiza_konkurence_SI.pptx")
