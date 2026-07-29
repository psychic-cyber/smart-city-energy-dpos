console.log("LOGIN JS LOADED");

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

    const submitBtn = this.querySelector("button[type='submit']");

    submitBtn.disabled = true;
    submitBtn.innerHTML = `
    <span class="spinner-border spinner-border-sm me-2"></span>
    Signing In...
`;

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
        }, 1500);
      } else {
        submitBtn.disabled = false;
        submitBtn.innerHTML = "Login";

        showToast(result.message, "error");
      }
    } catch (err) {
      console.error(err);

      submitBtn.disabled = false;
      submitBtn.innerHTML = "Login";

      showToast("Unable to connect to server.", "error");
    }
  });

function togglePasswordVisibility(event) {
  const button = event.currentTarget;
  const input = button.previousElementSibling;
  const icon = button.querySelector("i");

  if (input.type === "password") {
    input.type = "text";
    icon.classList.remove("bi-eye-slash");
    icon.classList.add("bi-eye");
  } else {
    input.type = "password";
    icon.classList.remove("bi-eye");
    icon.classList.add("bi-eye-slash");
  }
}
