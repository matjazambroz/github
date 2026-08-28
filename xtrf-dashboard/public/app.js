const SYMBOLS = { EUR: "€", USD: "$", GBP: "£" };
const STAGE_WIDTH = 1600;

function fitStage() {
  const stage = document.getElementById("stage");
  const scale = Math.min(window.innerWidth / STAGE_WIDTH, window.innerHeight / stage.scrollHeight);
  stage.style.transform = `scale(${scale})`;
}

function formatAmount(amount) {
  return new Intl.NumberFormat("sl-SI", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    useGrouping: true,
  }).format(amount);
}

function currencyLabel(code) {
  return SYMBOLS[code] ? `${SYMBOLS[code]} ${code}` : code;
}

function renderCards(container, totals, unitLabel) {
  container.innerHTML = "";
  const entries = Object.entries(totals ?? {});
  if (entries.length === 0) {
    container.innerHTML = '<div class="empty">Brez podatkov za danes</div>';
    return;
  }
  for (const [code, { amount, count }] of entries) {
    const symbol = SYMBOLS[code] ?? "";
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <div class="currency">${currencyLabel(code)}</div>
      <div class="value">${symbol}${formatAmount(amount)}</div>
      <div class="count">${count} ${unitLabel}</div>
    `;
    container.appendChild(card);
  }
}

function formatRate(rate) {
  return new Intl.NumberFormat("sl-SI", { minimumFractionDigits: 4, maximumFractionDigits: 6 }).format(rate);
}

function renderRatesNote(elementId, rates) {
  const el = document.getElementById(elementId);
  if (!rates || rates.length === 0) {
    el.textContent = "";
    return;
  }
  const parts = rates.map((r) => {
    const dateStr = r.date
      ? new Date(r.date).toLocaleDateString("sl-SI", { day: "numeric", month: "numeric", year: "numeric" })
      : "?";
    return `1 EUR = ${formatRate(r.rate)} ${r.code} (${dateStr})`;
  });
  el.textContent = `Tečaj: ${parts.join(" · ")}`;
}

function renderYtd(ytd) {
  const label = document.getElementById("ytd-label");
  const cells = [1, 2, 3, 4, 5, 6, 7, 8].map((n) => document.getElementById(`ytd-cell-${n}`));
  cells.forEach((c) => (c.innerHTML = ""));

  if (!ytd || ytd.status === "loading") {
    cells[0].innerHTML = '<div class="empty">Se nalaga...</div>';
    return;
  }
  if (ytd.status === "error" || !ytd.data) {
    cells[0].innerHTML = '<div class="empty">Ni na voljo</div>';
    return;
  }

  const { turnover, costs, paidTurnover, paidCosts, priorTurnover, priorCosts, projectSummary } = ytd.data;
  label.textContent = `YTD ${turnover.year} (vs. ${priorTurnover?.year ?? turnover.year - 1} do istega dne)`;

  const makeCard = (title, data, prior, unit, extraHtml = "") => {
    const card = document.createElement("div");
    card.className = "card";
    let compareHtml = "";
    if (prior && prior.amount > 0) {
      const deltaPct = ((data.amount - prior.amount) / prior.amount) * 100;
      const sign = deltaPct >= 0 ? "+" : "";
      const cls = deltaPct >= 0 ? "delta-up" : "delta-down";
      compareHtml = `
        <div class="compare">lani: &euro;${formatAmount(prior.amount)}</div>
        <div class="compare ${cls}">${sign}${formatAmount(deltaPct)}%</div>
      `;
    }
    card.innerHTML = `
      <div class="currency">${title} &middot; neto</div>
      <div class="value">&euro;${formatAmount(data.amount)}</div>
      <div class="count">${data.count} ${unit}</div>
      ${extraHtml}
      ${compareHtml}
    `;
    return card;
  };

  let marginHtml = "";
  if (turnover.amount > 0) {
    const marginPct = ((turnover.amount - costs.amount) / turnover.amount) * 100;
    const cls = marginPct >= 37 ? "margin-good" : "margin-bad";
    marginHtml = `<div class="margin">marža <span class="margin-value ${cls}">${formatAmount(marginPct)}%</span></div>`;
  }

  cells[0].appendChild(makeCard("Izdani računi", turnover, priorTurnover, "računov", marginHtml));
  cells[1].appendChild(makeCard("Prejeti računi", costs, priorCosts, "računov"));
  if (paidTurnover) {
    cells[2].appendChild(makeCard("Plačani računi", paidTurnover, null, "računov"));
  }
  if (paidCosts) {
    cells[3].appendChild(makeCard("Plačani stroški", paidCosts, null, "računov"));
  }

  if (projectSummary) {
    const { revenueClosed, revenueOpen, costClosed, costOpen } = projectSummary;

    const makeProjectCard = (title, closed, open, extraHtml = "") => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <div class="currency">${title}</div>
        <div class="value">&euro;${formatAmount(closed.amount)}</div>
        <div class="count">${closed.count} projektov &middot; zaprti</div>
        <div class="secondary">+ odprti: &euro;${formatAmount(open.amount)} (${open.count})</div>
        ${extraHtml}
      `;
      return card;
    };

    let projectMarginHtml = "";
    if (revenueClosed.amount > 0) {
      const projectMarginPct = ((revenueClosed.amount - costClosed.amount) / revenueClosed.amount) * 100;
      const cls = projectMarginPct >= 37 ? "margin-good" : "margin-bad";
      projectMarginHtml = `<div class="margin">marža <span class="margin-value ${cls}">${formatAmount(projectMarginPct)}%</span></div>`;
    }

    cells[4].appendChild(makeProjectCard("Promet YTD", revenueClosed, revenueOpen, projectMarginHtml));
    cells[5].appendChild(makeProjectCard("Stroški YTD", costClosed, costOpen));
  }

  // Unpaid amount = all issued/received invoices minus the fully-paid
  // subset - pure arithmetic on numbers already computed above, no extra
  // API calls needed.
  const makeUnpaidCard = (title, total, paid) => {
    const card = document.createElement("div");
    card.className = "card";
    const unpaidAmount = total.amount - (paid?.amount ?? 0);
    const unpaidCount = total.count - (paid?.count ?? 0);
    card.innerHTML = `
      <div class="currency">${title}</div>
      <div class="value">&euro;${formatAmount(unpaidAmount)}</div>
      <div class="count">${unpaidCount} računov &middot; neplačano</div>
    `;
    return card;
  };

  cells[6].appendChild(makeUnpaidCard("Razlika Izdani računi YTD", turnover, paidTurnover));
  cells[7].appendChild(makeUnpaidCard("Razlika Prejeti računi YTD", costs, paidCosts));
}

function updateClock() {
  const now = new Date();
  document.getElementById("clock").textContent = now.toLocaleTimeString("sl-SI", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
  document.getElementById("date").textContent = now.toLocaleDateString("sl-SI", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

async function refresh() {
  try {
    const res = await fetch("/api/status", { cache: "no-store" });
    const { today, ytd } = await res.json();

    const banner = document.getElementById("error-banner");
    if (today.status === "error") {
      banner.textContent = `Napaka pri osveževanju: ${today.error}`;
      banner.classList.add("visible");
    } else {
      banner.classList.remove("visible");
    }

    if (today.data) {
      renderCards(document.getElementById("agreed-cards"), today.data.totalAgreed, "projektov");
      renderCards(document.getElementById("agreed-week-cards"), today.data.totalAgreedWeek, "projektov");
      renderRatesNote("week-rates-note", today.data.totalAgreedWeekRates);
      renderCards(document.getElementById("paid-cards"), today.data.paidInvoices, "računov");
      renderRatesNote("rates-note", today.data.paidInvoiceRates);
      renderCards(document.getElementById("paid-week-cards"), today.data.paidInvoicesWeek, "računov");
      renderRatesNote("paid-week-rates-note", today.data.paidInvoicesWeekRates);
    }
    renderYtd(ytd);

    const footer = document.getElementById("footer");
    const parts = [];
    if (today.lastUpdated) {
      parts.push(`danes: ${new Date(today.lastUpdated).toLocaleTimeString("sl-SI", { hour: "2-digit", minute: "2-digit" })}`);
    }
    if (ytd?.lastUpdated) {
      parts.push(`YTD: ${new Date(ytd.lastUpdated).toLocaleTimeString("sl-SI", { hour: "2-digit", minute: "2-digit" })}`);
    }
    footer.textContent = parts.length ? `Zadnja osvežitev — ${parts.join(", ")}` : "";
  } catch (err) {
    const banner = document.getElementById("error-banner");
    banner.textContent = "Ni povezave s strežnikom.";
    banner.classList.add("visible");
  }
}

const stageResizeObserver = new ResizeObserver(fitStage);
stageResizeObserver.observe(document.getElementById("stage"));
window.addEventListener("resize", fitStage);

updateClock();
refresh();
fitStage();
setInterval(updateClock, 1000);
setInterval(refresh, 1000 * 60);
