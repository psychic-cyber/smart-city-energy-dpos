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

  const table = document.getElementById("blockchainTable");

  table.innerHTML = "";

  blocks.forEach((block) => {
    table.innerHTML += `
      <tr>
        <td>${block.index}</td>
        <td>${block.hash.substring(0, 15)}...</td>
      </tr>
    `;
  });

  const blockIndexes = blocks.map((block) => block.index);

  if (growthChart) growthChart.destroy();

  growthChart = new Chart(document.getElementById("blockChart"), {
    type: "line",

    data: {
      labels: blockIndexes,

      datasets: [
        {
          label: "Block Index",

          data: blockIndexes,

          borderColor: "#22c55e",

          tension: 0.4,
        },
      ],
    },
  });

  if (distributionChart) distributionChart.destroy();

  distributionChart = new Chart(document.getElementById("blockDistribution"), {
    type: "pie",

    data: {
      labels: ["Blocks", "Transactions"],

      datasets: [
        {
          data: [stats.total_blocks, stats.total_transactions],
        },
      ],
    },
  });
}

loadBlockchain();
