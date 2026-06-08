let revenueChart = null;
let energyChart = null;

async function loadReports() {
  const analytics = await (await fetch("/api/analytics")).json();

  document.getElementById("revenue").innerText =
    "Rs " + Math.round(analytics.total_bill_amount).toLocaleString();

  document.getElementById("consumed").innerText =
    Math.round(analytics.total_energy_consumed).toLocaleString() + " kWh";

  document.getElementById("generated").innerText =
    Math.round(analytics.total_energy_generated).toLocaleString() + " kWh";

  document.getElementById("performance").innerText =
    analytics.energy_efficiency.toFixed(2) + "%";

  if (energyChart) energyChart.destroy();

  energyChart = new Chart(document.getElementById("energyChart"), {
    type: "bar",

    data: {
      labels: ["House", "School", "Office"],

      datasets: [
        {
          label: "Energy Consumption",

          data: [
            analytics.house_consumption,
            analytics.school_consumption,
            analytics.office_consumption,
          ],

          backgroundColor: ["#3b82f6", "#22c55e", "#f59e0b"],
        },
      ],
    },
  });

  if (revenueChart) revenueChart.destroy();

  revenueChart = new Chart(document.getElementById("revenueChart"), {
    type: "radar",

    data: {
      labels: ["Revenue", "Efficiency", "Health Score", "Carbon Saved"],

      datasets: [
        {
          label: "System Performance",

          data: [
            analytics.total_bill_amount / 10000,
            analytics.energy_efficiency,
            analytics.health_score,
            analytics.carbon_saved / 10000,
          ],
        },
      ],
    },
  });
}

loadReports();
