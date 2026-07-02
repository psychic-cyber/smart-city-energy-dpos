let growthChart = null;
let distributionChart = null;

// =====================
// TOAST NOTIFICATION SYSTEM
// =====================

function showToast(message, type = 'info', duration = 4000) {
  const container = document.getElementById('dposToastContainer');
  const toast = document.createElement('div');
  toast.className = `dpos-toast dpos-toast--${type}`;
  
  const icons = {
    success: 'bi-check-circle-fill',
    error: 'bi-exclamation-circle-fill',
    info: 'bi-info-circle-fill',
    warning: 'bi-exclamation-triangle-fill'
  };
  
  toast.innerHTML = `
    <div class="dpos-toast__icon">
      <i class="bi ${icons[type]}"></i>
    </div>
    <span>${message}</span>
  `;
  
  container.appendChild(toast);
  
  if (duration > 0) {
    setTimeout(() => {
      toast.style.animation = 'dposToastSlideOut 0.24s cubic-bezier(0.4, 0, 0.2, 1) forwards';
      setTimeout(() => toast.remove(), 240);
    }, duration);
  }
  
  return toast;
}

// =====================
// DPoS MODAL FUNCTIONS
// =====================

function openStartElectionModal() {
  const overlay = document.getElementById('startElectionModalOverlay');
  overlay.classList.add('active');
  
  // Populate modal data
  fetch('/api/dpos/status')
    .then(r => r.json())
    .then(data => {
      document.getElementById('startModalElectionNum').innerText = data.current_election || '-';
      document.getElementById('startModalCurrentValidator').innerText = data.current_validator || 'None';
    })
    .catch(err => console.error('Failed to load modal data:', err));
}

function closeStartElectionModal() {
  const overlay = document.getElementById('startElectionModalOverlay');
  overlay.classList.remove('active');
}

function openFinishElectionModal() {
  const overlay = document.getElementById('finishElectionModalOverlay');
  overlay.classList.add('active');
  
  // Populate modal data
  fetch('/api/dpos/status')
    .then(r => r.json())
    .then(data => {
      document.getElementById('finishModalElectionNum').innerText = data.current_election || '-';
      document.getElementById('finishModalTotalVotes').innerText = data.total_votes || 0;
      document.getElementById('finishModalLeader').innerText = data.current_leader || 'None';
      document.getElementById('finishModalLeaderVotes').innerText = data.leader_votes || 0;
    })
    .catch(err => console.error('Failed to load modal data:', err));
}

function closeFinishElectionModal() {
  const overlay = document.getElementById('finishElectionModalOverlay');
  overlay.classList.remove('active');
}

// Close modals on overlay click
document.addEventListener('click', (e) => {
  if (e.target.id === 'startElectionModalOverlay') {
    closeStartElectionModal();
  }
  if (e.target.id === 'finishElectionModalOverlay') {
    closeFinishElectionModal();
  }
});

// =====================
// ELECTION WORKFLOW FUNCTIONS
// =====================

async function startNewElection() {
  openStartElectionModal();
}

async function confirmStartNewElection() {
  const button = document.getElementById('confirmStartElectionBtn');
  button.disabled = true;
  
  try {
    const resp = await fetch('/api/election/start', { method: 'POST' });
    
    if (resp.ok) {
      showToast('✨ Election started successfully!', 'success');
      closeStartElectionModal();
      
      // Update UI
      document.getElementById('startElectionBtn').style.display = 'none';
      document.getElementById('finishElectionBtn').style.display = 'inline-block';
      
      await new Promise(resolve => setTimeout(resolve, 500));
      await loadBlockchain();
    } else {
      const error = await resp.text();
      showToast(`❌ Failed to start election: ${error}`, 'error');
      console.error('Unable to start election', error);
    }
  } catch (err) {
    showToast('❌ Error starting election', 'error');
    console.error('Error starting election', err);
  } finally {
    button.disabled = false;
  }
}

async function finishNewElection() {
  openFinishElectionModal();
}

async function confirmFinishElection() {
  const button = document.getElementById('confirmFinishElectionBtn');
  button.disabled = true;
  
  try {
    const resp = await fetch('/api/election/end', { method: 'POST' });
    
    if (resp.ok) {
      showToast('🏆 Election finished! New validator elected.', 'success');
      closeFinishElectionModal();
      
      // Update UI
      document.getElementById('startElectionBtn').style.display = 'inline-block';
      document.getElementById('finishElectionBtn').style.display = 'none';
      
      await new Promise(resolve => setTimeout(resolve, 500));
      await loadBlockchain();
    } else {
      const error = await resp.text();
      showToast(`❌ Failed to finish election: ${error}`, 'error');
      console.error('Unable to finish election', error);
    }
  } catch (err) {
    showToast('❌ Error finishing election', 'error');
    console.error('Error finishing election', err);
  } finally {
    button.disabled = false;
  }
}

// =====================
// ELECTION CENTER UPDATE
// =====================

function formatElectionTime(value) {
  if (!value) {
    return "-";
  }

  return new Date(value).toLocaleString();
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
  
  // Update button visibility based on election state
  const electionActive = dposStatus.election_state === 'Active' || dposStatus.election_state === 'active';
  document.getElementById('startElectionBtn').style.display = electionActive ? 'none' : 'inline-block';
  document.getElementById('finishElectionBtn').style.display = electionActive ? 'inline-block' : 'none';
}

// =====================
// BLOCKCHAIN DATA LOADING
// =====================

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

// =====================
// INITIALIZATION & EVENT LISTENERS
// =====================

loadBlockchain();

document.getElementById("startElectionBtn").addEventListener("click", startNewElection);
document.getElementById("finishElectionBtn").addEventListener("click", finishNewElection);
document.getElementById("confirmStartElectionBtn").addEventListener("click", confirmStartNewElection);
document.getElementById("confirmFinishElectionBtn").addEventListener("click", confirmFinishElection);

// Auto-refresh every 5 seconds
setInterval(loadBlockchain, 5000);
