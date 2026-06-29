let marketplaceRequests = [];
let buyModalState = {
  seller: "",
  price: 0,
  available: 0,
};

let buyEnergyModal = null;

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatNumber(value) {
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 });
}

function showToast(message, type = "success") {
  const container = document.getElementById("toastContainer");
  const toastId = `toast-${Date.now()}`;
  const typeClass =
    type === "danger"
      ? "marketplace-toast--error"
      : type === "warning"
        ? "marketplace-toast--warning"
        : type === "info"
          ? "marketplace-toast--info"
          : "marketplace-toast--success";
  const iconClass =
    type === "danger"
      ? "bi-exclamation-octagon-fill"
      : type === "warning"
        ? "bi-exclamation-triangle-fill"
        : type === "info"
          ? "bi-info-circle-fill"
          : "bi-check-circle-fill";

  container.insertAdjacentHTML(
    "beforeend",
    `<div id="${toastId}" class="toast marketplace-toast ${typeClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex align-items-center">
        <i class="bi ${iconClass} marketplace-toast__icon"></i>
        <div class="toast-body marketplace-toast__body">${escapeHtml(message)}</div>
        <button type="button" class="btn-close btn-close-white me-2" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>`,
  );

  const toastElement = document.getElementById(toastId);
  const toast = bootstrap.Toast.getOrCreateInstance(toastElement, {
    delay: 4500,
  });
  toast.show();
  toastElement.addEventListener("hidden.bs.toast", () => toastElement.remove());
}

function updateMarketSummary(summary) {
  document.getElementById("summaryActiveListings").innerText =
    summary.active_listings ?? 0;
  document.getElementById("summaryCompletedTrades").innerText =
    summary.completed_trades ?? 0;
  document.getElementById("summaryEnergyTraded").innerText = `${formatNumber(
    summary.total_energy_traded ?? 0,
  )} kWh`;
  document.getElementById("summaryMarketVolume").innerText = `Rs ${formatNumber(
    summary.market_volume ?? 0,
  )}`;
  document.getElementById("summaryAveragePrice").innerText = `Rs ${formatNumber(
    summary.average_price ?? 0,
  )}`;
  document.getElementById("summaryHighestPrice").innerText = `Rs ${formatNumber(
    summary.highest_price ?? 0,
  )}`;
  document.getElementById("summaryLowestPrice").innerText = `Rs ${formatNumber(
    summary.lowest_price ?? 0,
  )}`;
}

function updateUserStats(stats) {
  document.getElementById("userEnergyBought").innerText = `${formatNumber(
    stats.total_energy_bought ?? 0,
  )} kWh`;
  document.getElementById("userEnergySold").innerText = `${formatNumber(
    stats.total_energy_sold ?? 0,
  )} kWh`;
  document.getElementById("userCompletedTrades").innerText =
    stats.completed_trades ?? 0;
  document.getElementById("userTotalRevenue").innerText = `Rs ${formatNumber(
    stats.total_revenue ?? 0,
  )}`;
  document.getElementById("userTotalSpending").innerText = `Rs ${formatNumber(
    stats.total_spending ?? 0,
  )}`;
  document.getElementById("userActiveListings").innerText =
    stats.active_listings ?? 0;
}

async function loadMarketSummary() {
  const response = await fetch("/api/marketplace/summary");
  if (!response.ok) {
    throw new Error("Unable to load marketplace summary");
  }
  updateMarketSummary(await response.json());
}

async function loadUserMarketplaceStats() {
  const response = await fetch("/api/user/marketplace-stats");
  if (response.status === 401) {
    return;
  }
  if (!response.ok) {
    throw new Error("Unable to load user marketplace statistics");
  }
  updateUserStats(await response.json());
}

async function loadMarketplaceListings() {
  const [listingResponse, requestResponse] = await Promise.all([
    fetch("/api/marketplace"),
    fetch("/api/marketplace/requests"),
  ]);

  if (!listingResponse.ok || !requestResponse.ok) {
    throw new Error("Unable to load marketplace listings");
  }

  marketplaceRequests = await requestResponse.json();
  renderRequests(marketplaceRequests);
  renderListings(await listingResponse.json());
}

async function refreshMarketplaceData() {
  try {
    await Promise.all([
      loadMarketSummary(),
      loadUserMarketplaceStats(),
      loadMarketplaceListings(),
    ]);
  } catch (error) {
    showToast(error.message, "danger");
  }
}

function renderListings(listings) {
  const container = document.getElementById("marketplaceListings");

  if (!listings.length) {
    container.innerHTML = `<div class="col-12"><div class="marketplace-empty-state">
      <i class="bi bi-inbox marketplace-empty-state__icon"></i>
      <p class="marketplace-empty-state__title">No listings available</p>
      <p class="marketplace-empty-state__text">Create a listing or submit an energy request below.</p>
    </div></div>`;
    return;
  }

  container.innerHTML = listings
    .map((listing) => {
      const available = Number(listing.energy);
      const price = Number(listing.price_per_kwh);
      const matched = marketplaceRequests.some(
        (request) =>
          request.status === "Matched" &&
          request.matching_seller === listing.seller,
      );
      const listingData = encodeURIComponent(JSON.stringify(listing));

      return `<div class="col-xl-4 col-lg-6">
      <article class="marketplace-listing-card ${matched ? "marketplace-listing-card--matched" : ""}">
        <div class="marketplace-listing-card__header">
          <div class="marketplace-listing-card__seller">
            <span class="marketplace-listing-card__label">Seller</span>
            <h3 class="marketplace-listing-card__name">${escapeHtml(listing.seller)}</h3>
          </div>
          ${matched ? '<span class="marketplace-badge marketplace-badge--match"><i class="bi bi-stars"></i> Request Match</span>' : ""}
        </div>

        <div class="marketplace-listing-card__metrics">
          <div class="marketplace-listing-card__metric">
            <span class="marketplace-listing-card__label"><i class="bi bi-lightning-charge"></i> Available</span>
            <p class="marketplace-listing-card__metric-value marketplace-listing-card__metric-value--green">${formatNumber(available)} kWh</p>
          </div>
          <div class="marketplace-listing-card__metric">
            <span class="marketplace-listing-card__label"><i class="bi bi-tag"></i> Price / kWh</span>
            <p class="marketplace-listing-card__metric-value marketplace-listing-card__metric-value--blue">Rs ${formatNumber(price)}</p>
          </div>
        </div>

        <div class="marketplace-listing-card__total">
          <span class="marketplace-listing-card__label">Listing Total</span>
          <strong class="marketplace-listing-card__total-value">Rs ${formatNumber(available * price)}</strong>
        </div>

        <button
          class="btn marketplace-btn-primary w-100 open-buy-modal-btn"
          type="button"
          data-listing="${listingData}"
        >
          <i class="bi bi-cart-plus"></i>
          Buy Energy
        </button>
      </article>
    </div>`;
    })
    .join("");

  container.querySelectorAll(".open-buy-modal-btn").forEach((button) => {
    button.addEventListener("click", () => {
      openBuyModal(JSON.parse(decodeURIComponent(button.dataset.listing)));
    });
  });
}

function validateModalQuantity() {
  const input = document.getElementById("modalQuantity");
  const raw = input.value.trim();
  const quantity = Number(raw);
  const maximum = buyModalState.available;

  if (raw === "" || !Number.isFinite(quantity)) {
    return "Enter a quantity";
  }
  if (!Number.isInteger(quantity)) {
    return "Quantity must be a whole number";
  }
  if (quantity < 1) {
    return "Quantity must be at least 1 kWh";
  }
  if (quantity > maximum) {
    return `Only ${formatNumber(maximum)} kWh is available`;
  }
  return "";
}

function updateBuyModalTotals() {
  const input = document.getElementById("modalQuantity");
  const error = validateModalQuantity();
  const quantity = Number(input.value);
  const total = error ? 0 : quantity * buyModalState.price;

  document.getElementById("modalQuantityError").textContent = error;
  document.getElementById("modalTotalCost").textContent = `Rs ${formatNumber(total)}`;
  document.getElementById("confirmPurchaseBtn").disabled = Boolean(error);
  input.classList.toggle("is-invalid", Boolean(error));
}

function changeModalQuantity(delta) {
  const input = document.getElementById("modalQuantity");
  const current = Number(input.value);
  const maximum = buyModalState.available;
  const next = Math.min(
    maximum,
    Math.max(1, (Number.isInteger(current) ? current : 1) + delta),
  );
  input.value = next;
  updateBuyModalTotals();
}

function openBuyModal(listing) {
  buyModalState = {
    seller: listing.seller,
    price: Number(listing.price_per_kwh),
    available: Number(listing.energy),
  };

  document.getElementById("modalSeller").innerText = listing.seller;
  document.getElementById("modalAvailable").innerText = `${formatNumber(
    buyModalState.available,
  )} kWh`;
  document.getElementById("modalPrice").innerText = `Rs ${formatNumber(
    buyModalState.price,
  )}`;

  const quantityInput = document.getElementById("modalQuantity");
  quantityInput.max = buyModalState.available;
  quantityInput.value = 1;
  updateBuyModalTotals();

  buyEnergyModal.show();
}

async function confirmPurchase() {
  updateBuyModalTotals();
  if (validateModalQuantity()) {
    return;
  }

  const button = document.getElementById("confirmPurchaseBtn");
  const quantity = Number(document.getElementById("modalQuantity").value);

  button.disabled = true;
  button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Purchasing…';

  try {
    const response = await fetch("/api/buy-energy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        seller: buyModalState.seller,
        quantity,
      }),
    });
    const result = await response.json();

    if (!result.success) {
      showToast(result.message, "danger");
      return;
    }

    buyEnergyModal.hide();

    const remaining = result.data?.remaining_amount ?? 0;
    const status = result.data?.listing_status ?? "Available";
    const completionMessage =
      status === "Sold"
        ? `${result.message} Listing fully sold.`
        : `${result.message} Remaining: ${formatNumber(remaining)} kWh.`;

    showToast(completionMessage, "success");
    await refreshMarketplaceData();
  } catch (error) {
    showToast("Purchase could not be completed. Please try again.", "danger");
  } finally {
    button.disabled = false;
    button.innerHTML = '<i class="bi bi-bag-check"></i> Confirm Purchase';
    updateBuyModalTotals();
  }
}

function renderRequests(requests) {
  const table = document.getElementById("marketplaceRequests");

  if (!requests.length) {
    table.innerHTML =
      '<tr><td colspan="5" class="marketplace-table-empty">No requests yet</td></tr>';
    return;
  }

  table.innerHTML = requests
    .map((request) => {
      const matched = request.status === "Matched";
      const badgeClass =
        request.status === "Completed"
          ? "marketplace-badge--completed"
          : matched
            ? "marketplace-badge--match"
            : "marketplace-badge--open";

      return `<tr class="marketplace-table-row ${matched ? "marketplace-table-row--matched" : ""}">
      <td>${escapeHtml(request.buyer)}</td>
      <td>${formatNumber(request.requested_energy)} kWh</td>
      <td>${request.maximum_price_per_kwh == null ? "Any" : `Rs ${formatNumber(request.maximum_price_per_kwh)}`}</td>
      <td class="marketplace-table-message">${escapeHtml(request.message) || "—"}</td>
      <td>
        <span class="marketplace-badge ${badgeClass}">${escapeHtml(request.status)}</span>
        ${matched ? `<div class="marketplace-table-match">Seller: ${escapeHtml(request.matching_seller)}</div>` : ""}
      </td>
    </tr>`;
    })
    .join("");
}

document.getElementById("createListingForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const energy = document.getElementById("listingEnergy").value;
  const price = document.getElementById("listingPrice").value;
  const button = document.getElementById("createListingBtn");

  if (!Number.isInteger(Number(energy)) || Number(energy) < 1) {
    showToast("Energy must be a whole number of at least 1 kWh.", "danger");
    return;
  }
  if (Number(price) <= 0) {
    showToast("Price must be greater than zero.", "danger");
    return;
  }

  button.disabled = true;

  try {
    const response = await fetch("/api/create-listing", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ energy: Number(energy), price: Number(price) }),
    });
    const result = await response.json();

    showToast(result.message, result.success ? "success" : "danger");

    if (result.success) {
      event.target.reset();
      await refreshMarketplaceData();
    }
  } catch (error) {
    showToast("Listing could not be created. Please try again.", "danger");
  } finally {
    button.disabled = false;
  }
});

document.getElementById("energyRequestForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const energy = document.getElementById("requestedEnergy").value;
  const maximumPrice = document.getElementById("maximumPrice").value;

  if (!Number.isInteger(Number(energy)) || Number(energy) < 1) {
    showToast("Requested energy must be a whole number of at least 1 kWh.", "danger");
    return;
  }
  if (maximumPrice !== "" && Number(maximumPrice) <= 0) {
    showToast("Maximum price must be greater than zero.", "danger");
    return;
  }

  try {
    const response = await fetch("/api/marketplace/requests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        requested_energy: Number(energy),
        maximum_price_per_kwh: maximumPrice === "" ? null : Number(maximumPrice),
        message: document.getElementById("requestMessage").value,
      }),
    });
    const result = await response.json();

    showToast(result.message, result.success ? "success" : "danger");

    if (result.success) {
      event.target.reset();
      await refreshMarketplaceData();
    }
  } catch (error) {
    showToast("Request could not be submitted. Please try again.", "danger");
  }
});

document.getElementById("refreshMarketplaceBtn").addEventListener("click", refreshMarketplaceData);
document.getElementById("modalQuantity").addEventListener("input", updateBuyModalTotals);
document.getElementById("modalQuantityDecrease").addEventListener("click", () => {
  changeModalQuantity(-1);
});
document.getElementById("modalQuantityIncrease").addEventListener("click", () => {
  changeModalQuantity(1);
});
document.getElementById("confirmPurchaseBtn").addEventListener("click", confirmPurchase);

document.addEventListener("DOMContentLoaded", () => {
  buyEnergyModal = new bootstrap.Modal(document.getElementById("buyEnergyModal"));
  refreshMarketplaceData();
});
