async function loadReports() {
  const response = await fetch("/api/analytics");
  const analytics = await response.json();

  const consumed = Number(analytics.total_energy_consumed);

  const generated = Number(analytics.total_energy_generated);

  const revenue = Number(analytics.total_bill_amount);

  document.getElementById("revenue").innerText =
    "Rs " + revenue.toLocaleString();

  document.getElementById("consumed").innerText =
    consumed.toLocaleString() + " kWh";

  document.getElementById("generated").innerText =
    generated.toLocaleString() + " kWh";

  const performance = consumed > 0 ? (generated / consumed) * 100 : 0;

  document.getElementById("performance").innerText =
    performance.toFixed(1) + "%";

  new Chart(document.getElementById("energyChart"), {
    type: "bar",

    data: {
      labels: ["Consumed", "Generated"],

      datasets: [
        {
          label: "Energy (kWh)",

          data: [consumed, generated],
        },
      ],
    },
  });

  new Chart(document.getElementById("revenueChart"), {
    type: "doughnut",

    data: {
      labels: ["Revenue"],

      datasets: [
        {
          data: [revenue],
        },
      ],
    },
  });
}

loadReports();
