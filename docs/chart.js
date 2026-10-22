const canvas = document.querySelector("#rate-chart");
const context = canvas.getContext("2d");
const status = document.querySelector("#chart-status");
const formatter = new Intl.NumberFormat("ja-JP", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 4,
});

function formatDate(value) {
  return new Intl.DateTimeFormat("ja-JP", {
    year: "numeric",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

function drawChart(rows) {
  const ratio = window.devicePixelRatio || 1;
  const bounds = canvas.getBoundingClientRect();
  canvas.width = Math.round(bounds.width * ratio);
  canvas.height = Math.round(bounds.height * ratio);
  context.setTransform(ratio, 0, 0, ratio, 0, 0);

  const width = bounds.width;
  const height = bounds.height;
  const pad = { top: 18, right: 18, bottom: 42, left: 58 };
  const values = rows.map((row) => row.usd_jpy);
  const low = Math.min(...values);
  const high = Math.max(...values);
  const spread = high - low || high * 0.01 || 1;
  const min = low - spread * 0.12;
  const max = high + spread * 0.12;
  const plotWidth = width - pad.left - pad.right;
  const plotHeight = height - pad.top - pad.bottom;

  context.clearRect(0, 0, width, height);
  context.font = "12px -apple-system, BlinkMacSystemFont, sans-serif";
  context.textAlign = "right";
  context.textBaseline = "middle";

  for (let step = 0; step <= 4; step += 1) {
    const value = max - ((max - min) * step) / 4;
    const y = pad.top + (plotHeight * step) / 4;
    context.strokeStyle = "#e9eef5";
    context.lineWidth = 1;
    context.beginPath();
    context.moveTo(pad.left, y);
    context.lineTo(width - pad.right, y);
    context.stroke();
    context.fillStyle = "#718096";
    context.fillText(formatter.format(value), pad.left - 10, y);
  }

  const xAt = (index) => pad.left + (index / Math.max(rows.length - 1, 1)) * plotWidth;
  const yAt = (value) => pad.top + ((max - value) / (max - min)) * plotHeight;

  const fill = context.createLinearGradient(0, pad.top, 0, height - pad.bottom);
  fill.addColorStop(0, "rgb(37 99 235 / 18%)");
  fill.addColorStop(1, "rgb(37 99 235 / 0%)");
  context.beginPath();
  rows.forEach((row, index) => {
    const x = xAt(index);
    const y = yAt(row.usd_jpy);
    if (index === 0) context.moveTo(x, y);
    else context.lineTo(x, y);
  });
  context.lineTo(xAt(rows.length - 1), height - pad.bottom);
  context.lineTo(xAt(0), height - pad.bottom);
  context.closePath();
  context.fillStyle = fill;
  context.fill();

  context.beginPath();
  rows.forEach((row, index) => {
    const x = xAt(index);
    const y = yAt(row.usd_jpy);
    if (index === 0) context.moveTo(x, y);
    else context.lineTo(x, y);
  });
  context.strokeStyle = "#2563eb";
  context.lineWidth = 2.5;
  context.lineJoin = "round";
  context.lineCap = "round";
  context.stroke();

  const last = rows.at(-1);
  context.beginPath();
  context.arc(xAt(rows.length - 1), yAt(last.usd_jpy), 4, 0, Math.PI * 2);
  context.fillStyle = "#2563eb";
  context.fill();

  const labels = [0, Math.floor((rows.length - 1) / 2), rows.length - 1];
  context.fillStyle = "#718096";
  context.textAlign = "center";
  context.textBaseline = "top";
  labels.forEach((index) => {
    context.fillText(formatDate(rows[index].date), xAt(index), height - pad.bottom + 14);
  });
}

async function loadRates() {
  try {
    const response = await fetch("data/usd-jpy.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`データ取得に失敗しました (${response.status})`);
    const rows = await response.json();
    if (!Array.isArray(rows) || rows.length === 0) {
      status.textContent = "まだデータがありません。GitHub Actions のワークフローを実行してください。";
      return;
    }
    const latest = rows.at(-1);
    document.querySelector("#latest-rate").textContent = formatter.format(latest.usd_jpy);
    document.querySelector("#latest-date").textContent = formatDate(latest.date);
    document.querySelector("#record-count").textContent = `${rows.length} 件`;
    drawChart(rows);
    status.textContent = `${formatDate(rows[0].date)} から ${formatDate(latest.date)} まで`;
  } catch (error) {
    status.textContent = error.message;
  }
}

loadRates();
window.addEventListener("resize", () => {
  fetch("data/usd-jpy.json", { cache: "no-store" })
    .then((response) => response.json())
    .then((rows) => {
      if (rows.length) drawChart(rows);
    });
});
