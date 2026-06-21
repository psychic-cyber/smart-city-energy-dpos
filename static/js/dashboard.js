let energyChart = null;
let districtChart = null;

async function loadDashboard() {
  const stats = await (await fetch("/api/stats")).json();

  const aiData = await (await fetch("/api/ai-monitoring")).json();

  const analytics = await (await fetch("/api/analytics")).json();

  const transactions = await (await fetch("/api/transactions")).json();

  const blocks = await (await fetch("/api/blocks")).json();

  const districts = await (await fetch("/api/districts")).json();

  const pendingReadings = await (await fetch("/api/pending-readings")).json();

  document.getElementById("transactions").innerText =
    stats.total_transactions.toLocaleString();

  document.getElementById("blocks").innerText =
    stats.total_blocks.toLocaleString();

  document.getElementById("status").innerText = stats.chain_valid
    ? "VALID"
    : "INVALID";

  document.getElementById("health").innerText =
    (100 - aiData.anomaly_rate).toFixed(2) + "%";

  document.getElementById("anomalies").innerText =
    analytics.anomalies_detected.toLocaleString();

  document.getElementById("consumed").innerText = Math.round(
    analytics.total_energy_consumed,
  ).toLocaleString();

  document.getElementById("generated").innerText = Math.round(
    analytics.total_energy_generated,
  ).toLocaleString();

  document.getElementById("revenue").innerText =
    "Rs " + Math.round(analytics.total_bill_amount).toLocaleString();

  document.getElementById("lastUpdated").innerText =
    "Last Updated: " + new Date().toLocaleString();

  const efficiency = Math.min(
    100,
    (analytics.total_energy_consumed / analytics.total_energy_generated) * 100,
  );

  document.getElementById("efficiency").innerText = efficiency.toFixed(1) + "%";

  if (efficiency >= 90) {
    document.getElementById("efficiency").style.color = "#22c55e";
  } else if (efficiency >= 75) {
    document.getElementById("efficiency").style.color = "#facc15";
  } else {
    document.getElementById("efficiency").style.color = "#ef4444";
  }

  let gridStability = 100;

  if (stats.total_transactions > 0) {
    const anomalyRate = aiData.anomaly_rate || 0;

    gridStability = Math.max(0, 100 - anomalyRate * 1.5);
  }

  document.getElementById("gridStability").innerText =
    gridStability.toFixed(1) + "%";

  document.getElementById("gridStability").innerText =
    gridStability.toFixed(1) + "%";

  document.getElementById("aiAccuracy").innerText =
    aiData.accuracy.toFixed(2) + "%";

  const securityScore = stats.chain_valid ? 100 : 50;

  document.getElementById("securityScore").innerText = securityScore + "%";

  const transactionTable = document.getElementById("transactionsTable");

  transactionTable.innerHTML = "";

  transactions.slice(0, 10).forEach((t) => {
    transactionTable.innerHTML += `
        <tr>
          <td>${t.username}</td>
          <td>${t.buyer}</td>
          <td>${t.energy_sold}</td>
          <td>${t.revenue}</td>
        </tr>
      `;
  });

  const blockTable = document.getElementById("blocksTable");

  blockTable.innerHTML = "";

  blocks.slice(0, 10).forEach((b) => {
    blockTable.innerHTML += `
        <tr>
          <td>${b.index}</td>
          <td>${b.hash.substring(0, 10)}
            ...${b.hash.substring(b.hash.length - 6)}
          </td>
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

  const pendingTable = document.getElementById("pendingReadingsTable");

  if (pendingTable) {
    pendingTable.innerHTML = "";

    if (pendingReadings.length === 0) {
      pendingTable.innerHTML = `
      <tr>
        <td colspan="5" style="text-align:center;">
          No Pending Energy Readings
        </td>
      </tr>
    `;
    } else {
      pendingReadings.forEach((record) => {
        pendingTable.innerHTML += `
      <tr>
        <td>${record.username}</td>
        <td>${record.energy_generated}</td>
        <td>${record.energy_consumed}</td>
        <td>${record.status}</td>
        <td>
          <button
            class="btn btn-success btn-sm"
            onclick="approveReading('${record.username}')"
          >
            Approve
          </button>

          <button
            class="btn btn-danger btn-sm ms-1"
            onclick="declineReading('${record.username}')"
          >
            Decline
          </button>
        </td>
      </tr>
      `;
      });
    }
  }

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

async function approveReading(username) {
  const response = await fetch("/api/approve-reading", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username: username,
    }),
  });

  const result = await response.json();

  alert(result.message);

  loadDashboard();
}

async function declineReading(username) {
  const response = await fetch("/api/decline-reading", {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      username: username,
    }),
  });

  const result = await response.json();

  alert(result.message);

  loadDashboard();
}
