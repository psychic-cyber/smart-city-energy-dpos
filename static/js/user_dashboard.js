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
      alert(`Energy Sold!\nRevenue: Rs ${result.earned}`);

      loadUserDashboard();

      loadTransactions();
    } else {
      alert(result.message);
    }
  } catch (error) {
    console.error(error);
  }
}

loadUserDashboard();

loadTransactions();

loadDelegates();

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

  alert(result.message);
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

  alert(result.message);
}

async function loadDelegates() {
  const response = await fetch("/api/delegates");

  const delegates = await response.json();

  const container = document.getElementById("delegateVotingList");

  container.innerHTML = "";

  delegates.forEach((d) => {
    container.innerHTML += `
      <div
        class="d-flex justify-content-between align-items-center mb-3 p-3"
        style="
          background: rgba(15,23,42,0.8);
          border-radius:12px;
        "
      >
        <div>
          <h6 style="color:white;">
            ${d.username}
          </h6>

          <small>
            ${d.role}
          </small>
        </div>

        <button
          class="btn btn-success"
          onclick="vote('${d.username}')"
        >
          Vote
        </button>

      </div>
    `;
  });
}

async function vote(delegate) {
  const response = await fetch("/api/vote", {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      delegate,
    }),
  });

  const result = await response.json();

  alert(result.message);

  loadDelegates();
}
