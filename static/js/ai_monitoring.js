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

  document.getElementById("aiInsight").innerHTML =
    `<div class="metric-highlight">
        ${anomalies} DETECTED
    </div>`;

  document.getElementById("recommendation").innerHTML =
    `<div class="metric-highlight">
      MONITOR
    </div>`;

  document.getElementById("actionPlan").innerHTML =
    `<div class="metric-highlight">
      ACTIVE
    </div>`;

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
        },
      ],
    },
  });
}

loadAI();
