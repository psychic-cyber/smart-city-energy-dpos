let growthChart = null;
let distributionChart = null;

async function loadBlockchain() {
  const stats = await (await fetch("/api/stats")).json();

  const blocks = await (await fetch("/api/blocks")).json();

  const delegates = await (await fetch("/api/delegates/top")).json();

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
          ${block.data?.validator || "SYSTEM"}
        </td>

        <td>
          <span class="hash-badge">
            ${block.hash.substring(0, 12)}...
          </span>
        </td>
      </tr>
    `;
    });

  const delegateTable = document.getElementById("delegateTable");

  if (delegateTable) {
    delegateTable.innerHTML = "";

    delegates.forEach((d, index) => {
      delegateTable.innerHTML += `
      <tr>
        <td>
          ${index === 0 ? `<span style="color:#fbbf24;">👑</span>` : ""}
          ${d.username}
        </td>
        <td>${d.role}</td>
        <td>${d.votes}</td>
      </tr>
      `;
    });
  }

  const validator = delegates.length > 0 ? delegates[0].username : "SYSTEM";

  document.getElementById("currentValidator").innerText = validator;

  const transactions = await (await fetch("/api/transactions")).json();

  const transactionTypes = {};

  blocks.forEach((block) => {
    const type = block.data?.transaction?.type;

    if (!type) return;

    transactionTypes[type] = (transactionTypes[type] || 0) + 1;
  });

  const labelMap = {
    ENERGY_READING_APPROVED: "Energy Reading",
    ENERGY_LISTED: "Energy Listed",
    MARKETPLACE_TRADE: "Marketplace Trade",
    ENERGY_SALE: "Energy Sale",
    AI_ALERT: "AI Alert",
  };

  const chartLabels = Object.keys(transactionTypes).map(
    (type) => labelMap[type] || type,
  );

  const chartValues = Object.values(transactionTypes);

  const blockLabels = blocks.map((block) => `#${block.index}`);

  const blockActivity = blocks.map((block) => {
    const tx = block.data?.transaction;

    if (!tx) {
      return 0;
    }

    return tx.energy || tx.generated || tx.consumed || 0;
  });

  if (growthChart) growthChart.destroy();

  growthChart = new Chart(document.getElementById("blockChart"), {
    type: "line",

    data: {
      labels: blockLabels,

      datasets: [
        {
          label: "Blockchain Activity",

          data: blockActivity,

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
      responsive: true,
      maintainAspectRatio: false,
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

// Keep an already-open ledger view current when marketplace trades add blocks.
setInterval(loadBlockchain, 5000);
