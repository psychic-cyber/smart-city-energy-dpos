async function loadBlockchain() {
  const statsResponse = await fetch("/api/stats");

  const blocksResponse = await fetch("/api/blocks");

  const stats = await statsResponse.json();

  const blocks = await blocksResponse.json();

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
                <td>${block.hash.substring(0, 12)}...</td>
            </tr>
        `;
  });

  const growthData = Array.from({ length: blocks.length }, (_, i) => i + 1);

  new Chart(document.getElementById("blockChart"), {
    type: "line",

    data: {
      labels: growthData,

      datasets: [
        {
          label: "Blockchain Growth",

          data: growthData,

          borderWidth: 3,

          tension: 0.4,

          fill: false,
        },
      ],
    },

    options: {
      responsive: true,

      plugins: {
        legend: {
          display: true,
        },
      },
    },
  });

  new Chart(document.getElementById("blockDistribution"), {
    type: "doughnut",

    data: {
      labels: ["Validated Blocks", "Reserved Capacity"],

      datasets: [
        {
          data: [blocks.length, Math.max(100 - blocks.length, 0)],
        },
      ],
    },

    options: {
      responsive: true,
    },
  });
}

loadBlockchain();
