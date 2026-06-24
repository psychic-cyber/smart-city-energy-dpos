let userChart = null;

async function loadUsers() {
  const users = await (await fetch("/api/users")).json();

  const stats = await (await fetch("/api/users/stats")).json();

  const latest = await (await fetch("/api/users/latest")).json();

  document.getElementById("totalUsers").innerText = stats.total_users;

  document.getElementById("admins").innerText = stats.admins;

  document.getElementById("regularUsers").innerText =
    stats.houses +
    stats.hospitals +
    stats.universities +
    stats.restaurants +
    stats.offices +
    stats.factories +
    stats.solarfarms;

  document.getElementById("latestUsers").innerText = latest.length;

  const table = document.getElementById("usersTable");

  table.innerHTML = "";

  users.forEach((user) => {
    const roleBadge = `
    <span class="badge bg-info">
      ${user.role}
    </span>
  `;

    const createdDate = user.created_at
      ? new Date(user.created_at).toLocaleDateString("en-GB", {
          day: "2-digit",
          month: "short",
          year: "numeric",
        })
      : "N/A";

    const allowedRoles = ["SolarFarm", "Hospital", "University"];

    const voteButton = allowedRoles.includes(user.role)
      ? `
        <button
          class="btn btn-sm btn-success"
          onclick="voteDelegate('${user.username}')"
        >
          Vote
        </button>
      `
      : "-";

    table.innerHTML += `
    <tr>
      <td>${user.username}</td>
      <td>${user.email}</td>
      <td>${roleBadge}</td>
      <td>${user.energy_balance || 0}</td>
      <td>${createdDate}</td>
      <td>${voteButton}</td>
    </tr>
  `;
  });

  const latestList = document.getElementById("latestUsersList");

  latestList.innerHTML = "";

  latest.forEach((user) => {
    const roleColor = user.role === "Admin" ? "#ef4444" : "#22c55e";

    latestList.innerHTML += `
      <div
        style="
          background: rgba(15,23,42,0.8);
          border: 1px solid rgba(56,189,248,0.15);
          border-radius: 12px;
          padding: 15px;
          margin-bottom: 12px;
        "
      >
        <h6 style="color:white;margin:0;">
          ${user.username}
        </h6>

        <small
          style="
            color:${roleColor};
            font-weight:600;
          "
        >
          ${user.role.toUpperCase()}
        </small>
      </div>
    `;
  });

  if (userChart) {
    userChart.destroy();
  }

  userChart = new Chart(document.getElementById("userChart"), {
    type: "pie",

    data: {
      labels: [
        "House",
        "Hospital",
        "University",
        "Restaurant",
        "Office",
        "Factory",
        "SolarFarm",
      ],

      datasets: [
        {
          data: [
            stats.houses,
            stats.hospitals,
            stats.universities,
            stats.restaurants,
            stats.offices,
            stats.factories,
            stats.solarfarms,
          ],

          backgroundColor: [
            "#38bdf8",
            "#f43f5e",
            "#22c55e",
            "#f59e0b",
            "#8b5cf6",
            "#ef4444",
            "#06b6d4",
          ],
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

loadUsers();

async function voteDelegate(username) {
  const response = await fetch(`/api/delegates/vote/${username}`, {
    method: "POST",
  });

  const result = await response.json();

  alert(result.message);

  loadUsers();
}
