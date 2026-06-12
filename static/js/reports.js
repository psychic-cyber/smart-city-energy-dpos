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

  const districts = await (await fetch("/api/districts")).json();

  energyChart = new Chart(document.getElementById("energyChart"), {
    type: "bar",

    data: {
      labels: districts.map((d) => d._id),

      datasets: [
        {
          label: "Energy Consumption (kWh)",

          data: districts.map((d) => Math.round(d.energy)),

          backgroundColor: "#38bdf8",
        },
      ],
    },
  });

  if (revenueChart) revenueChart.destroy();

  revenueChart = new Chart(document.getElementById("revenueChart"), {
    type: "doughnut",

    data: {
      labels: ["Revenue", "Energy Consumed", "Energy Generated"],

      datasets: [
        {
          label: "System Performance",

          data: [
            analytics.total_bill_amount,
            analytics.total_energy_consumed,
            analytics.total_energy_generated
          ],
        },
      ],
    },
  });
}

loadReports();
