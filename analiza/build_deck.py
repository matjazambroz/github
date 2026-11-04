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
s.placeholders[1].text = "AMIDAS d.o.o. · faza 1 (Slovenija) · osnutek v2 na podlagi javnih virov"

bullets("Obseg in omejitve", [
    "Cilj: pregled slovenskih konkurentov AMIDAS in izhodišče za razširitev na EU (faza 2).",
    "Viri: spletne strani podjetij (navedbe podjetij samih), poslovni register bizi.si, ELIA, akademski članek.",
    "Česa NI: cene, prihodki in število zaposlenih večine podjetij niso javni; navedbe na spletu so marketinške in neodvisno niso preverjene.",
    "Nepreverjeno je označeno z »za preveriti«. Številk nismo ugibali.",
], "Clutch.co in milengo.com se nista odprla (403/401), zato primerjalnih lestvic nismo uporabili.")

bullets("Slovenski trg prevajalskih storitev", [
    "Prva prevajalska podjetja so nastala 1990–1991; po vstopu v EU (2004) se je število podjetij močno povečalo.",
    "Trg je razdrobljen: v raziskavi iz 2008 je imelo 8 od 10 najuspešnejših podjetij le 4–17 zaposlenih.",
    "Mednarodni igralci z lokalnimi podružnicami (Star, Skrivanek) so bili takrat med prvimi desetimi po tržnem deležu.",
    "Podatek je star 17 let (Fišer, JoSTrans 2008) – nujno ga je osvežiti z AJPES-om.",
], "Vir: Fišer, »Recent trends in the translation industry in Slovenia«, JoSTrans.")

bullets("Izhodišče: AMIDAS d.o.o. (po lastnih navedbah)", [
    "Ljubljana (Ukmarjeva ulica 2), od 1991; družinsko podjetje; prevedli so tudi Ustavo RS.",
    "Mreža 300+ samostojnih prevajalcev in partnerskih agencij; prevaja le v materni jezik; »največja ekipa angleških naravnih govorcev v državi«.",
    "Storitve: prevajanje, strojno prevajanje (Amidas MT v orodju memoQ), lektoriranje, sodni prevodi, vse tri vrste tolmačenja.",
    "Članstva: soustanovitelj ELIA, ustanovni član Eulogia, član Združenja prevajalskih podjetij Slovenije.",
    "Na spletni strani ni navedenih certifikatov ISO, cenika ali referenčnih strank – za preveriti.",
], "Vir: amidas.si (naslovnica, O Amidasu, Strojno prevajanje).")

table("Konkurenti (1/2): večji in mednarodno povezani", [
    ["Podjetje", "Kar navajajo sami", "Za preveriti"],
    ["Ciklopea (Ljubljana od 2018; Zagreb, Beograd)", "30+ jezikov; regulirane panoge (life sciences, tehnika, IT, igre, e-commerce); na strani navedeni ISO 17100, 18587, 9001, 13485, 27001", "Veljavnost certifikatov, velikost v Sloveniji, cene"],
    ["STAR Prevajalske storitve d.o.o. (Ljubljana)", "25 let v SI; del skupine STAR (40 let); lastna programska oprema (STAR Transit, CLM); stalno zaposleni prevajalci; člani EUATC, ZPP", "Certifikati (na naslovnici ni omenjen noben ISO), cene"],
    ["Leemeta (Celje)", "»Prevodi na ključ«: prevod + lektura + DTP; naročniški paketi, spletni hitri izračun cene; 6 faz kontrole kakovosti; lasten IT-oddelek; omenjena ISO 17100 in 9001", "Obseg poslovanja, dejanski certifikati"],
    ["Skrivanek", "Češka skupina (1994), 300+ zaposlenih; slovenščino ponuja prek poljske enote", "Slovenske pisarne nismo našli"],
], [3.0, 6.3, 3.0])

table("Konkurenti (2/2): lokalne in nišne agencije", [
    ["Podjetje", "Kar navajajo sami", "Za preveriti"],
    ["Translat d.o.o. (Ljubljana, Komenskega 12)", "30+ jezikov (140 prek partnerjev); »upoštevamo ISO 17100:2015«; član ZPP, EUATC, ELIA; sodni prevodi, tolmačenje, podnaslavljanje, DTP", "Formalni certifikat, velikost"],
    ["Birotranslations (BIRO 2000 d.o.o., Ljubljana)", "Niša: vzhodnoevropski jeziki za tuje naročnike; 670+ podjetij, 15 mio. besed letno, 25 let, 91 % strank 7+ let; life sciences, avtomobilska, IT", "Naročniki so tuji – to je izvozna, ne domača konkurenca"],
    ["Julija, ATE Globalis (Adriatiqa), Trans Linguis, Slavna, TAIA INT, Eurotranslate, M prevodi", "Samo vpis v poslovni register kot prevajalska podjetja v Ljubljani; Trans Linguis ima 2 zaposlena", "Vse ostalo"],
], [3.6, 5.8, 2.9])

bullets("Kaj opažamo (hipoteze za razpravo)", [
    "Certifikati: Ciklopea jih izpostavlja na naslovnici, Translat in Leemeta jih omenjata; amidas.si jih ne omenja – preveriti, ali jih AMIDAS ima, in če da, jih pokazati.",
    "Tehnologija: STAR ima lastna orodja, Ciklopea »technology-powered«; AMIDAS je s ponudbo Amidas MT (april 2026) v isti smeri.",
    "Cene: Leemeta kaže cene prek paketov in hitrega izračuna; AMIDAS cen ne objavlja.",
    "Kjer AMIDAS izstopa: tradicija od 1991, naravni govorci, slovenščina↔angleščina, polna paleta (sodni prevodi, tolmačenje, MT).",
    "Birotranslations ni neposreden domači konkurent (izvozna niša).",
], "To so opažanja iz spletnih strani, ne ocene tržnega deleža ali kakovosti.")

bullets("Kaj vemo o cenah", [
    "Tržnih cenikov konkurentov (razen naročniških paketov Leemete) v javnih virih nismo našli.",
    "Edina številčna referenca: javni razpis iz 2020 – 25,80 EUR bruto na obračunsko stran (1.500 znakov brez presledkov). To NI tržna cena.",
    "Sodni prevodi imajo z Pravilnikom omejeno ceno (v razpisu omenjeno do 41,00 EUR).",
    "Predlog: povpraševanje pri 3–5 agencijah (isto besedilo, isti jezikovni par) za pošteno primerjavo.",
])

bullets("Priporočeni naslednji koraki", [
    "1. AJPES: prihodki, zaposleni in dobiček za vsa našteta podjetja → tržna lestvica.",
    "2. Mystery shopping: ista ponudba pri 3–5 agencijah → cene, odzivni čas, ponudba.",
    "3. Preveriti certifikate (ISO 17100, 18587, 9001) pri izdajateljih; ugotoviti stanje pri AMIDAS.",
    "4. SWOT za AMIDAS z notranjimi podatki (ni v javnih virih).",
    "5. Faza 2 – EU: isti postopek z agentom (--scope eu), ločen memory.",
])

bullets("Viri", [
    "Spletne strani: amidas.si, ciklopea.com, star-ljubljana.si, translat.si, leemeta.com, birotranslations.com (stanje: november 2026)",
    "bizi.si – poslovni register; ELIA – profila Birotranslations in Translat",
    "Fišer (2008), Recent trends in the translation industry in Slovenia, JoSTrans",
    "skrivanek.pl / skrivanek.com; gov.si – razpis 2021 (cene)",
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
prs.save("analiza_konkurence_SI.pptx")
