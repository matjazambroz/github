import html from "./index.html";
import { renderModel } from "./models.js";
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

async function handleContact(request, env) {
  if (!env.RESEND_API_KEY) return json({ ok: false, error: "Pošiljanje ni nastavljeno." }, 500);
  let d;
  try { d = await request.json(); } catch { return json({ ok: false, error: "Neveljavna zahteva." }, 400); }

  if (d.website) return json({ ok: true }); // honeypot
  const ime = String(d.ime || "").trim().slice(0, 100);
  const email = String(d.email || "").trim().slice(0, 150);
  const tel = String(d.tel || "").trim().slice(0, 40);
  const model = String(d.model || "").trim().slice(0, 60);
  const sporocilo = String(d.sporocilo || "").trim().slice(0, 2000);
  if (!ime || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json({ ok: false, error: "Vnesite ime in veljavno e-pošto." }, 400);
  }

  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { "content-type": "application/json", authorization: `Bearer ${env.RESEND_API_KEY}` },
    body: JSON.stringify({
      from: env.FROM_EMAIL,
      to: [env.TO_EMAIL],
      reply_to: email,
      subject: `Povpraševanje: testna vožnja – ${model || "model ni izbran"}`,
      html: `<h2>Novo povpraševanje</h2>
<p><b>Ime:</b> ${esc(ime)}<br><b>E-pošta:</b> ${esc(email)}<br><b>Telefon:</b> ${esc(tel) || "–"}<br><b>Model:</b> ${esc(model) || "–"}</p>
<p>${esc(sporocilo).replace(/\n/g, "<br>") || "<i>Brez sporočila</i>"}</p>`,
    }),
  });
  if (!res.ok) {
    console.error("Resend error", res.status, await res.text());
    return json({ ok: false, error: "Pošiljanje ni uspelo. Poskusite znova ali nas pokličite." }, 502);
  }
  return json({ ok: true });
}

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);
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
