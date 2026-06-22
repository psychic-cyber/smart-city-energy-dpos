let predictionChart = null;
let anomalyChart = null;

async function loadAI() {
  const aiData = await (await fetch("/api/ai-monitoring")).json();

  const anomalies = aiData.anomalies;

  const anomalyRate = aiData.anomaly_rate;

  const healthScore = aiData.accuracy;

  const efficiency = aiData.confidence;

  const totalTransactions = aiData.total_records;

  const riskElement = document.getElementById("riskLevel");

  riskElement.innerText = aiData.risk_level;

  if (aiData.risk_level === "LOW") {
    riskElement.style.color = "#22c55e";
  } else if (aiData.risk_level === "MEDIUM") {
    riskElement.style.color = "#f59e0b";
  } else {
    riskElement.style.color = "#ef4444";
  }

  document.getElementById("anomalies").innerText = anomalies.toLocaleString();

  document.getElementById("aiAccuracy").innerText =
    healthScore.toFixed(2) + "%";

  document.getElementById("confidence").innerText = efficiency.toFixed(2) + "%";

  document.getElementById("systemStatus").innerText =
    healthScore >= 90 ? "ACTIVE" : "WARNING";

  document.getElementById("aiInsight").innerHTML = `
    <div class="metric-highlight">
      ${anomalies}
    </div>

    <div class="metric-sub">
      Active AI Alerts
    </div>
    `;

  document.getElementById("recommendation").innerHTML = `
    <div class="metric-highlight">
      ${aiData.recommendation}
    </div>
    `;

  document.getElementById("actionPlan").innerHTML = `
    <div class="metric-highlight">
      NO ACTION
    </div>
    <div class="metric-sub">
      REQUIRED
    </div>
    `;

  if (predictionChart) predictionChart.destroy();

  predictionChart = new Chart(document.getElementById("predictionChart"), {
    type: "bar",

    data: {
      labels: ["Health Score", "Energy Efficiency", "Anomaly Rate"],

      datasets: [
        {
          label: "AI Metrics",

          data: [healthScore, efficiency, anomalyRate],

          backgroundColor: ["#22c55e", "#3b82f6", "#ef4444"],
        },
      ],
    },
  });

  if (anomalyChart) anomalyChart.destroy();

  anomalyChart = new Chart(document.getElementById("anomalyChart"), {
    type: "doughnut",

    data: {
      labels: ["Normal Records", "Anomalies"],

      datasets: [
        {
          data: [totalTransactions - anomalies, anomalies],

          backgroundColor: ["#22c55e", "#ef4444"],
        },
      ],
    },
  });

  // AI ALERTS

  try {
    const alerts = await (await fetch("/api/ai-alerts")).json();

    const table = document.getElementById("aiAlertsTable");

    if (table) {
      table.innerHTML = "";

      alerts.forEach((a) => {
        table.innerHTML += `
          <tr>
            <td>${a.username}</td>
            <td>${a.generated} kWh</td>
            <td>${a.consumed} kWh</td>
            <td>
              <span class="badge bg-danger">
                ${a.risk_level}
              </span>
            </td>
            <td>${a.reason}</td>
          </tr>
          `;
      });
    }
  } catch (error) {
    console.error("AI Alerts Error:", error);
  }
}

loadAI();
