let growthChart = null;
let distributionChart = null;

function formatElectionTime(value) {
  if (!value) {
    return "-";
  }

  return new Date(value).toLocaleString();
}

async function startNewElection() {
  const button = document.getElementById("startElectionBtn");

  button.disabled = true;

  try {
    await fetch("/api/election/start", {
      method: "POST",
    });

    await loadBlockchain();
  } finally {
    button.disabled = false;
  }
}

function updateElectionCenter(dposStatus) {
  document.getElementById("electionNumber").innerText =
    dposStatus.current_election ?? "-";

  const centerStatus = document.getElementById("electionCenterStatus");
  centerStatus.innerText = dposStatus.election_state || "-";
  centerStatus.style.color =
    dposStatus.election_state === "Active" ? "#22c55e" : "#fbbf24";

  document.getElementById("electionLeader").innerText =
    dposStatus.current_leader || "None";

  document.getElementById("electionVotes").innerText =
    dposStatus.total_votes ?? 0;

  document.getElementById("electionParticipation").innerText =
    `${dposStatus.participation_percentage ?? 0}%`;

  document.getElementById("electionStarted").innerText = formatElectionTime(
    dposStatus.election_started,
  );
}

async function loadBlockchain() {
  const blocks = await (await fetch("/api/blocks")).json();

  const delegates = await (await fetch("/api/delegates/top")).json();

  const dposStatus = await (await fetch("/api/dpos/status")).json();

  const validatorHistory = await (
    await fetch("/api/dpos/validator-history")
  ).json();

  updateElectionCenter(dposStatus);

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

    delegates.forEach((d) => {
      delegateTable.innerHTML += `
      <tr>
        <td>
          ${d.is_active ? `<span style="color:#fbbf24;">👑</span>` : ""}
          ${d.username}
        </td>
        <td>${d.role}</td>
        <td>${d.votes}</td>
        <td>
          <span class="badge ${d.is_active ? "bg-success" : "bg-secondary"}">
            ${d.is_active ? "Active" : "Standby"}
          </span>
        </td>
      </tr>
      `;
    });
  }

  document.getElementById("currentValidator").innerText =
    dposStatus.current_validator || "SYSTEM";

  document.getElementById("totalDelegateVotes").innerText =
    dposStatus.total_delegate_votes;

  document.getElementById("lastElectionTime").innerText =
    dposStatus.last_election_time
      ? new Date(dposStatus.last_election_time).toLocaleString()
      : "Not elected";

  const electionStatus = document.getElementById("electionStatus");
  electionStatus.innerText = dposStatus.election_status;
  electionStatus.style.color = dposStatus.current_validator
    ? "#22c55e"
    : "#fbbf24";

  const historyTable = document.getElementById("validatorHistoryTable");
  historyTable.innerHTML = "";

  if (!validatorHistory.length) {
    historyTable.innerHTML = `
      <tr>
        <td colspan="5" class="text-center text-secondary">
          No validator changes recorded
        </td>
      </tr>`;
  } else {
    validatorHistory.forEach((election) => {
      historyTable.innerHTML += `
        <tr>
          <td>${election.previous_validator || "Initial Election"}</td>
          <td>${election.new_validator}</td>
          <td>${election.previous_votes}</td>
          <td>${election.new_votes}</td>
          <td>${new Date(election.election_time).toLocaleString()}</td>
        </tr>`;
    });
  }

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

document
  .getElementById("startElectionBtn")
  .addEventListener("click", startNewElection);

setInterval(loadBlockchain, 5000);
