let userChart = null;

async function loadUsers() {
  const users = await (await fetch("/api/users")).json();

  const stats = await (await fetch("/api/users/stats")).json();

  const latest = await (await fetch("/api/users/latest")).json();

  document.getElementById("totalUsers").innerText = stats.total_users;

  document.getElementById("admins").innerText = stats.total_admins;

  document.getElementById("regularUsers").innerText = stats.total_regular_users;

  document.getElementById("latestUsers").innerText = stats.latest_users;

  const table = document.getElementById("usersTable");

  table.innerHTML = "";

  users.forEach((user) => {
    const roleBadge =
      user.role === "admin"
        ? `<span class="badge bg-danger">Admin</span>`
        : `<span class="badge bg-success">User</span>`;

    const createdDate = user.created_at
      ? new Date(user.created_at).toLocaleDateString("en-GB", {
          day: "2-digit",
          month: "short",
          year: "numeric",
        })
      : "N/A";

    table.innerHTML += `
      <tr>
        <td>${user.username}</td>
        <td>${user.email}</td>
        <td>${roleBadge}</td>
        <td>${user.energy_balance || 0}</td>
        <td>${createdDate}</td>
      </tr>
    `;
  });

  const latestList = document.getElementById("latestUsersList");

  latestList.innerHTML = "";

  latest.forEach((user) => {
    const roleColor = user.role === "admin" ? "#ef4444" : "#22c55e";

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
      labels: ["Admins", "Users"],

      datasets: [
        {
          data: [stats.total_admins, stats.total_regular_users],

          backgroundColor: ["#38bdf8", "#f43f5e"],
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
