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
s.placeholders[1].text = "AMIDAS d.o.o. · faza 1 (Slovenija) · osnutek v3 · javni viri + bonitetni podatki"

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


def table_n(title, rows, widths, font=10):
    s = prs.slides.add_slide(prs.slide_layouts[5])
    s.shapes.title.text = title
    s.shapes.title.text_frame.paragraphs[0].font.size = Pt(26)
    s.shapes.title.text_frame.paragraphs[0].font.color.rgb = DARK
    t = s.shapes.add_table(len(rows), len(widths), Inches(0.4), Inches(1.3), Inches(sum(widths)), Inches(5.6)).table
    for j, w in enumerate(widths): t.columns[j].width = Inches(w)
    for i, r in enumerate(rows):
        t.rows[i].height = Inches(0.26)
        for j, v in enumerate(r):
            c = t.cell(i, j); c.text = v
            c.margin_top = c.margin_bottom = Inches(0.01)
            for p in c.text_frame.paragraphs:
                p.font.size = Pt(font); p.font.bold = (i == 0 or "AMIDAS" in r[0])
                if j >= 3: p.alignment = 3

def eur(n): return f"{n:,.0f}".replace(",", ".")
DATA = [
 ("IOLAR d.o.o.","Ljubljana",3881431,5595,797038,20.16,7),
 ("Alcatranz Linguistics d.o.o.","Medvode",2573391,233096,1696013,1.25,10),
 ("LEEMETA d.o.o.","Celje",1271687,263217,414097,5,10),
 ("SDL d.o.o., Ljubljana","Ljubljana",1264716,71703,607908,16.31,10),
 ("AMIDAS d.o.o.","Ljubljana",1004119,537,291887,5.87,8),
 ("ALKEMIST d.o.o.","Ljubljana",984758,20916,97083,6,6),
 ("CeFormT d.o.o.","Trzin",953938,150205,305288,6.47,10),
 ("Prevajalski Studio Milenko Babič d.o.o.","Ljubljana - Polje",912632,-20386,33524,20.65,4),
 ("STAR Prevajalske storitve d.o.o.","Ljubljana - Šentvid",859880,4763,374692,6.6,10),
 ("Zavod združenje tolmačev za slovenski znakovni jezik","Ljubljana",802291,-3958,120541,1,"N"),
 ("VERIS d.o.o.","Ljubljana",800154,-12967,206546,6,7),
 ("Aikwit d.o.o.","Beltinci",667892,57904,180587,3.42,10),
 ("BIRO 2000 d.o.o. (Birotranslations)","Ljubljana",628797,47820,1087333,3.75,10),
 ("Ekspert-S d.o.o.","Ljubljana",593439,19051,113392,0,1),
 ("TRANSLAT d.o.o.","Ljubljana",560914,3295,14621,4.36,5),
 ("TRANSLEKTRA d.o.o.","Maribor",521982,137447,215868,0.91,10),
 ("ALT PLUS d.o.o.","Ljubljana",519569,5574,93824,8.31,10),
 ("Prevajalska agencija Julija d.o.o.","Ljubljana",517224,45176,325173,3,8),
 ("Mojca Andrijanič s.p.","Novo mesto",457253,37525,412333,0,10),
 ("PREVEKSO d.o.o.","Bled",436200,11952,190333,3.15,10),
]
rows = [["#", "Podjetje", "Kraj", "Prihodki €", "Čisti izid €", "Kapital €", "Zaposleni", "Prih./zaposl. tis. €", "Bonit. ocena"]]
for i, (n, k, p, iz, kap, z, o) in enumerate(DATA, 1):
    pz = f"{p / z / 1000:.0f}" if z >= 2 else "–"
    rows.append([str(i), n, k, eur(p), eur(iz), eur(kap), f"{z:.2f}".replace(".", ","), pz, str(o)])
table_n("Top 20 po prihodkih (iz baze ebonitete.si)", [[r[0]] + r[1:] for r in rows], [0.4, 3.9, 1.6, 1.2, 1.1, 1.1, 0.9, 1.4, 0.8])
slide_note = prs.slides[-1].shapes.add_textbox(Inches(0.4), Inches(7.0), Inches(12.5), Inches(0.4))
slide_note.text_frame.text = "Vir: PBA ebonitete.si (posnetek zaslona, 3.643 zadetkov, razvrščeno po prihodkih). Leto izkazov ni razvidno. Seznam ni nujno omejen na prevajalska podjetja. Prih./zaposl. je naš izračun (le pri 2+ zaposlenih)."
slide_note.text_frame.paragraphs[0].font.size = Pt(10); slide_note.text_frame.paragraphs[0].font.color.rgb = GREY
slide_note.text_frame.word_wrap = True

bullets("AMIDAS v primerjavi z lestvico", [
    "Po prihodkih je AMIDAS 5. na lestvici: 1,00 mio. €. Pred njim so IOLAR (3,88), Alcatranz Linguistics (2,57), Leemeta (1,27) in SDL (1,26 mio. €).",
    "Za AMIDAS so STAR (0,86), BIRO 2000 (0,63), Translat (0,56) in Julija (0,52 mio. €).",
    "Prihodki na zaposlenega: AMIDAS ≈ 171 tis. €; Leemeta ≈ 254 tis., IOLAR ≈ 193 tis., STAR ≈ 130 tis., Translat ≈ 129 tis. €.",
    "Čisti izid AMIDAS je 537 €, kapital 292 tis. €; Leemeta ima izid 263 tis. €, CeFormT 150 tis. € – marža je področje za razpravo.",
    "Ciklopea in Skrivanek nista med prvimi 20 (slovenska pravna oseba Ciklopee v registru nosi drugo ime – za preveriti).",
], "Vir: ebonitete.si. Leto izkazov ni razvidno; prihodki so lahko deloma izvozni. Zaposleni so lahko povprečje FTE.")

bullets("Izhodišče: AMIDAS d.o.o. (po lastnih navedbah)", [
    "Ljubljana (Ukmarjeva ulica 2), od 1991; družinsko podjetje; prevedli so tudi Ustavo RS.",
    "Mreža 300+ samostojnih prevajalcev in partnerskih agencij; prevaja le v materni jezik; »največja ekipa angleških naravnih govorcev v državi«.",
    "Storitve: prevajanje, strojno prevajanje (Amidas MT v orodju memoQ), lektoriranje, sodni prevodi, vse tri vrste tolmačenja.",
    "Članstva: soustanovitelj ELIA, ustanovni član Eulogia, član Združenja prevajalskih podjetij Slovenije.",
    "Certifikata ISO 17100 in ISO 9001 (podatek naročnika; na amidas.si nista omenjena). Cenika in referenc na strani ni.",
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
    "Certifikati: AMIDAS ima ISO 17100 in 9001, a ju spletna stran ne omenja. Ciklopea ju izpostavlja na naslovnici, Translat in Leemeta ju omenjata – hitra priložnost: certifikata pokazati.",
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
    "3. Certifikate konkurentov (ISO 17100, 18587, 9001) preveriti pri izdajateljih; certifikata AMIDAS objaviti na spletni strani.",
    "4. SWOT za AMIDAS z notranjimi podatki (ni v javnih virih).",
    "5. Faza 2 – EU: isti postopek z agentom (--scope eu), ločen memory.",
])

bullets("Viri", [
    "Spletne strani: amidas.si, ciklopea.com, star-ljubljana.si, translat.si, leemeta.com, birotranslations.com (stanje: november 2026)",
    "bizi.si – poslovni register; ELIA – profila Birotranslations in Translat; PBA ebonitete.si – finančni podatki (posnetek zaslona)",
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
