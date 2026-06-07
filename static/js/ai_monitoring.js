async function loadAI() {
  const response = await fetch("/api/analytics");

  const analytics = await response.json();

  const anomalies = Number(analytics.anomalies_detected);

  const totalRecords = 10001;

  const anomalyRate = (anomalies / totalRecords) * 100;

  const accuracy = 100 - anomalyRate;

  const confidence = accuracy - 2;

  document.getElementById("anomalies").innerText = anomalies;

  document.getElementById("aiAccuracy").innerText = accuracy.toFixed(2) + "%";

  document.getElementById("confidence").innerText = confidence.toFixed(2) + "%";

  document.getElementById("systemStatus").innerText =
    accuracy > 90 ? "ACTIVE" : "WARNING";

  new Chart(document.getElementById("predictionChart"), {
    type: "bar",

    data: {
      labels: ["Accuracy", "Confidence"],

      datasets: [
        {
          label: "AI Performance",

          data: [accuracy, confidence],
        },
      ],
    },
  });

  new Chart(document.getElementById("anomalyChart"), {
    type: "doughnut",

    data: {
      labels: ["Anomalies", "Normal Records"],

      datasets: [
        {
          data: [anomalies, totalRecords - anomalies],
        },
      ],
    },
  });
}

loadAI();
