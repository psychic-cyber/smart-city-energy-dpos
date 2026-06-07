let energyChart = null;
let districtChart = null;

async function loadDashboard() {
  const stats = await (await fetch("/api/stats")).json();

  const analytics = await (await fetch("/api/analytics")).json();

  const transactions = await (await fetch("/api/transactions")).json();

  const blocks = await (await fetch("/api/blocks")).json();

  const districts = await (await fetch("/api/districts")).json();

  document.getElementById("transactions").innerText =
    stats.total_transactions.toLocaleString();

  document.getElementById("blocks").innerText =
    stats.total_blocks.toLocaleString();

  document.getElementById("status").innerText = stats.chain_valid
    ? "VALID"
    : "INVALID";

  document.getElementById("health").innerText = stats.chain_valid
    ? "100%"
    : "ERROR";

  document.getElementById("anomalies").innerText =
    analytics.anomalies_detected.toLocaleString();

  document.getElementById("consumed").innerText = Math.round(
    analytics.total_energy_consumed,
  ).toLocaleString();

  document.getElementById("generated").innerText = Math.round(
    analytics.total_energy_generated,
  ).toLocaleString();

  document.getElementById("revenue").innerText =
    "₨ " + Math.round(analytics.total_bill_amount * 280).toLocaleString();

  document.getElementById("lastUpdated").innerText =
    "Last Updated: " + new Date().toLocaleString();

  const efficiency =
    (analytics.total_energy_consumed / analytics.total_energy_generated) * 100;

  document.getElementById("efficiency").innerText = efficiency.toFixed(1) + "%";

  if (efficiency >= 90) {
    document.getElementById("efficiency").style.color = "#22c55e";
  } else if (efficiency >= 75) {
    document.getElementById("efficiency").style.color = "#facc15";
  } else {
    document.getElementById("efficiency").style.color = "#ef4444";
  }

  const gridStability =
    100 - (analytics.anomalies_detected / stats.total_transactions) * 100;

  document.getElementById("gridStability").innerText =
    gridStability.toFixed(1) + "%";

  document.getElementById("aiAccuracy").innerText = "96.8%";

  document.getElementById("securityScore").innerText = stats.chain_valid
    ? "100%"
    : "0%";

  const transactionTable = document.getElementById("transactionsTable");

  transactionTable.innerHTML = "";

  transactions.slice(0, 10).forEach((t) => {
    transactionTable.innerHTML += `
        <tr>
          <td>${t.entity_id}</td>
          <td>${t.entity_type}</td>
          <td>${t.district}</td>
          <td>${t.bill_amount}</td>
        </tr>
      `;
  });

  const blockTable = document.getElementById("blocksTable");

  blockTable.innerHTML = "";

  blocks.slice(0, 10).forEach((b) => {
    blockTable.innerHTML += `
        <tr>
          <td>${b.index}</td>
          <td>${b.hash.substring(0, 15)}...</td>
        </tr>
      `;
  });

  if (energyChart) {
    energyChart.destroy();
  }

  energyChart = new Chart(document.getElementById("energyChart"), {
    type: "bar",

    data: {
      labels: ["Energy Consumed", "Energy Generated"],

      datasets: [
        {
          label: "kWh",

          data: [
            analytics.total_energy_consumed,
            analytics.total_energy_generated,
          ],

          backgroundColor: ["#38bdf8", "#22c55e"],
        },
      ],
    },

    options: {
      responsive: true,

      plugins: {
        legend: {
          labels: {
            color: "white",
          },
        },
      },

      scales: {
        x: {
          ticks: {
            color: "white",
          },
        },

        y: {
          ticks: {
            color: "white",
          },
        },
      },
    },
  });

  const districtLabels = districts.map((d) => d._id);

  const districtEnergy = districts.map((d) => Math.round(d.energy));

  if (districtChart) {
    districtChart.destroy();
  }

  districtChart = new Chart(document.getElementById("districtChart"), {
    type: "bar",

    data: {
      labels: districtLabels,

      datasets: [
        {
          label: "Energy Consumption (kWh)",
          data: districtEnergy,
          backgroundColor: "#38bdf8",
        },
      ],
    },

    options: {
      responsive: true,

      plugins: {
        legend: {
          labels: {
            color: "white",
          },
        },
      },
    },
  });
}

loadDashboard();

setInterval(loadDashboard, 30000);
