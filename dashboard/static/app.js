const state = {
  tab: "market",
  pctSingle: 0.35,
  pctPays: 0.15,
  captureY3: 0.03,
  funnelStep: 3,
};

const $ = (id) => document.getElementById(id);
const fmt = (n) => Number(n).toLocaleString("en-US");

async function api(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`API error: ${path}`);
  return res.json();
}

// ---------------------------------------------------------------------
// Tabs
// ---------------------------------------------------------------------
document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    state.tab = btn.dataset.tab;
    document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("active", b === btn));
    $("marketSection").classList.toggle("hidden", state.tab === "product");
    $("productSection").classList.toggle("hidden", state.tab === "market");
  });
});

// ---------------------------------------------------------------------
// KPIs
// ---------------------------------------------------------------------
async function renderKpis() {
  const k = await api(`/api/kpis?pct_single=${state.pctSingle}&pct_pays=${state.pctPays}&capture_y3=${state.captureY3}`);
  const cards = [
    { label: "TAM 2026", value: `€${k.tam_2026_eur_bn}B`, delta: `+${k.tam_cagr_pct.toFixed(2)}% CAGR to 2034`, color: "var(--sage)", note: "EU dating apps, incl. hybrid matchmaking" },
    { label: "SAM", value: `€${k.sam_eur_bn.toFixed(2)}B`, delta: "Paying tier +11.2% CAGR", color: "var(--sage)", note: "France, paying tier only" },
    { label: "SOM Y3", value: fmt(k.som_y3_users), delta: `${Math.round(k.som_y3_capture_pct)}% capture, Paris`, color: "var(--lavender)", note: "Paying users, bottom-up" },
    { label: "Incumbent momentum", value: `${k.incumbent_avg_yoy_pct}%`, delta: `PURE, no-swipe: +${k.pure_yoy_pct}%`, color: "var(--lavender)", note: "Avg. revenue/user growth, Q1–Q3 2025" },
  ];
  $("kpiGrid").innerHTML = cards.map(c => `
    <div class="kpi-card">
      <div class="kpi-label">${c.label}</div>
      <div class="kpi-value">${c.value}</div>
      <div class="kpi-delta" style="color:${c.color}">${c.delta}</div>
      <div class="kpi-note">${c.note}</div>
    </div>`).join("");
}

// ---------------------------------------------------------------------
// TAM / SAM / SOM funnel + sliders
// ---------------------------------------------------------------------
async function renderTamSom() {
  const d = await api(`/api/tam-som?pct_single=${state.pctSingle}&pct_pays=${state.pctPays}&capture_y3=${state.captureY3}`);
  const tam = d.tam.value_eur_bn;
  const rows = [
    { label: d.tam.label, sub: d.tam.sub, w: 100, value: `€${tam}B`, color: "var(--sage)" },
    { label: d.sam.label, sub: d.sam.sub, w: Math.max(14, (d.sam.value_eur_bn / tam) * 100), value: `€${d.sam.value_eur_bn.toFixed(2)}B`, color: "var(--green-mid)" },
    { label: d.som_y1.label, sub: d.som_y1.sub, w: Math.max(8, (d.som_y1.value_users / 20000) * 100), value: `${fmt(d.som_y1.value_users)} users`, color: "var(--lavender)" },
    { label: d.som_y3.label, sub: d.som_y3.sub, w: Math.max(10, (d.som_y3.value_users / 20000) * 100), value: `${fmt(d.som_y3.value_users)} users`, color: "var(--lav-soft)" },
  ];
  $("funnelRows").innerHTML = rows.map(r => `
    <div class="funnel-row">
      <div class="funnel-label">
        <div class="funnel-label-main">${r.label}</div>
        <div class="funnel-label-sub">${r.sub}</div>
      </div>
      <div class="funnel-track"><div class="funnel-fill" style="width:${r.w.toFixed(1)}%;background:${r.color}"></div></div>
      <div class="funnel-value">${r.value}</div>
    </div>`).join("");

  $("somFootnote").textContent =
    `Addressable Paris pool: ${fmt(d.addressable_paris_pool)} paying singles. SOM is stated in users, not currency — the bars are scaled for comparison, not directly comparable to the € figures above.`;
}

function initSliders() {
  $("pctSingle").value = state.pctSingle * 100;
  $("pctPays").value = state.pctPays * 100;
  $("captureY3").value = state.captureY3 * 100;
  updateSliderLabels();

  const onChange = async () => {
    state.pctSingle = +$("pctSingle").value / 100;
    state.pctPays = +$("pctPays").value / 100;
    state.captureY3 = +$("captureY3").value / 100;
    updateSliderLabels();
    await Promise.all([renderKpis(), renderTamSom()]);
  };
  ["pctSingle", "pctPays", "captureY3"].forEach(id => $(id).addEventListener("input", onChange));
}

function updateSliderLabels() {
  $("pctSingleVal").textContent = Math.round(state.pctSingle * 100) + "%";
  $("pctPaysVal").textContent = Math.round(state.pctPays * 100) + "%";
  $("captureY3Val").textContent = Math.round(state.captureY3 * 100) + "%";
}

// ---------------------------------------------------------------------
// Why now
// ---------------------------------------------------------------------
async function renderWhyNow() {
  const d = await api("/api/demand-context");
  const items = [
    { value: `${Math.round(d.eu_single_households_millions)}M`, label: `EU single-adult households, +${d.single_households_growth_pct_since_2015}% since 2015` },
    { value: `${Math.round(d.pct_eu_adults_no_close_friends)}%`, label: "of EU adults report no close friends" },
    { value: "60.7%", label: "of EU dating-app revenue is paying tier — and it's the faster-growing half" },
  ];
  $("whyNow").innerHTML = items.map(w => `
    <div class="why-now-item">
      <div class="why-now-value">${w.value}</div>
      <div class="why-now-label">${w.label}</div>
    </div>`).join("");
}

// ---------------------------------------------------------------------
// Incumbents
// ---------------------------------------------------------------------
async function renderIncumbents() {
  const list = await api("/api/incumbents");
  const maxMau = Math.max(...list.map(i => i.mau_millions_est));
  $("incumbents").innerHTML = list.map(i => {
    const color = i.yoy_revenue_pct > 0 ? "#2F4A3F" : "#9B7FA8";
    const yoy = (i.yoy_revenue_pct > 0 ? "+" : "") + i.yoy_revenue_pct + "%";
    return `
    <div>
      <div class="incumbent-head">
        <div class="incumbent-name">${i.app}</div>
        <div class="incumbent-stats">${i.mau_millions_est}M MAU est. · $${i.revenue_usd_bn}B rev</div>
      </div>
      <div class="incumbent-track"><div class="incumbent-fill" style="width:${(i.mau_millions_est / maxMau * 100).toFixed(0)}%"></div></div>
      <div class="incumbent-yoy">
        <div class="incumbent-yoy-value" style="color:${color}">${yoy}</div>
        <div class="incumbent-yoy-label">revenue YoY</div>
      </div>
    </div>`;
  }).join("");
}

// ---------------------------------------------------------------------
// Trend chart (SVG)
// ---------------------------------------------------------------------
let trendSeries = [];
let trendHoverIdx = 4;

async function renderTrend() {
  trendSeries = await api("/api/tam-series");
  drawTrend();
}

function drawTrend() {
  const W = 480, H = 168, pad = 14;
  const values = trendSeries.map(d => d.value);
  const vmin = Math.min(...values) - 0.2, vmax = Math.max(...values) + 0.2;
  const px = (i) => pad + (i / (trendSeries.length - 1)) * (W - pad * 2);
  const py = (v) => H - pad - ((v - vmin) / (vmax - vmin)) * (H - pad * 2);
  const hi = Math.min(trendHoverIdx, trendSeries.length - 1);

  const line = trendSeries.map((d, i) => `${px(i).toFixed(1)},${py(d.value).toFixed(1)}`).join(" ");
  const area = `${pad},${H - pad} ${line} ${W - pad},${H - pad}`;

  let svg = `
    <defs>
      <linearGradient id="anaFill" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#A69ACD" stop-opacity="0.35"/>
        <stop offset="100%" stop-color="#A69ACD" stop-opacity="0.02"/>
      </linearGradient>
    </defs>
    <polygon points="${area}" fill="url(#anaFill)"/>
    <polyline points="${line}" fill="none" stroke="#2F4A3F" stroke-width="2.2" stroke-linejoin="round"/>
    <line x1="${px(4)}" y1="${pad}" x2="${px(4)}" y2="${H - pad}" stroke="#DDEAE6" stroke-width="1" stroke-dasharray="3 3"/>
    <text x="${px(4) + 5}" y="${pad + 10}" font-size="9.5" fill="#9AA79F" font-family="Inter">today</text>`;

  trendSeries.forEach((d, i) => {
    svg += `<circle cx="${px(i)}" cy="${py(d.value)}" r="${i === hi ? 5 : 3}" fill="${i === hi ? '#A69ACD' : '#2F4A3F'}" stroke="#FFFFFF" stroke-width="${i === hi ? 2 : 0}"/>`;
    svg += `<rect x="${px(i) - 16}" y="0" width="32" height="${H}" fill="transparent" data-idx="${i}" class="trend-hit"/>`;
  });
  trendSeries.forEach((d, i) => {
    if (i % 3 === 0 || i === trendSeries.length - 1) {
      svg += `<text x="${px(i)}" y="${H + 12}" font-size="10" fill="#9AA79F" font-family="Inter" text-anchor="middle">${d.year}</text>`;
    }
  });

  const el = $("trendChart");
  el.setAttribute("viewBox", `0 0 ${W} ${H + 22}`);
  el.innerHTML = svg;
  el.querySelectorAll(".trend-hit").forEach(rect => {
    rect.addEventListener("mouseenter", () => {
      trendHoverIdx = +rect.dataset.idx;
      drawTrend();
      updateTrendHoverLabel();
    });
  });
  updateTrendHoverLabel();
}

function updateTrendHoverLabel() {
  const d = trendSeries[Math.min(trendHoverIdx, trendSeries.length - 1)];
  $("trendHoverValue").textContent = `€${d.value.toFixed(2)}B`;
  $("trendHoverYear").textContent = d.year;
}

// ---------------------------------------------------------------------
// Growth comparison
// ---------------------------------------------------------------------
async function renderGrowth() {
  const list = await api("/api/growth");
  $("growth").innerHTML = list.map(g => {
    const negWidth = g.pct_change < 0 ? (Math.abs(g.pct_change) / 95 * 100).toFixed(1) + "%" : "0%";
    const posWidth = g.pct_change > 0 ? (g.pct_change / 95 * 100).toFixed(1) + "%" : "0%";
    const color = g.pct_change > 0 ? "#2F4A3F" : "#9B7FA8";
    const label = (g.pct_change > 0 ? "+" : "") + g.pct_change + "%";
    return `
    <div class="growth-row">
      <div class="growth-name">${g.player}</div>
      <div class="growth-bars">
        <div class="growth-neg-wrap"><div class="growth-neg" style="width:${negWidth}"></div></div>
        <div class="growth-mid"></div>
        <div class="growth-pos-wrap"><div class="growth-pos" style="width:${posWidth}"></div></div>
      </div>
      <div class="growth-value" style="color:${color}">${label}</div>
    </div>`;
  }).join("");
}

// ---------------------------------------------------------------------
// Product funnel
// ---------------------------------------------------------------------
async function renderProductFunnel() {
  const d = await api("/api/product-funnel");
  const funnel = d.funnel;
  const max = funnel[0].value;
  $("productFunnel").innerHTML = funnel.map((f, i) => {
    const color = i === state.funnelStep ? "var(--lavender)" : i === 4 ? "var(--green-mid)" : "var(--sky)";
    const textColor = (i === state.funnelStep || i === 4) ? "#FFFFFF" : "var(--sage)";
    const width = Math.max(12, (f.value / max) * 100).toFixed(0) + "%";
    return `
    <div class="pf-row" data-idx="${i}">
      <div class="pf-label">${f.label}</div>
      <div class="pf-track"><div class="pf-fill" style="width:${width};background:${color};color:${textColor}"></div></div>
      <div class="pf-value">${fmt(f.value)}</div>
      <div class="pf-pct">${Math.round(f.value / max * 100)}%</div>
    </div>`;
  }).join("");

  document.querySelectorAll(".pf-row").forEach(row => {
    row.addEventListener("click", () => {
      state.funnelStep = +row.dataset.idx;
      renderProductFunnel();
    });
  });

  $("funnelNote").textContent = d.drops[state.funnelStep].note;
}

// ---------------------------------------------------------------------
// Score chart (SVG bars)
// ---------------------------------------------------------------------
async function renderScoreChart() {
  const d = await api("/api/score-chart");
  const curve = d.curve;
  $("liftValue").textContent = "+" + d.mean_lift;

  const CW = 420, CH = 150;
  const bw = CW / curve.length;
  let svg = "";
  curve.forEach((row, i) => {
    const a = row.without_friend, b = row.with_friend;
    const ha = a * (CH - 10), hb = b * (CH - 10);
    svg += `<rect x="${i * bw + 6}" y="${CH - ha}" width="${bw / 2 - 6}" height="${ha}" fill="#C7D6CE" rx="3"/>`;
    svg += `<rect x="${i * bw + bw / 2}" y="${CH - hb}" width="${bw / 2 - 6}" height="${hb}" fill="#A69ACD" rx="3"/>`;
    svg += `<text x="${i * bw + bw / 2}" y="${CH + 14}" font-size="10" fill="#9AA79F" font-family="Inter" text-anchor="middle">${row.score}</text>`;
  });
  const el = $("scoreChart");
  el.setAttribute("viewBox", `0 0 ${CW} ${CH + 20}`);
  el.innerHTML = svg;
}

// ---------------------------------------------------------------------
// Ask the data
// ---------------------------------------------------------------------
async function runAsk(query) {
  const q = (query ?? $("askInput").value).trim();
  if (!q) return;
  $("askInput").value = q;
  $("askBtn").disabled = true;
  $("askBtn").textContent = "Thinking…";
  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q, pct_single: state.pctSingle, pct_pays: state.pctPays, capture_y3: state.captureY3 }),
    });
    const data = await res.json();
    $("answerEyebrow").textContent = data.via === "openai" ? "Anaphora AI · answer (generated)" : "Anaphora AI · answer";
    $("answerHeadline").textContent = data.headline;
    $("answerText").textContent = data.body;
    $("answerSource").textContent = data.source || "";
    $("answerCard").classList.remove("hidden");
  } catch (e) {
    $("answerHeadline").textContent = "Something went wrong reaching the data assistant.";
    $("answerText").textContent = String(e);
    $("answerSource").textContent = "";
    $("answerCard").classList.remove("hidden");
  } finally {
    $("askBtn").disabled = false;
    $("askBtn").textContent = "Ask";
  }
}

$("askBtn").addEventListener("click", () => runAsk());
$("askInput").addEventListener("keydown", (e) => { if (e.key === "Enter") runAsk(); });
document.querySelectorAll(".chip").forEach(chip => chip.addEventListener("click", () => runAsk(chip.dataset.q)));
$("answerClose").addEventListener("click", () => $("answerCard").classList.add("hidden"));

// ---------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------
(async function init() {
  initSliders();
  await Promise.all([
    renderKpis(),
    renderTamSom(),
    renderWhyNow(),
    renderIncumbents(),
    renderTrend(),
    renderGrowth(),
    renderProductFunnel(),
    renderScoreChart(),
  ]);
})();
