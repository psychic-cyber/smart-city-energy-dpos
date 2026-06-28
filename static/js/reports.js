let revenueChart = null;
let energyChart = null;

async function loadReport(type = "monthly") {
  const report = await (await fetch(`/api/report/${type}`)).json();

  document.getElementById("revenue").innerText =
    "Rs " + report.revenue.toLocaleString();

  document.getElementById("generated").innerText = report.generated + " kWh";

  document.getElementById("consumed").innerText = report.consumed + " kWh";

  document.getElementById("performance").innerText = report.efficiency + "%";

  document.getElementById("co2").innerText = report.co2_saved + " kg";

  document.getElementById("transactions").innerText = report.transactions;

  document.getElementById("producerTable").innerHTML = "";

  report.top_producers.forEach((p) => {
    document.getElementById("producerTable").innerHTML += `
      <tr>
        <td>${p.username}</td>
        <td>${p.role}</td>
        <td>${p.energy_generated}</td>
      </tr>
      `;
  });

  document.getElementById("consumerTable").innerHTML = "";

  report.top_consumers.forEach((p) => {
    document.getElementById("consumerTable").innerHTML += `
      <tr>
        <td>${p.username}</td>
        <td>${p.role}</td>
        <td>${p.energy_consumed}</td>
      </tr>
      `;
  });

  const marketplaceTable = document.getElementById("marketplaceReportTable");
  marketplaceTable.innerHTML = "";
  const marketplaceTransactions = report.marketplace_transactions || [];
  if (!marketplaceTransactions.length) {
    marketplaceTable.innerHTML = '<tr><td colspan="8" class="text-center text-secondary">No marketplace purchases in this period</td></tr>';
  } else {
    marketplaceTransactions.forEach((transaction) => {
      marketplaceTable.innerHTML += `
        <tr>
          <td>${transaction.seller}</td>
          <td>${transaction.buyer}</td>
          <td>${transaction.original_listing_amount} kWh</td>
          <td>${transaction.purchased_amount} kWh</td>
          <td>${transaction.remaining_amount} kWh</td>
          <td>Rs ${transaction.price_per_kwh}</td>
          <td>Rs ${transaction.total_amount}</td>
          <td>${transaction.timestamp}</td>
        </tr>`;
    });
  }

  if (revenueChart) revenueChart.destroy();

  revenueChart = new Chart(document.getElementById("revenueChart"), {
    type: "doughnut",

    data: {
      labels: ["Revenue", "Generated", "Consumed"],

      datasets: [
        {
          data: [report.revenue, report.generated, report.consumed],
        },
      ],
    },
  });

  if (energyChart) energyChart.destroy();

  energyChart = new Chart(document.getElementById("energyChart"), {
    type: "bar",

    data: {
      labels: report.top_producers.map((p) => p.username),

      datasets: [
        {
          label: "Energy Generated",

          data: report.top_producers.map((p) => p.energy_generated),
        },
      ],
    },
  });
}

loadReport("monthly");
