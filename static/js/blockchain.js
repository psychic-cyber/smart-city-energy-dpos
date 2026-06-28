let growthChart = null;
let distributionChart = null;
let toastTimeout = null;

function formatElectionTime(value) {
  if (!value) {
    return "-";
  }

  return new Date(value).toLocaleString();
}

function showToast(message) {
  const toast = document.getElementById("electionToast");
  const toastMessage = document.getElementById("electionToastMessage");

  toastMessage.innerText = message;
  toast.hidden = false;
  toast.classList.add("show");

  if (toastTimeout) {
    clearTimeout(toastTimeout);
  }

  toastTimeout = setTimeout(() => {
    toast.classList.remove("show");
    toast.hidden = true;
  }, 3500);
}

function openCloseElectionModal() {
  document.getElementById("closeElectionModal").hidden = false;
}

function closeCloseElectionModal() {
  document.getElementById("closeElectionModal").hidden = true;
}

async function closeElection() {
  const button = document.getElementById("confirmCloseElectionBtn");

  button.disabled = true;

  try {
    const response = await fetch("/api/election/close", {
      method: "POST",
    });

    if (!response.ok) {
      throw new Error("Failed to close election");
    }

    closeCloseElectionModal();
    showToast("Election closed successfully.");
    await loadBlockchain();
  } finally {
    button.disabled = false;
  }
}

async function startNextElection() {
  const button = document.getElementById("electionActionBtn");

  button.disabled = true;

  try {
    const response = await fetch("/api/election/start", {
      method: "POST",
    });

    if (!response.ok) {
      throw new Error("Failed to start election");
    }

    showToast("New election started successfully.");
    await loadBlockchain();
  } finally {
    button.disabled = false;
  }
}

function handleElectionAction() {
  const button = document.getElementById("electionActionBtn");

  if (button.dataset.action === "close") {
    openCloseElectionModal();
    return;
  }

  startNextElection();
}

function updateElectionCenter(dposStatus) {
  const isActive = dposStatus.election_state === "Active";
  const isClosed = dposStatus.election_state === "Closed";
  const hasLeader = Boolean(dposStatus.current_leader);

  document.getElementById("electionNumber").innerText =
    dposStatus.current_election ?? "-";

  const centerStatus = document.getElementById("electionCenterStatus");
  centerStatus.innerText = dposStatus.election_state || "-";
  centerStatus.style.color = isActive
    ? "#22c55e"
    : isClosed
      ? "#fbbf24"
      : "#94a3b8";

  const leaderName = document.getElementById("electionLeaderName");
  const leaderVotesLabel = document.getElementById("electionLeaderVotes");

  if (hasLeader) {
    leaderName.innerText = dposStatus.current_leader;
    leaderVotesLabel.innerText = `${dposStatus.leader_votes ?? 0} votes`;
  } else {
    leaderName.innerText = "Waiting for votes";
    leaderVotesLabel.innerText = "0 votes";
  }

  document.getElementById("electionLeaderVoteCount").innerText =
    dposStatus.leader_votes ?? 0;

  const totalVotes = dposStatus.total_votes ?? 0;
  const totalUsers = dposStatus.total_users ?? 0;

  document.getElementById("electionParticipationCount").innerText =
    `${totalVotes} / ${totalUsers} Users Voted`;

  document.getElementById("electionParticipationRate").innerText =
    `${dposStatus.participation_percentage ?? 0}%`;

  document.getElementById("electionStarted").innerText = formatElectionTime(
    dposStatus.election_started,
  );

  document.getElementById("electionEnded").innerText = isActive
    ? "-"
    : formatElectionTime(dposStatus.election_ended);

  const winnerEl = document.getElementById("electionWinner");

  if (isClosed && dposStatus.winner) {
    winnerEl.innerText = dposStatus.winner;
    winnerEl.style.color = "#fbbf24";
  } else {
    winnerEl.innerText = "-";
    winnerEl.style.color = "#94a3b8";
  }

  const validatorBadge = document.getElementById("electionValidatorBadge");

  if (dposStatus.current_validator) {
    validatorBadge.innerText = `Validator: ${dposStatus.current_validator}`;
    validatorBadge.classList.add("elected");
  } else {
    validatorBadge.innerText = "Validator: Not elected yet";
    validatorBadge.classList.remove("elected");
  }

  const actionBtn = document.getElementById("electionActionBtn");

  if (dposStatus.can_close_election) {
    actionBtn.dataset.action = "close";
    actionBtn.innerText = "Close Election";
    actionBtn.className = "btn btn-danger election-action-btn";
  } else {
    actionBtn.dataset.action = "start";
    actionBtn.innerText = "Start Next Election";
    actionBtn.className = "btn btn-success election-action-btn";
  }
}

function updateElectionHistoryTable(history) {
  const historyTable = document.getElementById("electionHistoryTable");
  historyTable.innerHTML = "";

  if (!history.length) {
    historyTable.innerHTML = `
      <tr>
        <td colspan="6" class="text-center text-secondary">
          No election history recorded yet
        </td>
      </tr>`;
    return;
  }

  history.forEach((election) => {
    const started = election.started_at || election.start_time;
    const ended = election.ended_at || election.end_time;

    historyTable.innerHTML += `
      <tr>
        <td>#${election.election_id}</td>
        <td>${election.winner || "-"}</td>
        <td>${election.total_votes ?? 0}</td>
        <td>${formatElectionTime(started)}</td>
        <td>${formatElectionTime(ended)}</td>
        <td>
          <span class="badge ${
            election.status === "Active" ? "bg-success" : "bg-secondary"
          }">
            ${election.status}
          </span>
        </td>
      </tr>`;
  });
}

async function loadBlockchain() {
  const stats = await (await fetch("/api/stats")).json();
  const blocks = await (await fetch("/api/blocks")).json();
  const delegates = await (await fetch("/api/delegates/top")).json();
  const dposStatus = await (await fetch("/api/dpos/status")).json();
  const validatorHistory = await (
    await fetch("/api/dpos/validator-history")
  ).json();
  const electionHistory = await (
    await fetch("/api/election/history")
  ).json();

  document.getElementById("totalBlocks").innerText = stats.total_blocks;
  document.getElementById("totalTransactions").innerText =
    stats.total_transactions;

  const chainStatus = document.getElementById("chainStatus");
  chainStatus.innerText = stats.chain_valid ? "VALID" : "INVALID";
  chainStatus.style.color = stats.chain_valid ? "#22c55e" : "#ef4444";

  const securityScore = document.getElementById("securityScore");
  securityScore.innerText = stats.chain_valid ? "100%" : "0%";
  securityScore.style.color = stats.chain_valid ? "#22c55e" : "#ef4444";

  updateElectionCenter(dposStatus);
  updateElectionHistoryTable(electionHistory);

  const table = document.getElementById("blockchainTable");
  table.innerHTML = "";

  blocks
    .slice(-10)
    .reverse()
    .forEach((block) => {
      table.innerHTML += `
      <tr>
        <td>${block.index}</td>
        <td>${block.data?.validator || "SYSTEM"}</td>
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
      const isActive = d.votes > 0 && d.is_active;

      delegateTable.innerHTML += `
      <tr>
        <td>
          ${isActive ? `<span style="color:#fbbf24;">👑</span>` : ""}
          ${d.username}
        </td>
        <td>${d.role}</td>
        <td>${d.votes}</td>
        <td>
          <span class="badge ${isActive ? "bg-success" : "bg-secondary"}">
            ${isActive ? "Active" : "Standby"}
          </span>
        </td>
      </tr>
      `;
    });
  }

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
  .getElementById("electionActionBtn")
  .addEventListener("click", handleElectionAction);

document
  .getElementById("cancelCloseElectionBtn")
  .addEventListener("click", closeCloseElectionModal);

document
  .getElementById("confirmCloseElectionBtn")
  .addEventListener("click", closeElection);

document
  .querySelector(".election-modal-backdrop")
  .addEventListener("click", closeCloseElectionModal);

setInterval(loadBlockchain, 5000);
