import html from "./index.html";

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
    if (pathname !== "/" && pathname !== "/index.html") return new Response("Ni najdeno", { status: 404 });
    return new Response(html, {
      headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=300" },
    });
  },
};
