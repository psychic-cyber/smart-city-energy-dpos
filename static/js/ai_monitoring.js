let predictionChart = null;
let anomalyChart = null;

async function loadAI() {
  const analytics = await (await fetch("/api/analytics")).json();

  const totalTransactions = analytics.total_transactions;
  const anomalies = analytics.anomalies_detected;

  const anomalyRate = analytics.anomaly_percentage;
  const healthScore = analytics.health_score;
  const efficiency = analytics.energy_efficiency;

  document.getElementById("anomalies").innerText = anomalies.toLocaleString();

  document.getElementById("aiAccuracy").innerText =
    healthScore.toFixed(2) + "%";

  document.getElementById("confidence").innerText = efficiency.toFixed(2) + "%";

  document.getElementById("systemStatus").innerText =
    healthScore >= 90 ? "ACTIVE" : "WARNING";

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
