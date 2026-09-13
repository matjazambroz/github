function formatAmount(amount) {
  return new Intl.NumberFormat("sl-SI", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    useGrouping: true,
  }).format(amount);
}

function formatEuro(amount) {
  return `€ ${formatAmount(amount)}`;
}

function formatTime(iso) {
  if (!iso) return null;
  return new Date(iso).toLocaleTimeString("sl-SI", { hour: "2-digit", minute: "2-digit" });
}

function setValue(id, text, { skeleton = false } = {}) {
  const el = document.getElementById(id);
  el.textContent = text;
  el.classList.toggle("skeleton", skeleton);
}

function updateDate() {
  document.getElementById("date").textContent = new Date().toLocaleDateString("sl-SI", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function render(payload) {
  const banner = document.getElementById("error-banner");
  if (payload.status === "error") {
    banner.textContent = `Napaka pri osveževanju: ${payload.error}`;
    banner.classList.add("visible");
  } else {
    banner.classList.remove("visible");
  }

  const data = payload.data;
  if (!data) {
    setValue("value-day", payload.status === "error" ? "Ni na voljo" : "Nalagam…", { skeleton: true });
    setValue("value-week", payload.status === "error" ? "Ni na voljo" : "Nalagam…", { skeleton: true });
    setValue("value-ytd", payload.status === "error" ? "Ni na voljo" : "Nalagam…", { skeleton: true });
    return;
  }

  setValue("value-day", formatEuro(data.day.amount));
  document.getElementById("meta-day").textContent = `${data.day.count} projektov`;

  setValue("value-week", formatEuro(data.week.amount));
  document.getElementById("meta-week").textContent = `${data.week.count} projektov`;

  document.getElementById("label-ytd").textContent = `Promet YTD ${data.ytd.year}`;
  setValue("value-ytd", formatEuro(data.ytd.amount));
  document.getElementById("meta-ytd").textContent = `${data.ytd.count} računov`;

  const syncingEl = document.getElementById("syncing-ytd");
  if (data.ytd.syncing) {
    syncingEl.textContent = `Posodabljam zgodovino… ${data.ytd.cachedInvoices}/${data.ytd.totalInvoiceCandidates} računov`;
  } else {
    syncingEl.textContent = "";
  }

  const footer = document.getElementById("footer");
  const time = formatTime(payload.updatedAt);
  footer.textContent = time ? `Zadnja osvežitev — ${time}` : "";
}

async function refresh() {
  try {
    const res = await fetch("/api/data", { cache: "no-store" });
    const payload = await res.json();
    render(payload);
  } catch (err) {
    const banner = document.getElementById("error-banner");
    banner.textContent = "Ni povezave s strežnikom.";
    banner.classList.add("visible");
  }
}

updateDate();
refresh();
setInterval(updateDate, 60 * 1000);
setInterval(refresh, 60 * 1000);

// Refresh immediately when the app is brought back to the foreground
// (e.g. reopened from the home screen after a while).
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") {
    refresh();
  }
});
