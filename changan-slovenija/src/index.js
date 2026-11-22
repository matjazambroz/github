import html from "./index.html";
import { renderModel, renderTestDrive, renderAbout } from "./models.js";
import { GEN } from "./assets.js";
import fL from "./fonts/changan-L.woff2";
import fR from "./fonts/changan-R.woff2";
import fB from "./fonts/changan-B.woff2";

const FONTS = { "/fonts/changan-L.woff2": fL, "/fonts/changan-R.woff2": fR, "/fonts/changan-B.woff2": fB };
import s05 from "./img/deepal-s05.jpg";
import s07 from "./img/deepal-s07.jpg";
import cs55 from "./img/cs55-plus.jpg";
import cs75 from "./img/cs75-plus.jpg";
import s05p from "./img/deepal-s05-phev.jpg";
import og from "./img/og.jpg";
import fav32 from "./img/favicon-32.png";
import touch from "./img/apple-touch-icon.png";
import icon192 from "./img/icon-192.png";

const IMAGES = {
  "/img/deepal-s05.jpg": [s05, "image/jpeg"],
  "/img/deepal-s07.jpg": [s07, "image/jpeg"],
  "/img/cs55-plus.jpg": [cs55, "image/jpeg"],
  "/img/cs75-plus.jpg": [cs75, "image/jpeg"],
  "/img/deepal-s05-phev.jpg": [s05p, "image/jpeg"],
  "/og.jpg": [og, "image/jpeg"],
  "/favicon.png": [fav32, "image/png"],
  "/favicon.ico": [fav32, "image/png"],
  "/apple-touch-icon.png": [touch, "image/png"],
  "/icon-192.png": [icon192, "image/png"],
};

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json; charset=utf-8" } });

async function sendMail(env, { subject, reply_to, rows, message }) {
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { "content-type": "application/json", authorization: `Bearer ${env.RESEND_API_KEY}` },
    body: JSON.stringify({
      from: env.FROM_EMAIL,
      to: [env.TO_EMAIL],
      reply_to,
      subject,
      html: `<h2>${esc(subject)}</h2><p>${rows.map(([k, v]) => `<b>${esc(k)}:</b> ${esc(v) || "–"}`).join("<br>")}</p>
<p>${esc(message).replace(/\n/g, "<br>") || "<i>Brez sporočila</i>"}</p>`,
    }),
  });
  if (!res.ok) {
    console.error("Resend error", res.status, await res.text());
    return json({ ok: false, error: "Pošiljanje ni uspelo. Poskusite znova ali nas pokličite." }, 502);
  }
  return json({ ok: true });
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const clip = (v, n) => String(v || "").trim().slice(0, n);

async function readBody(request, env) {
  if (!env.RESEND_API_KEY) return [null, json({ ok: false, error: "Pošiljanje ni nastavljeno." }, 500)];
  try { return [await request.json(), null]; } catch { return [null, json({ ok: false, error: "Neveljavna zahteva." }, 400)]; }
}

async function handleContact(request, env) {
  const [d, err] = await readBody(request, env);
  if (err) return err;
  if (d.website) return json({ ok: true }); // honeypot
  const ime = clip(d.ime, 100), email = clip(d.email, 150), tel = clip(d.tel, 40), model = clip(d.model, 60);
  if (!ime || !EMAIL_RE.test(email)) return json({ ok: false, error: "Vnesite ime in veljavno e-pošto." }, 400);
  return sendMail(env, {
    subject: `Povpraševanje – ${model || "model ni izbran"}`,
    reply_to: email,
    rows: [["Ime", ime], ["E-pošta", email], ["Telefon", tel], ["Model", model]],
    message: clip(d.sporocilo, 2000),
  });
}

async function handleTestDrive(request, env) {
  const [d, err] = await readBody(request, env);
  if (err) return err;
  if (d.website) return json({ ok: true }); // honeypot
  const ime = clip(d.ime, 100), email = clip(d.email, 150), tel = clip(d.tel, 40);
  const model = clip(d.model, 60), prodajalec = clip(d.prodajalec, 120), datum = clip(d.datum, 10), cas = clip(d.cas, 20);
  if (!ime || !EMAIL_RE.test(email) || !tel) return json({ ok: false, error: "Vnesite ime, veljavno e-pošto in telefon." }, 400);
  if (!model || !prodajalec) return json({ ok: false, error: "Izberite model in prodajalca." }, 400);
  if (datum && !/^\d{4}-\d{2}-\d{2}$/.test(datum)) return json({ ok: false, error: "Neveljaven datum." }, 400);
  return sendMail(env, {
    subject: `Testna vožnja – ${model}`,
    reply_to: email,
    rows: [["Model", model], ["Prodajalec", prodajalec], ["Želeni datum", datum], ["Del dneva", cas], ["Ime", ime], ["E-pošta", email], ["Telefon", tel]],
    message: clip(d.sporocilo, 2000),
  });
}

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);
    if (pathname === "/api/test-drive") {
      if (request.method !== "POST") return json({ ok: false, error: "Metoda ni dovoljena." }, 405);
      return handleTestDrive(request, env);
    }
    if (pathname === "/o-nas" || pathname === "/o-nas/") {
      return new Response(renderAbout(html), {
        headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=300" },
      });
    }
    if (pathname === "/testna-voznja" || pathname === "/testna-voznja/") {
      return new Response(renderTestDrive(html), {
        headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=300" },
      });
    }
    if (pathname === "/api/contact") {
      if (request.method !== "POST") return json({ ok: false, error: "Metoda ni dovoljena." }, 405);
      return handleContact(request, env);
    }
    const mm = pathname.match(/^\/modeli\/([a-z0-9-]+)\/?$/);
    if (mm) {
      const page = renderModel(mm[1], html);
      if (!page) return new Response("Ni najdeno", { status: 404 });
      return new Response(page, {
        headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=300" },
      });
    }
    if (FONTS[pathname]) {
      return new Response(FONTS[pathname], {
        headers: { "content-type": "font/woff2", "cache-control": "public, max-age=31536000, immutable" },
      });
    }
    if (GEN[pathname]) {
      return new Response(GEN[pathname], {
        headers: { "content-type": pathname.endsWith(".webp") ? "image/webp" : "image/jpeg", "cache-control": "public, max-age=86400" },
      });
    }
    if (IMAGES[pathname]) {
      return new Response(IMAGES[pathname][0], {
        headers: { "content-type": IMAGES[pathname][1], "cache-control": "public, max-age=86400" },
      });
    }
    if (pathname !== "/" && pathname !== "/index.html") return new Response("Ni najdeno", { status: 404 });
    return new Response(html, {
      headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=300" },
    });
  },
};
