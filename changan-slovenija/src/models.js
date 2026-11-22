// Podatki o modelih (vir: changanslovenija.si/model/...) in izris strani posameznega modela.

import COLORS from "./colors.json";

const SITE = "https://changan-slovenija.matjaz-ambroz.workers.dev";

export const MODELS = {
  "deepal-s05": {
    name: "Deepal S05",
    img: "/img/deepal-s05.jpg",
    gallery: ["/img/deepal-s05-phev.jpg"],
    tag: "Kompaktni SUV · električni ali PHEV",
    title: "Pelji prihodnost.",
    lead: "Nagrajeno oblikovanje (iF Design Award), nastalo v Changanovem oblikovalskem centru v Torinu. Aerodinamična linija s koeficientom upora le 0,25 pomeni večjo učinkovitost in daljši doseg.",
    specs: [
      ["240 km", "dosega v 15 minutah hitrega polnjenja (DC)"],
      ["0,25", "koeficient zračnega upora"],
      ["1600 kg", "vlečna zmogljivost"],
      ["15,4″", "nagibni zaslon na dotik"],
      ["492 l", "prtljažnik (do 1250 l) + 159 l sprednji"],
      ["2880 mm", "medosna razdalja"],
    ],
    highlights: [
      "Svetlobni podpis Energy Interaction Ring Lights ves čas prikazuje stanje napolnjenosti vozila.",
      "Vratna okna brez okvirja in električno pomične skrite kljuke za razkošen videz.",
      "Aktivna aerodinamika: maska se pri visokih hitrostih samodejno zapre.",
      "Toplotna črpalka in grelec baterije za zanesljiv doseg v vseh vremenskih razmerah.",
      "Čip Qualcomm 8155, 50-vatni brezžični polnilnik in 14-zvočniški Hi-Fi sistem.",
      "Sprednja sedeža ogrevana in prezračevana, sopotnik pa ima sedež Queen’s Seat z električnim naslonom za noge.",
      "1,9 m² velika panoramska streha z električnim zatemnjevanjem.",
    ],
    variants: [
      ["S05 električni", "Čisto električni pogon z možnostjo hitrega polnjenja z enosmernim tokom."],
      ["S05 PHEV (Ultra-Hybrid)", "Skupni doseg do 1060 km, do 100 km električnega dosega (WLTP). Kombinirana poraba 2,03 l/100 km, CO₂ 47 g/km, poraba električne energije 18,0 kWh/100 km (WLTP)."],
    ],
    colors: ["Blue", "Silver", "Comet White", "Eclipse Black", "Gray"],
    official: "https://changanslovenija.si/model/changan-deepal-s05/",
    docs: [
      ["Cenik S05 Max RWD (PDF)", "https://changanslovenija.si/wp-content/uploads/2026/06/Deepal_S05_Max_RWD_Ponudba_Cenik-splet.pdf"],
      ["Cenik S05 PHEV (PDF)", "https://changanslovenija.si/wp-content/uploads/2026/09/Changan-Deepal-S05-PHEV-cenik-SLO-WEB-v7.pdf"],
    ],
    note: "Podatki o porabi in emisijah so izmerjeni po postopku WLTP; dejanska poraba, izpusti in električni doseg so odvisni od načina vožnje, vremena, temperature, obremenitve in hitrosti.",
  },
  "deepal-s07": {
    name: "Deepal S07",
    img: "/img/deepal-s07.jpg",
    gallery: [],
    tag: "Coupé SUV · električni",
    title: "Zanesljiv. Zabaven.",
    lead: "Italijansko oblikovalsko znanje in sodobna kitajska tehnologija v dinamičnem coupé SUV-ju. Športen značaj coupéja z vsestranskostjo SUV-ja.",
    specs: [
      ["475 km", "doseg"],
      ["160 kW", "moč"],
      ["79,97 kWh", "baterija"],
      ["15,6″", "zaslon na dotik v obliki sončnice"],
      ["10 smeri", "nastavitev voznikovega sedeža"],
      ["AR HUD", "prikaz na vetrobranskem steklu"],
    ],
    highlights: [
      "Svetlobna letev LED po celotni širini in prepoznaven svetlobni podpis.",
      "Električno pomične skrite vratne kljuke, ki izboljšajo aerodinamiko.",
      "AR Head-Up prikaz v realnem času kaže navigacijo, hitrost in varnostna opozorila.",
      "Zaslon na dotik, ki ga lahko obrnete proti vozniku ali sovozniku.",
      "Ogrevana in hlajena sprednja sedeža, voznikove nastavitve se shranijo.",
    ],
    variants: [],
    colors: ["Sunset Orange", "Comet White", "Eclipse Black", "Lunar Gray", "Nebula Green"],
    official: "https://changanslovenija.si/model/changan-deepal-s07/",
    docs: [["Brošura S07 (PDF)", "https://changanslovenija.si/wp-content/uploads/2026/06/Changan-Deepal-S07-brosura-SLO-V07-WEB24.pdf"]],
    note: "Rok dobave in razpoložljivost preverite pri prodajalcu.",
  },
  "cs55-plus": {
    name: "Changan CS55 PLUS",
    img: "/img/cs55-plus.jpg",
    gallery: [],
    tag: "Mestni SUV segmenta C · bencinski",
    title: "Začutite premijski razred.",
    lead: "Mestni SUV segmenta C za udobnejšo, bolj intuitivno in dovršeno vsakdanjo vožnjo. Sodoben dizajn, napredne tehnologije in bogata serijska oprema v kompaktni karoseriji.",
    specs: [
      ["1,5T", "motor BlueCore"],
      ["280 Nm", "največji navor"],
      ["350 bar", "tlak neposrednega vbrizga"],
      ["7DCT", "samodejni menjalnik z dvojno sklopko"],
      ["7 let", "ali 160.000 km garancije"],
      ["12 let", "garancije proti prerjavenju"],
    ],
    highlights: [
      "Motor BlueCore 1,5T je zasnovan za odzivnost in učinkovitost v mestu in na odprti cesti.",
      "7-stopenjski menjalnik z dvojno sklopko prestavlja hitro, natančno in skoraj neopazno.",
      "Uravnotežena vožnja, enako prepričljiva v mestnem vrvežu kot na daljših potovanjih.",
    ],
    variants: [],
    colors: ["Fluoritno siva", "Diamantno grafitna", "Zvezdno črna", "Lunina belina", "Šampanjski sijaj"],
    official: "https://changanslovenija.si/model/changan-cs-55-plus/",
    docs: [],
    note: "Aktualne akcijske cene in pogoje najdete na uradni strani ali pri prodajalcu.",
  },
  "cs75-plus": {
    name: "Changan CS75 PLUS",
    img: "/img/cs75-plus.jpg",
    gallery: [],
    tag: "Družinski SUV · bencinski",
    title: "Pametni SUV za vsakdan.",
    lead: "Sodoben SUV za družinske obveznosti, mobilnost v mestu in spontane izlete. Udobje, intuitivne tehnologije in učinkovite zmogljivosti.",
    specs: [
      ["3 zasloni", "digitalna plošča, osrednji in sopotnikov zaslon"],
      ["256 barv", "ambientna LED-osvetlitev, v ritmu glasbe"],
      ["Panorama", "steklena streha z električnim senčilom"],
      ["7 let", "ali 160.000 km garancije"],
      ["12 let", "garancije proti prerjavenju"],
      ["CarPlay", "Apple CarPlay in Android Auto"],
    ],
    highlights: [
      "Mehke površine, oblazinjenje, navdihnjeno z napa usnjem, in detajli z leseno strukturo.",
      "Trojni zaslon nove generacije: vse je na svojem mestu, brez nereda in iskanja.",
      "Panoramska steklena streha napolni kabino z naravno svetlobo.",
    ],
    variants: [],
    colors: ["Svetlo siva Atom", "Kristalno bela", "Azurno modra", "Šampanjski sijaj", "Siva Andes", "Plemenito črna"],
    official: "https://changanslovenija.si/model/changan-cs-75-plus/",
    docs: [],
    note: "Aktualne akcijske cene in pogoje najdete na uradni strani ali pri prodajalcu.",
  },
};

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

export function renderModel(slug, home) {
  const m = MODELS[slug];
  if (!m) return null;
  const style = home.match(/<style>[\s\S]*?<\/style>/)[0];
  const header = home
    .match(/<header>[\s\S]*?<\/header>/)[0]
    .replace('class="logo" href="#"', 'class="logo" href="/"')
    .replace(/href="#(modeli|prednosti|kontakt)"/g, 'href="/#$1"')
    .replace('href="/#kontakt">Testna', `href="/?model=${slug}#kontakt">Testna`);
  const footer = home.match(/<footer>[\s\S]*?<\/footer>/)[0];
  const url = `${SITE}/modeli/${slug}`;
  const others = Object.entries(MODELS).filter(([k]) => k !== slug);

  const specs = m.specs.map(([v, l]) => `<div><b>${esc(v)}</b><span>${esc(l)}</span></div>`).join("");
  const hl = m.highlights.map((h) => `<li>${esc(h)}</li>`).join("");
  const variants = m.variants.length
    ? `<section class="alt"><div class="wrap"><h2>Izvedbe</h2><div class="grid">${m.variants
        .map(([n, d]) => `<div class="feat"><h3>${esc(n)}</h3><p style="color:var(--mut)">${esc(d)}</p></div>`)
        .join("")}</div></div></section>`
    : "";
  const gallery = `<div class="wrap" style="display:grid;gap:22px"><img class="wide" src="${m.img}" alt="${esc(m.name)}" loading="lazy">${m.gallery
    .map((g) => `<img class="wide" src="${g}" alt="${esc(m.name)}" loading="lazy">`)
    .join("")}</div>`;
  const cfg = COLORS[slug] || { ext: [], int: [] };
  const sw = (list, kind) =>
    list
      .map(
        (c, i) =>
          `<button type="button" class="sw" data-k="${kind}" data-i="${i}" style="--c:${c.hex}" aria-label="${esc(c.n)}" aria-pressed="${i === 0 ? "true" : "false"}" title="${esc(c.n)}"></button>`
      )
      .join("");
  const viewer = `<div class="viewer" id="viewer"><div class="layer on"><img src="${cfg.ext[0].img}" alt="${esc(m.name)}"></div></div>
    ${cfg.int.length ? `<div class="tabs" role="tablist"><button type="button" class="tab on" data-v="ext">Zunanjost</button><button type="button" class="tab" data-v="int">Notranjost</button></div>` : ""}
    <div class="pick"><div class="lbl">Barva zunanjosti: <b id="en">${esc(cfg.ext[0].n)}</b></div><div class="sws">${sw(cfg.ext, "ext")}</div></div>
    ${cfg.int.length ? `<div class="pick"><div class="lbl">Barva notranjosti: <b id="in">${esc(cfg.int[0].n)}</b></div><div class="sws">${sw(cfg.int, "int")}</div></div>` : ""}
    <p class="note" style="margin:10px 0 0">Prikaz je ilustrativen; barve na zaslonu se lahko razlikujejo od dejanskih.</p>`;
  const docs = [["Več na uradni strani", m.official], ...m.docs]
    .map(([t, h]) => `<a class="btn ghost" href="${h}" rel="noopener" target="_blank">${esc(t)}</a>`)
    .join("");
  const more = others
    .map(
      ([k, o]) =>
        `<a class="card" href="/modeli/${k}"><div class="car"><img src="${o.img}" alt="${esc(o.name)}" loading="lazy"></div><div class="body"><span class="pill">${esc(o.tag)}</span><h3>${esc(o.name)}</h3></div></a>`
    )
    .join("");

  return `<!doctype html>
<html lang="sl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script>(function(){try{var t=localStorage.getItem('theme')}catch(e){}if(!t)t=matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';document.documentElement.setAttribute('data-theme',t)})()</script>
<script>document.documentElement.classList.add('js')</script>
<title>${esc(m.name)} – Changan Slovenija</title>
<meta name="description" content="${esc(m.name)}: ${esc(m.lead)}">
<meta property="og:title" content="${esc(m.name)} – Changan Slovenija">
<meta property="og:description" content="${esc(m.lead)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="sl_SI">
<meta property="og:url" content="${url}">
<meta property="og:image" content="${SITE}${m.img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="canonical" href="${url}">
${style}
<style>
.mhero{padding:48px 0 56px}.crumb{color:var(--mut);font-size:.9rem;margin-bottom:18px}.crumb a:hover{color:var(--fg)}
.mhero .row{display:grid;grid-template-columns:1fr 1.15fr;gap:40px;align-items:center}
@media(max-width:860px){.mhero .row{grid-template-columns:1fr}}
.mhero h1{font-size:clamp(2rem,5vw,3.2rem);line-height:1.05;margin:10px 0 16px}
.mhero p.l{color:var(--mut);max-width:48ch;margin-bottom:26px}
.mhero .photo{border-radius:var(--r);overflow:hidden;border:1px solid var(--line);aspect-ratio:16/10}
.mhero .photo img,img.wide{width:100%;height:100%;object-fit:cover;display:block}
img.wide{border-radius:var(--r);border:1px solid var(--line);height:auto;aspect-ratio:2/1}
.hl{list-style:none;padding:0;display:grid;gap:12px;max-width:70ch}
.hl li{padding-left:28px;position:relative;color:var(--mut)}
.hl li:before{content:"";position:absolute;left:0;top:.55em;width:14px;height:2px;background:linear-gradient(90deg,var(--acc),var(--acc2))}
.row2{display:flex;gap:12px;flex-wrap:wrap;margin-top:6px}
.note{color:var(--mut);font-size:.82rem;margin-top:22px}
a.card{display:block}
.viewer{position:relative;aspect-ratio:16/10;border-radius:var(--r);overflow:hidden;border:1px solid var(--line);background:#e9edf2}
.layer{position:absolute;inset:0;opacity:0;transform:scale(1.025);isolation:isolate;background:radial-gradient(120% 90% at 50% 30%,#fff,#dfe5ec);transition:opacity .7s cubic-bezier(.4,0,.2,1),transform .9s cubic-bezier(.2,.7,.2,1);will-change:opacity,transform}
.layer.on{opacity:1;transform:none}
.layer img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;padding:5%;mix-blend-mode:multiply}
.layer.int{background:#111}.layer.int img{object-fit:cover;padding:0;mix-blend-mode:normal}
@media(prefers-reduced-motion:reduce){.layer{transition:none;transform:none}}
.tabs{display:flex;gap:8px;margin:14px 0 4px}
.tab{padding:8px 18px;border-radius:999px;border:1px solid var(--line);background:none;color:var(--mut);font:inherit;font-size:.9rem;cursor:pointer}
.tab.on{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.pick{margin-top:14px}.lbl{color:var(--mut);font-size:.9rem;margin-bottom:8px}.lbl b{color:var(--fg)}
.sws{display:flex;gap:12px;flex-wrap:wrap}
.sw{width:36px;height:36px;border-radius:50%;background:var(--c);border:2px solid var(--line);cursor:pointer;padding:0;box-shadow:inset 0 0 0 2px var(--bg);transition:transform .2s,border-color .2s}
.sw:hover{transform:scale(1.1)}.sw[aria-pressed=true]{border-color:var(--acc);box-shadow:inset 0 0 0 2px var(--bg),0 0 0 3px rgba(47,123,255,.25)}
.sw:focus-visible,.tab:focus-visible{outline:2px solid var(--acc);outline-offset:3px}
</style>
</head>
<body>
${header}
<main>
<div class="mhero"><div class="wrap">
  <div class="crumb"><a href="/">Domov</a> / <a href="/#modeli">Modeli</a> / ${esc(m.name)}</div>
  <div class="row">
    <div><span class="pill">${esc(m.tag)}</span><h1>${esc(m.name)}</h1><p class="l"><b style="color:var(--fg)">${esc(m.title)}</b> ${esc(m.lead)}</p>
      <div class="row2"><a class="btn" href="/?model=${slug}#kontakt">Rezerviraj testno vožnjo</a></div></div>
    <div>${viewer}</div>
  </div>
  <div class="stats">${specs}</div>
</div></div>
${gallery}
<section><div class="wrap"><h2>Poudarki</h2><p class="lead">Kaj izpostavlja model ${esc(m.name)}.</p><ul class="hl">${hl}</ul></div></section>
${variants}
<section><div class="wrap"><h2>Dodatne informacije</h2>
<p class="note" style="margin-top:0">${esc(m.note)} Slike so ilustrativne, oprema in možnosti se lahko razlikujejo glede na izvedbo. Podatki: <a href="${m.official}" rel="noopener" style="text-decoration:underline">changanslovenija.si</a>.</p>
<div class="row2" style="margin-top:22px">${docs}</div></div></section>
<section class="alt"><div class="wrap"><h2>Poglejte še</h2><div class="grid" style="margin-top:24px">${more}</div></div></section>
</main>
${footer}
<script>
(function(){var C=${JSON.stringify(cfg)};var viewer=document.getElementById('viewer');var st={v:'ext',ext:0,int:0},cur=C.ext[0].img,tok=0;
function show(){var l=st.v==='ext'?C.ext:C.int;var src=l[st[st.v]].img;if(src===cur)return;cur=src;var my=++tok;var isInt=st.v==='int';
var n=new Image();function go(){if(my!==tok)return;var layer=document.createElement('div');layer.className='layer'+(isInt?' int':'');var im=document.createElement('img');im.src=src;im.alt='';layer.appendChild(im);viewer.appendChild(layer);void layer.offsetWidth;
var olds=[].slice.call(viewer.querySelectorAll('.layer.on'));layer.classList.add('on');olds.forEach(function(o){o.classList.remove('on');setTimeout(function(){o.remove()},1000)})}
n.onload=go;n.onerror=go;n.src=src}
document.querySelectorAll('.tab').forEach(function(b){b.addEventListener('click',function(){st.v=b.dataset.v;document.querySelectorAll('.tab').forEach(function(t){t.classList.toggle('on',t===b)});show()})});
document.querySelectorAll('.sw').forEach(function(b){b.addEventListener('click',function(){var k=b.dataset.k,i=+b.dataset.i;st[k]=i;st.v=k;document.querySelectorAll('.sw[data-k='+k+']').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});document.getElementById(k==='ext'?'en':'in').textContent=C[k][i].n;document.querySelectorAll('.tab').forEach(function(t){t.classList.toggle('on',t.dataset.v===k)});show()})});
C.ext.concat(C.int).forEach(function(c){var p=new Image();p.src=c.img})})();
document.getElementById('tt').addEventListener('click',function(){var r=document.documentElement,n=r.getAttribute('data-theme')==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('theme',n)}catch(e){}});
document.getElementById('y').textContent=new Date().getFullYear();
(function(){var els=[].slice.call(document.querySelectorAll('section h2,section .lead,.card,.feat,.stats>div,.hl li'));
els.forEach(function(el){el.classList.add('rv')});
document.querySelectorAll('.grid,.stats').forEach(function(g){[].slice.call(g.children).forEach(function(c,i){c.style.setProperty('--d',(i*0.08)+'s')})});
if(!('IntersectionObserver' in window)){els.forEach(function(el){el.classList.add('in')});return}
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.15,rootMargin:'0px 0px -40px 0px'});
els.forEach(function(el){io.observe(el)});})();
</script>
</body>
</html>`;
}
