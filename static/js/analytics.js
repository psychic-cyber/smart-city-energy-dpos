let districtChart = null;
let entityChart = null;

async function loadAnalytics() {
  const analytics = await (await fetch("/api/analytics")).json();

  const districts = await (await fetch("/api/districts")).json();

  const districtLabels = districts.map((d) => d._id);

  const districtEnergy = districts.map((d) => Math.round(d.energy));

  if (districtChart) districtChart.destroy();

  districtChart = new Chart(document.getElementById("districtChart"), {
    type: "bar",

    data: {
      labels: districtLabels,

      datasets: [
        {
          label: "Energy Consumption (kWh)",

          data: districtEnergy,

          backgroundColor: [
            "#3b82f6",
            "#22c55e",
            "#f59e0b",
            "#ef4444",
            "#8b5cf6",
          ],
        },
      ],
    },
  });

  const entityLabels = Object.keys(analytics.entity_distribution);

  const entityValues = Object.values(analytics.entity_distribution);

  if (entityChart) entityChart.destroy();

  entityChart = new Chart(document.getElementById("entityChart"), {
    type: "doughnut",

    data: {
      labels: entityLabels,

      datasets: [
        {
          data: entityValues,
        },
      ],
    },
  });

  document.getElementById("totalEnergy").innerText =
    Math.round(
      analytics.total_energy_generated + analytics.total_energy_consumed,
    ).toLocaleString() + " kWh";

  document.getElementById("totalRevenue").innerText =
    "Rs " + Math.round(analytics.total_bill_amount).toLocaleString();

  document.getElementById("efficiencyRate").innerText =
    (
      (analytics.total_energy_consumed / analytics.total_energy_generated) *
      100
    ).toFixed(1) + "%";

  document.getElementById("entityCount").innerText = districts.length;
}

loadAnalytics();
