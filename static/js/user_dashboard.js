// =====================
// TOAST NOTIFICATION SYSTEM (Shared with blockchain)
// =====================

function showToast(message, type = 'info', duration = 4000) {
  let container = document.getElementById('dposToastContainer');
  
  // If container doesn't exist in user dashboard, create it
  if (!container) {
    container = document.createElement('div');
    container.id = 'dposToastContainer';
    container.className = 'dpos-toast-container';
    document.body.appendChild(container);
  }
  
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

async function loadUserDashboard() {
  try {
    const response = await fetch("/api/user/dashboard");

    const data = await response.json();

    document.getElementById("energyBalance").innerText =
      data.energy_balance + " kWh";

    document.getElementById("energyGenerated").innerText =
      data.energy_generated + " kWh";

    document.getElementById("energyConsumed").innerText =
      data.energy_consumed + " kWh";

    document.getElementById("revenue").innerText = "Rs " + data.revenue;
  } catch (error) {
    console.error(error);
  }
}

async function loadTransactions() {
  const response = await fetch("/api/user/transactions");

  const data = await response.json();

  const table = document.getElementById("transactionsTable");

  table.innerHTML = "";

  data.forEach((t) => {
    table.innerHTML += `
      <tr>
        <td>${t.buyer}</td>
        <td>${t.energy_sold} kWh</td>
        <td>Rs ${t.revenue}</td>
        <td>${t.status}</td>
        <td>${t.timestamp}</td>
      </tr>
    `;
  });
}

async function sellEnergy() {
  try {
    const response = await fetch("/api/sell-energy", {
      method: "POST",
    });

    const result = await response.json();

    if (result.success) {
      showToast(`💰 Energy Sold! Revenue: Rs ${result.earned}`, 'success');

      loadUserDashboard();

      loadTransactions();
    } else {
      showToast(result.message, 'error');
    }
  } catch (error) {
    showToast('❌ Error selling energy', 'error');
    console.error(error);
  }
}

loadUserDashboard();

loadTransactions();

loadDelegates();

loadDposStatus();

async function createListing() {
  const energy = document.getElementById("listingEnergy").value;

  const price = document.getElementById("listingPrice").value;

  const response = await fetch("/api/create-listing", {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      energy,
      price,
    }),
  });

  const result = await response.json();

  showToast(result.message, result.success ? 'success' : 'error');
}

async function submitEnergyReading() {
  const generated = document.getElementById("generatedEnergy").value;

  const consumed = document.getElementById("consumedEnergy").value;

  const response = await fetch("/api/submit-energy", {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      generated,
      consumed,
    }),
  });

  const result = await response.json();

  showToast(result.message, result.success ? 'success' : 'error');
}

// =====================
// DPoS VOTING WORKFLOW
// =====================

let userHasVoted = false;
let userVotedFor = null;

async function checkUserVote() {
  try {
    const response = await fetch("/api/user/vote-status");
    const data = await response.json();
    userHasVoted = data.has_voted || false;
    userVotedFor = data.voted_for || null;
  } catch (error) {
    console.error("Failed to check vote status:", error);
  }
}

async function loadDelegates() {
  try {
    await checkUserVote();
    
    const response = await fetch("/api/delegates");
    const delegates = await response.json();

    const container = document.getElementById("delegateVotingList");
    container.innerHTML = "";

    if (!delegates || delegates.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 2rem; color: #94a3b8;">
          <i class="bi bi-inbox" style="font-size: 2rem; display: block; margin-bottom: 0.5rem;"></i>
          <p>No delegates available</p>
        </div>
      `;
      return;
    }

    delegates.forEach((d) => {
      const hasVoted = userHasVoted && userVotedFor === d.username;
      const cardClass = hasVoted ? 'voted' : '';
      
      container.innerHTML += `
        <div class="dpos-delegate-card ${cardClass}" id="delegate_${d.username}">
          <div class="dpos-delegate-info">
            <p class="dpos-delegate-name">
              ${d.username}
              ${d.is_active ? '<span style="color: #fbbf24; margin-left: 0.5rem;"><i class="bi bi-star-fill"></i></span>' : ''}
            </p>
            <p class="dpos-delegate-votes">
              <i class="bi bi-hand-thumbs-up"></i> ${d.votes} vote${d.votes !== 1 ? 's' : ''}
            </p>
          </div>
          <button 
            class="dpos-vote-btn" 
            onclick="vote('${d.username}')"
            id="voteBtn_${d.username}"
            ${hasVoted ? 'disabled' : ''}
          >
            ${hasVoted ? '<i class="bi bi-check-circle"></i> Voted' : '<i class="bi bi-check"></i> Vote'}
          </button>
        </div>
      `;
    });
  } catch (error) {
    showToast('❌ Failed to load delegates', 'error');
    console.error(error);
  }
}

async function vote(delegate) {
  if (userHasVoted) {
    showToast(`⚠️ You have already voted for ${userVotedFor}`, 'warning');
    return;
  }

  const button = document.getElementById(`voteBtn_${delegate}`);
  button.disabled = true;

  try {
    const response = await fetch("/api/vote", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ delegate }),
    });

    const result = await response.json();

    if (response.ok) {
      // Update voting state
      userHasVoted = true;
      userVotedFor = delegate;

      // Update UI
      const card = document.getElementById(`delegate_${delegate}`);
      if (card) card.classList.add('voted');
      
      button.innerHTML = '<i class="bi bi-check-circle"></i> Voted';
      button.disabled = true;

      // Show success toast
      showToast(`✨ Your vote for ${delegate} has been recorded!`, 'success');

      // Reload delegates to show updated vote counts
      await new Promise(resolve => setTimeout(resolve, 800));
      await Promise.all([loadDelegates(), loadDposStatus()]);
    } else {
      button.disabled = false;
      showToast(result.message || '❌ Failed to vote', 'error');
    }
  } catch (error) {
    button.disabled = false;
    showToast('❌ Error voting', 'error');
    console.error(error);
  }
}

async function loadDposStatus() {
  try {
    const response = await fetch("/api/dpos/status");
    if (!response.ok) {
      return;
    }

    const status = await response.json();

    const electionElements = {
      electionNumber: document.getElementById("electionNumber"),
      electionCenterStatus: document.getElementById("electionCenterStatus"),
      electionLeader: document.getElementById("electionLeader"),
      electionVotes: document.getElementById("electionVotes"),
      electionParticipation: document.getElementById("electionParticipation"),
      electionStarted: document.getElementById("electionStarted"),
      currentValidator: document.getElementById("currentValidator"),
      totalDelegateVotes: document.getElementById("totalDelegateVotes"),
      electionStatus: document.getElementById("electionStatus"),
    };

    if (electionElements.electionNumber) {
      electionElements.electionNumber.innerText = status.current_election ?? "-";
    }
    if (electionElements.electionCenterStatus) {
      electionElements.electionCenterStatus.innerText = status.election_state || "-";
      electionElements.electionCenterStatus.style.color =
        status.election_state === "Active" ? "#22c55e" : "#fbbf24";
    }
    if (electionElements.electionLeader) {
      electionElements.electionLeader.innerText = status.current_leader || "None";
    }
    if (electionElements.electionVotes) {
      electionElements.electionVotes.innerText = status.total_votes ?? 0;
    }
    if (electionElements.electionParticipation) {
      electionElements.electionParticipation.innerText = `${status.participation_percentage ?? 0}%`;
    }
    if (electionElements.electionStarted) {
      electionElements.electionStarted.innerText = status.election_started || "-";
    }
    if (electionElements.currentValidator) {
      electionElements.currentValidator.innerText = status.current_validator || "SYSTEM";
    }
    if (electionElements.totalDelegateVotes) {
      electionElements.totalDelegateVotes.innerText = status.total_delegate_votes ?? 0;
    }
    if (electionElements.electionStatus) {
      electionElements.electionStatus.innerText = status.election_status || "-";
      electionElements.electionStatus.style.color = status.current_validator
        ? "#22c55e"
        : "#fbbf24";
    }
  } catch (error) {
    console.error("Unable to refresh election status", error);
  }
}

// =====================
// AUTO-REFRESH VOTING STATUS
// =====================

// Refresh voting delegates every 4 seconds
setInterval(async () => {
  await checkUserVote();
  
  // Update vote buttons state
  const buttons = document.querySelectorAll('[id^="voteBtn_"]');
  buttons.forEach(btn => {
    const delegateName = btn.id.replace('voteBtn_', '');
    const hasVoted = userHasVoted && userVotedFor === delegateName;
    
    if (hasVoted) {
      btn.disabled = true;
      btn.innerHTML = '<i class="bi bi-check-circle"></i> Voted';
    }
  });
}, 4000);
