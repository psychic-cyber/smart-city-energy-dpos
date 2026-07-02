let userChart = null;
let userToDeleteUsername = null;

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

    // Add delete button for non-admin users
    const deleteButton = user.role !== "Admin"
      ? `
        <button
          class="btn btn-sm btn-danger"
          onclick="showDeleteModal('${user.username}')"
          title="Delete user"
        >
          <i class="bi bi-trash"></i>
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
      <td>${deleteButton}</td>
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

function showDeleteModal(username) {
  userToDeleteUsername = username;
  document.querySelector(".user-to-delete-name").textContent = `Username: ${username}`;
  const deleteModal = new bootstrap.Modal(document.getElementById("deleteUserModal"));
  deleteModal.show();
}

async function confirmDeleteUser() {
  if (!userToDeleteUsername) return;

  const confirmBtn = document.getElementById("confirmDeleteBtn");
  confirmBtn.disabled = true;
  confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Deleting...';

  try {
    const response = await fetch(`/api/delete-user/${userToDeleteUsername}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (data.success) {
      showSuccessToast(`User '${userToDeleteUsername}' deleted successfully`);
      const deleteModal = bootstrap.Modal.getInstance(document.getElementById("deleteUserModal"));
      deleteModal.hide();
      loadUsers();
    } else {
      showErrorToast(data.message || "Failed to delete user");
    }
  } catch (error) {
    console.error("Error:", error);
    showErrorToast("An error occurred while deleting the user");
  } finally {
    confirmBtn.disabled = false;
    confirmBtn.innerHTML = "Delete User";
    userToDeleteUsername = null;
  }
}

function showSuccessToast(message) {
  const toastHtml = `
    <div class="toast-notification toast-success" role="alert">
      <div class="toast-content">
        <i class="bi bi-check-circle-fill"></i>
        <span>${message}</span>
      </div>
    </div>
  `;
  const toastContainer = document.querySelector(".toast-container") || createToastContainer();
  const toastElement = document.createElement("div");
  toastElement.innerHTML = toastHtml;
  toastContainer.appendChild(toastElement.firstElementChild);

  const toast = toastContainer.lastElementChild;
  setTimeout(() => {
    toast.style.animation = "slideOut 0.3s ease forwards";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function showErrorToast(message) {
  const toastHtml = `
    <div class="toast-notification toast-error" role="alert">
      <div class="toast-content">
        <i class="bi bi-exclamation-circle-fill"></i>
        <span>${message}</span>
      </div>
    </div>
  `;
  const toastContainer = document.querySelector(".toast-container") || createToastContainer();
  const toastElement = document.createElement("div");
  toastElement.innerHTML = toastHtml;
  toastContainer.appendChild(toastElement.firstElementChild);

  const toast = toastContainer.lastElementChild;
  setTimeout(() => {
    toast.style.animation = "slideOut 0.3s ease forwards";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function createToastContainer() {
  const container = document.createElement("div");
  container.className = "toast-container";
  container.style.cssText = `
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 2000;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  `;
  document.body.appendChild(container);
  return container;
}

// Setup delete confirmation button
document.addEventListener("DOMContentLoaded", function() {
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener("click", confirmDeleteUser);
  }
});

loadUsers();

async function voteDelegate(username) {
  const response = await fetch("/api/vote", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ delegate: username }),
  });

  const result = await response.json();

  alert(result.message);

  loadUsers();
}
