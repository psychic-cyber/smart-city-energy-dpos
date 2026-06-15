let predictionChart = null;
let anomalyChart = null;

async function loadAI() {
  const aiData = await (await fetch("/api/ai-monitoring")).json();

  const anomalies = aiData.anomalies;

  const anomalyRate = aiData.anomaly_rate;

  const healthScore = aiData.accuracy;

  const efficiency = aiData.confidence;

  const totalTransactions = aiData.total_records;

  document.getElementById("anomalies").innerText = anomalies.toLocaleString();

  document.getElementById("aiAccuracy").innerText =
    healthScore.toFixed(2) + "%";

  document.getElementById("confidence").innerText = efficiency.toFixed(2) + "%";

  document.getElementById("systemStatus").innerText =
    healthScore >= 90 ? "ACTIVE" : "WARNING";

  document.getElementById("riskLevel").innerText = aiData.risk_level;

  document.getElementById("aiInsight").innerText = aiData.insight;

  document.getElementById("recommendation").innerText = aiData.recommendation;

  document.getElementById("actionPlan").innerText = aiData.action;

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
