let predictionTrendChart = null;
let riskDistributionChart = null;
let forecastChart = null;
let consumptionChart = null;
let marketplaceTrendChart = null;

const api = {
  dashboard: "/api/ai/dashboard",
  forecast: "/api/ai/forecast",
  history: "/api/ai/history",
  model: "/api/ai/model",
  statistics: "/api/ai/statistics",
  anomalies: "/api/ai/anomalies",
  recommendations: "/api/ai/recommendations",
  alerts: "/api/ai/alerts",
  run: "/api/ai/run",
};

const toastContainer = document.getElementById("toastContainer");
const skeletonOverlay = document.getElementById("aiSkeletonLoader");
const runButton = document.getElementById("runAnalysisBtn");
const refreshRecommendationsBtn = document.getElementById("refreshRecommendationsBtn");

function createToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `marketplace-toast marketplace-toast--${type}`;
  toast.innerHTML = `
    <div class="marketplace-toast__icon"><i class="bi bi-${type === "success" ? "check-circle" : type === "warning" ? "exclamation-triangle" : "x-circle"}"></i></div>
    <div>
      <p class="marketplace-toast__title">${type === "success" ? "Success" : type === "warning" ? "Warning" : "Error"}</p>
      <p class="marketplace-toast__message">${message}</p>
    </div>
  `;

  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.classList.add("marketplace-toast--hide");
    setTimeout(() => toast.remove(), 400);
  }, 3600);
}

function formattedNumber(value) {
  return typeof value === "number" ? value.toLocaleString() : value;
}

function badgeClassForRisk(value) {
  const normalized = String(value || "").toUpperCase();
  if (normalized === "CRITICAL" || normalized === "HIGH") return "ai-badge--critical";
  if (normalized === "MEDIUM") return "ai-badge--warning";
  return "ai-badge--normal";
}

function badgeClassForSeverity(value) {
  const normalized = String(value || "").toUpperCase();
  if (normalized === "CRITICAL") return "ai-badge--critical";
  if (normalized === "HIGH") return "ai-badge--warning";
  if (normalized === "MEDIUM") return "ai-badge--amber";
  return "ai-badge--low";
}

function animateValue(element, endValue, suffix = "") {
  if (!element) return;
  const startValue = Number(element.dataset.start || 0);
  const target = Number(endValue) || 0;
  const duration = 700;
  const startTime = performance.now();

  function step(currentTime) {
    const progress = Math.min((currentTime - startTime) / duration, 1);
    const value = Math.floor(startValue + (target - startValue) * progress);
    element.textContent = `${formattedNumber(value)}${suffix}`;
    if (progress < 1) requestAnimationFrame(step);
    else element.dataset.start = target;
  }

  requestAnimationFrame(step);
}

function configureMetric(elementId, value, suffix = "") {
  const element = document.getElementById(elementId);
  if (!element) return;
  element.dataset.start = Number(element.dataset.start || 0);
  animateValue(element, value, suffix);
}

function buildDecisionSummary(data) {
  const prediction = document.getElementById("decisionPrediction");
  const confidenceBar = document.getElementById("decisionConfidenceBar");
  const confidenceText = document.getElementById("decisionConfidence");
  const status = document.getElementById("decisionStatus");
  const action = document.getElementById("decisionAction");
  const riskBadge = document.getElementById("decisionRisk");

  const riskValue = (data.risk_level || "LOW").toUpperCase();
  const systemValue = data.system_status || "Active";
  const confidenceValue = Math.round(data.prediction_confidence || 0);
  const predictionText = data.recommendation || "Maintain current energy strategy";
  const actionText = data.suggested_action || data.recommendation || "Monitor system status";

  prediction.textContent = predictionText;
  confidenceBar.style.width = `${Math.min(Math.max(confidenceValue, 0), 100)}%`;
  confidenceText.textContent = `${confidenceValue}%`;
  status.textContent = systemValue;
  status.className = `ai-badge ${systemValue.toUpperCase().includes("WARN") ? "ai-badge--warning" : systemValue.toUpperCase().includes("ACTIVE") ? "ai-badge--green" : badgeClassForRisk(riskValue)}`;
  action.textContent = actionText;
  riskBadge.textContent = riskValue;
  riskBadge.className = `ai-decision-card__pill ${badgeClassForRisk(riskValue)}`;
}

function buildForecastCards(forecast) {
  const nextHour = forecast.next_hour_prediction;
  const nextDay = forecast.next_day_prediction;
  const nextWeek = forecast.next_week_prediction;
  const peakHour = forecast.peak_hour;
  const lowestHour = forecast.lowest_demand_hour;

  document.getElementById("forecastNextHour").textContent = nextHour != null ? `${formattedNumber(nextHour)} kWh` : "--";
  document.getElementById("forecastToday").textContent = nextDay != null ? `${formattedNumber(nextDay)} kWh` : "--";
  document.getElementById("forecastWeek").textContent = nextWeek != null ? `${formattedNumber(nextWeek)} kWh` : "--";
  document.getElementById("forecastPeakHour").textContent = peakHour != null ? `${String(peakHour).padStart(2, "0")}:00` : "--";
  document.getElementById("forecastLowestHour").textContent = lowestHour != null ? `${String(lowestHour).padStart(2, "0")}:00` : "--";
}

function buildRecommendationCards(items, confidence) {
  const container = document.getElementById("recommendationsGrid");
  container.innerHTML = "";

  if (!items || !items.length) {
    container.innerHTML = `<div class="marketplace-empty-state"><div class="marketplace-empty-state__icon"><i class="bi bi-lightbulb"></i></div><p class="marketplace-empty-state__title">No active recommendations</p><p class="marketplace-empty-state__text">The AI system is running smoothly right now.</p></div>`;
    return;
  }

  const iconMap = {
    possible_grid_overload: "bi-exclamation-octagon-fill",
    reduce_consumption: "bi-fire",
    sell_excess_energy: "bi-stack",
    buy_additional_energy: "bi-cart-plus-fill",
    solar_generation_low: "bi-sun",
    store_battery_energy: "bi-battery-half",
    high_marketplace_prices: "bi-currency-dollar",
    low_marketplace_prices: "bi-currency-exchange",
    monitor_demand_trend: "bi-graph-up",
    investigate_anomalies: "bi-search",
    maintain_operations: "bi-check-circle-fill",
  };

  items.slice(0, 6).forEach((item) => {
    const iconClass = iconMap[item.type] || "bi-lightning-charge";
    const badge = item.priority || "LOW";
    const badgeState = badgeClassForSeverity(badge);
    const confidenceText = confidence ? `${Math.round(confidence)}%` : "--";
    const titleText = item.type ? item.type.replace(/_/g, " ") : "Recommendation";

    const card = document.createElement("article");
    card.className = "ai-recommendation-card";
    card.innerHTML = `
      <div class="ai-recommendation-card__header">
        <div class="ai-recommendation-card__icon"><i class="bi ${iconClass}"></i></div>
        <span class="ai-badge ${badgeState}">${badge}</span>
      </div>
      <h3 class="ai-recommendation-card__title">${titleText}</h3>
      <p class="ai-recommendation-card__text">${item.message}</p>
      <div class="ai-recommendation-card__footer">
        <span class="ai-recommendation-card__confidence">Confidence ${confidenceText}</span>
        <span class="ai-recommendation-card__tag">${titleText}</span>
      </div>
    `;
    container.appendChild(card);
  });
}

function buildModelPanel(modelData) {
  document.getElementById("modelAlgorithm").textContent = modelData.algorithm || "-";
  document.getElementById("modelVersion").textContent = modelData.model_version || modelData.model_version || "-";
  document.getElementById("modelAccuracy").textContent = `${formattedNumber(modelData.accuracy)}%`;
  document.getElementById("modelSamples").textContent = formattedNumber(modelData.training_samples || modelData.feature_count || "-");
  const trainingDate = modelData.last_training_time || modelData.training_date || "-";
  document.getElementById("modelTrainingDate").textContent = trainingDate;
  document.getElementById("modelLastUpdated").textContent = trainingDate;
  document.getElementById("modelStatus").textContent = modelData.model_status || "-";
}

function buildAlertsTable(alerts) {
  const body = document.getElementById("alertsTableBody");
  body.innerHTML = "";
  if (!alerts || !alerts.length) {
    body.innerHTML = `<tr class="marketplace-table-row"><td colspan="5" class="marketplace-table-empty">No alerts reported yet.</td></tr>`;
    return;
  }

  alerts.slice(0, 12).forEach((alert) => {
    const badgeClass = badgeClassForSeverity(alert.severity || alert.risk_level);
    body.insertAdjacentHTML("beforeend", `
      <tr class="marketplace-table-row">
        <td>${alert.timestamp || "-"}</td>
        <td>${alert.username || alert.user || "SYSTEM"}</td>
        <td><span class="ai-badge ${badgeClass}">${(alert.severity || alert.risk_level || "LOW").toUpperCase()}</span></td>
        <td>${formattedNumber(alert.confidence || 0)}%</td>
        <td>${alert.reason || "No reason provided"}</td>
      </tr>
    `);
  });
}

function buildHistoryTable(records) {
  const body = document.getElementById("historyTableBody");
  body.innerHTML = "";
  if (!records || !records.length) {
    body.innerHTML = `<tr class="marketplace-table-row"><td colspan="7" class="marketplace-table-empty">Prediction history is empty.</td></tr>`;
    return;
  }

  records.forEach((record) => {
    const badgeClass = badgeClassForRisk(record.risk_level || "LOW");
    body.insertAdjacentHTML("beforeend", `
      <tr class="marketplace-table-row">
        <td>${record.timestamp || "-"}</td>
        <td>${formattedNumber(record.prediction || record.prediction_value || 0)}</td>
        <td>${formattedNumber(record.confidence || 0)}%</td>
        <td><span class="ai-badge ${badgeClass}">${(record.risk_level || "LOW").toUpperCase()}</span></td>
        <td>${record.recommendation || "-"}</td>
        <td>${record.model_version || "-"}</td>
        <td>${record.risk_level ? record.risk_level.toUpperCase() : "-"}</td>
      </tr>
    `);
  });
}

function buildCharts(dashboard, statistics, forecast, alerts, history) {
  let labels = history?.slice(0, 10).reverse().map((item) => item.timestamp || "-") || [];
  let predictionValues = history?.slice(0, 10).reverse().map((item) => Number(item.prediction || 0)) || [];
  let confidenceValues = history?.slice(0, 10).reverse().map((item) => Number(item.confidence || 0)) || [];

  if (!labels.length) {
    labels = ["No history available"];
    predictionValues = [0];
    confidenceValues = [0];
  }

  if (predictionTrendChart) predictionTrendChart.destroy();
  predictionTrendChart = new Chart(document.getElementById("predictionTrendChart"), {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Prediction",
          data: predictionValues,
          borderColor: "#38bdf8",
          backgroundColor: "rgba(56, 189, 248, 0.15)",
          tension: 0.32,
          pointRadius: 4,
        },
        {
          label: "Confidence",
          data: confidenceValues,
          borderColor: "#22c55e",
          backgroundColor: "rgba(34, 197, 94, 0.14)",
          tension: 0.32,
          pointRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: "#cbd5e1" } } },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.06)" } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.06)" } },
      },
    },
  });

  if (riskDistributionChart) riskDistributionChart.destroy();
  const severity = statistics?.alerts_by_severity || {};
  riskDistributionChart = new Chart(document.getElementById("riskDistributionChart"), {
    type: "doughnut",
    data: {
      labels: ["Low", "Medium", "High", "Critical"],
      datasets: [{
        data: [severity.LOW || 0, severity.MEDIUM || 0, severity.HIGH || 0, severity.CRITICAL || 0],
        backgroundColor: ["#22c55e", "#fbbf24", "#f97316", "#ef4444"],
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "bottom", labels: { color: "#cbd5e1" } } },
    },
  });

  if (forecastChart) forecastChart.destroy();
  const forecastLabels = ["Next Hour", "Today", "This Week"];
  const forecastData = [forecast.next_hour_prediction || 0, forecast.next_day_prediction || 0, forecast.next_week_prediction || 0];
  forecastChart = new Chart(document.getElementById("forecastChart"), {
    type: "bar",
    data: {
      labels: forecastLabels,
      datasets: [{
        label: "kWh",
        data: forecastData,
        backgroundColor: ["#38bdf8", "#22c55e", "#7c3aed"],
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.06)" } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.06)" } },
      },
    },
  });

  if (consumptionChart) consumptionChart.destroy();
  consumptionChart = new Chart(document.getElementById("consumptionChart"), {
    type: "line",
    data: {
      labels: ["Current", "Predicted"],
      datasets: [{
        label: "Demand",
        data: [dashboard.current_demand || 0, dashboard.predicted_demand || 0],
        borderColor: "#f97316",
        backgroundColor: "rgba(249, 115, 22, 0.16)",
        tension: 0.35,
        pointRadius: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.06)" } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.06)" } },
      },
    },
  });

  if (marketplaceTrendChart) marketplaceTrendChart.destroy();
  const demandLabels = ["Current Demand", "Predicted Demand", "Next Hour"];
  const demandData = [dashboard.current_demand || 0, dashboard.predicted_demand || 0, forecast.next_hour_prediction || 0];
  marketplaceTrendChart = new Chart(document.getElementById("marketplaceTrendChart"), {
    type: "bar",
    data: {
      labels: demandLabels,
      datasets: [{
        label: "kWh",
        data: demandData,
        backgroundColor: ["#38bdf8", "#22c55e", "#8b5cf6"],
        borderRadius: 12,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (context) => `${context.dataset.label}: ${formattedNumber(context.parsed.y)} kWh` } },
      },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.06)" } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.06)" } },
      },
    },
  });
}

function updateSummary(dashboard, statistics, recommendations) {
  configureMetric("summaryTotalPredictions", statistics.total_predictions || 0);
  configureMetric("summaryCriticalAlerts", statistics.critical_alerts || 0);
  configureMetric("summaryRecommendations", recommendations.length || 0);
  configureMetric("summaryModelAccuracy", dashboard.ai_accuracy || 0, "%");
  buildDecisionSummary(dashboard);
}

function setLoading(active) {
  if (runButton) runButton.disabled = active;
  if (refreshRecommendationsBtn) refreshRecommendationsBtn.disabled = active;
  if (skeletonOverlay) {
    skeletonOverlay.style.display = active ? "grid" : "none";
  }
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`${response.status}: ${errorText}`);
  }
  return response.json();
}

async function loadAiData() {
  setLoading(true);
  try {
    const [dashboard, forecast, history, model, statistics, anomalies, recommendations, alerts] = await Promise.all([
      fetchJson(api.dashboard),
      fetchJson(api.forecast),
      fetchJson(api.history),
      fetchJson(api.model),
      fetchJson(api.statistics),
      fetchJson(api.anomalies),
      fetchJson(api.recommendations),
      fetchJson(api.alerts),
    ]);

    updateSummary(dashboard, statistics, recommendations);
    buildForecastCards(forecast);
    buildRecommendationCards(recommendations, dashboard.prediction_confidence || 0);
    buildModelPanel(model);
    buildAlertsTable(alerts);
    buildHistoryTable(history);
    buildCharts(dashboard, statistics, forecast, alerts, history);
    createToast("AI dashboard refreshed successfully", "success");
  } catch (error) {
    console.error(error);
    createToast("Unable to load AI monitoring data", "error");
  } finally {
    setLoading(false);
  }
}

async function runAnalysis() {
  setLoading(true);
  runButton.innerHTML = `<i class="bi bi-hourglass-split"></i> Running...`;
  try {
    const result = await fetchJson(api.run, { method: "POST" });
    createToast(`Analysis completed. ${result.alerts_created || 0} alert(s) updated.`, "success");
    await loadAiData();
  } catch (error) {
    console.error(error);
    createToast("AI analysis request failed", "error");
  } finally {
    runButton.innerHTML = `<i class="bi bi-play-circle"></i><span>Run AI Analysis</span>`;
    setLoading(false);
  }
}

if (runButton) {
  runButton.addEventListener("click", runAnalysis);
}
if (refreshRecommendationsBtn) {
  refreshRecommendationsBtn.addEventListener("click", loadAiData);
}

window.addEventListener("load", loadAiData);
