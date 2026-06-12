let growthChart = null;
let distributionChart = null;

async function loadBlockchain() {
  const stats = await (await fetch("/api/stats")).json();

  const blocks = await (await fetch("/api/blocks")).json();

  document.getElementById("totalBlocks").innerText = stats.total_blocks;

  document.getElementById("totalTransactions").innerText =
    stats.total_transactions;

  document.getElementById("chainStatus").innerText = stats.chain_valid
    ? "VALID"
    : "INVALID";

  document.getElementById("chainStatus").style.color = stats.chain_valid
    ? "#22c55e"
    : "#ef4444";

  document.getElementById("securityScore").innerText = stats.chain_valid
    ? "100%"
    : "0%";

  document.getElementById("securityScore").style.color = stats.chain_valid
    ? "#22c55e"
    : "#ef4444";

  const table = document.getElementById("blockchainTable");

  table.innerHTML = "";

  blocks
    .slice(-10)
    .reverse()
    .forEach((block) => {
      table.innerHTML += `
      <tr>
        <td>${block.index}</td>
        <td>
          <span class="hash-badge">
            ${block.hash.substring(0, 12)}...
          </span>
        </td>
      </tr>
    `;
    });

  const transactions = await (await fetch("/api/transactions")).json();

  const transactionTypes = {};

  transactions.forEach((t) => {
    let type = "User Trading";

    if (t.username.includes("SolarFarm") || t.buyer.includes("SolarFarm")) {
      type = "Solar Trading";
    }

    transactionTypes[type] = (transactionTypes[type] || 0) + 1;
  });

  const chartLabels = Object.keys(transactionTypes);

  const chartValues = Object.values(transactionTypes);

  const txLabels = transactions.map((_, index) => `Trade ${index + 1}`);

  transactions.reverse();

  const txEnergy = transactions.map((t) => t.energy_sold);

  if (growthChart) growthChart.destroy();

  growthChart = new Chart(document.getElementById("blockChart"), {
    type: "line",

    data: {
      labels: txLabels,

      datasets: [
        {
          label: "Energy Traded (kWh)",

          data: txEnergy,

          backgroundColor: "#22c55e",
          borderColor: "#16a34a",
          borderWidth: 1,
          borderRadius: 10,
        },
      ],
    },

    options: {
      responsive: true,

      plugins: {
        tooltip: {
          callbacks: {
            afterLabel: function (context) {
              const tx = transactions[context.dataIndex];

              return `${tx.username} → ${tx.buyer}`;
            },
          },
        },

        legend: {
          labels: {
            color: "white",
          },
        },
      },

      scales: {
        x: {
          ticks: {
            color: "#cbd5e1",
          },
        },

        y: {
          ticks: {
            color: "#cbd5e1",
          },
        },
      },
    },
  });

  if (distributionChart) distributionChart.destroy();

  distributionChart = new Chart(document.getElementById("blockDistribution"), {
    type: "doughnut",

    data: {
      labels: chartLabels,

      datasets: [
        {
          data: chartValues,
        },
      ],
    },

    options: {
      cutout: "65%",
      plugins: {
        legend: {
          position: "top",
          labels: {
            color: "white",
          },
        },
      },
    },
  });
}

loadBlockchain();
