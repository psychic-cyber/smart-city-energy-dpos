function showToast(message, type = "success") {
  let container = document.querySelector(".toast-container");

  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast-notification toast-${type}`;

  const icon =
    type === "success"
      ? "bi-check-circle-fill"
      : "bi-exclamation-triangle-fill";

  toast.innerHTML = `
        <div class="toast-content">
            <i class="bi ${icon}"></i>
            <span>${message}</span>
        </div>
    `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "slideOut .3s forwards";

    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 3000);
}

document
  .getElementById("loginForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    try {
      const response = await fetch("/login", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        showToast("Login successful.", "success");

        setTimeout(() => {
          window.location.href = result.redirect;
        }, 1000);
      } else {
        showToast(result.message, "error");
      }
    } catch (err) {
      console.error(err);

      showToast("Unable to connect to server.", "error");
    }
  });
