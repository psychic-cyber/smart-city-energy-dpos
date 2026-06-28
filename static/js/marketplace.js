let marketplaceRequests = [];

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

function showAlert(message, type = "success") {
  const alert = document.getElementById("marketplaceAlert");
  alert.innerHTML = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
    ${escapeHtml(message)}
    <button type="button" class="btn-close" aria-label="Close" onclick="this.parentElement.remove()"></button>
  </div>`;
}

async function loadMarketplace() {
  try {
    const [listingResponse, requestResponse] = await Promise.all([
      fetch("/api/marketplace"),
      fetch("/api/marketplace/requests"),
    ]);
    if (!listingResponse.ok || !requestResponse.ok) throw new Error("Unable to load marketplace");

    const listings = await listingResponse.json();
    marketplaceRequests = await requestResponse.json();
    renderRequests(marketplaceRequests);
    renderListings(listings);
  } catch (error) {
    showAlert(error.message, "danger");
  }
}

function renderListings(listings) {
  const container = document.getElementById("marketplaceListings");
  if (!listings.length) {
    container.innerHTML = `<div class="col-12"><div class="alert alert-info mb-0">
      No energy is available right now. Create an energy request below.
    </div></div>`;
    return;
  }

  container.innerHTML = listings.map((listing, index) => {
    const available = Number(listing.energy);
    const price = Number(listing.price_per_kwh);
    const matched = marketplaceRequests.some(
      (request) => request.status === "Matched" && request.matching_seller === listing.seller,
    );
    return `<div class="col-xl-4 col-md-6">
      <div class="data-panel marketplace-card ${matched ? "matching-listing" : ""}">
        <div class="d-flex justify-content-between align-items-start mb-3">
          <div>
            <small class="text-secondary">Seller</small>
            <h4 class="mb-0">${escapeHtml(listing.seller)}</h4>
          </div>
          ${matched ? '<span class="badge bg-warning text-dark">Request Match</span>' : ""}
        </div>

        <div class="row mb-3">
          <div class="col-6">
            <small class="text-secondary">Available Energy</small>
            <div class="fs-4 fw-bold text-success" id="available-${index}">${formatNumber(available)} kWh</div>
          </div>
          <div class="col-6">
            <small class="text-secondary">Price per kWh</small>
            <div class="fs-4 fw-bold text-info">Rs ${formatNumber(price)}</div>
          </div>
        </div>

        <label class="form-label" for="quantity-${index}">Quantity</label>
        <div class="input-group quantity-selector mb-2">
          <button class="btn btn-secondary" type="button" onclick="changeQuantity(${index}, -1)">−</button>
          <input
            id="quantity-${index}"
            class="form-control text-center"
            type="number"
            value="1"
            min="1"
            max="${available}"
            step="1"
            data-price="${price}"
            data-seller="${escapeHtml(listing.seller)}"
            oninput="updatePurchaseCard(${index})"
          />
          <button class="btn btn-primary" type="button" onclick="changeQuantity(${index}, 1)">+</button>
        </div>
        <div id="quantity-error-${index}" class="text-danger small mb-3" aria-live="polite"></div>

        <div class="d-flex justify-content-between align-items-center border-top border-secondary pt-3 mb-3">
          <span>Total Price</span>
          <strong class="fs-4 text-warning" id="total-${index}">Rs ${formatNumber(price)}</strong>
        </div>
        <button id="buy-${index}" class="btn btn-success w-100" onclick="buyEnergy(${index})">
          Buy Energy
        </button>
      </div>
    </div>`;
  }).join("");
}

function validateQuantity(input) {
  const raw = input.value.trim();
  const quantity = Number(raw);
  const maximum = Number(input.max);
  if (raw === "" || !Number.isFinite(quantity)) return "Enter a quantity";
  if (!Number.isInteger(quantity)) return "Quantity must be a whole number";
  if (quantity < 1) return "Quantity must be at least 1 kWh";
  if (quantity > maximum) return `Only ${formatNumber(maximum)} kWh is available`;
  return "";
}

function updatePurchaseCard(index) {
  const input = document.getElementById(`quantity-${index}`);
  const error = validateQuantity(input);
  const quantity = Number(input.value);
  const total = error ? 0 : quantity * Number(input.dataset.price);
  document.getElementById(`quantity-error-${index}`).textContent = error;
  document.getElementById(`total-${index}`).textContent = `Rs ${formatNumber(total)}`;
  document.getElementById(`buy-${index}`).disabled = Boolean(error);
  input.classList.toggle("is-invalid", Boolean(error));
}

function changeQuantity(index, delta) {
  const input = document.getElementById(`quantity-${index}`);
  const current = Number(input.value);
  const maximum = Number(input.max);
  const next = Math.min(maximum, Math.max(1, (Number.isInteger(current) ? current : 1) + delta));
  input.value = next;
  updatePurchaseCard(index);
}

async function buyEnergy(index) {
  const input = document.getElementById(`quantity-${index}`);
  updatePurchaseCard(index);
  if (validateQuantity(input)) return;

  const button = document.getElementById(`buy-${index}`);
  button.disabled = true;
  button.textContent = "Purchasing…";
  try {
    const response = await fetch("/api/buy-energy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        seller: input.dataset.seller,
        quantity: Number(input.value),
      }),
    });
    const result = await response.json();
    if (!result.success) {
      showAlert(result.message, "danger");
      return;
    }
    showAlert(`${result.message}. Remaining: ${formatNumber(result.data.remaining_amount)} kWh.`);
    await loadMarketplace();
  } catch (error) {
    showAlert("Purchase could not be completed. Please try again.", "danger");
  } finally {
    button.disabled = false;
    button.textContent = "Buy Energy";
  }
}

function renderRequests(requests) {
  const table = document.getElementById("marketplaceRequests");
  if (!requests.length) {
    table.innerHTML = '<tr><td colspan="5" class="text-center text-secondary">No requests yet</td></tr>';
    return;
  }
  table.innerHTML = requests.map((request) => {
    const matched = request.status === "Matched";
    const badge = request.status === "Completed" ? "success" : matched ? "warning text-dark" : "primary";
    return `<tr class="${matched ? "table-warning" : ""}">
      <td>${escapeHtml(request.buyer)}</td>
      <td>${formatNumber(request.requested_energy)} kWh</td>
      <td>${request.maximum_price_per_kwh == null ? "Any" : `Rs ${formatNumber(request.maximum_price_per_kwh)}`}</td>
      <td>${escapeHtml(request.message) || "—"}</td>
      <td><span class="badge bg-${badge}">${escapeHtml(request.status)}</span>
        ${matched ? `<div class="small mt-1">Seller: ${escapeHtml(request.matching_seller)}</div>` : ""}
      </td>
    </tr>`;
  }).join("");
}

document.getElementById("energyRequestForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const energy = document.getElementById("requestedEnergy").value;
  const maximumPrice = document.getElementById("maximumPrice").value;
  if (!Number.isInteger(Number(energy)) || Number(energy) < 1) {
    showAlert("Requested energy must be a whole number of at least 1 kWh.", "danger");
    return;
  }
  if (maximumPrice !== "" && Number(maximumPrice) <= 0) {
    showAlert("Maximum price must be greater than zero.", "danger");
    return;
  }

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
  showAlert(result.message, result.success ? "success" : "danger");
  if (result.success) {
    event.target.reset();
    await loadMarketplace();
  }
});

loadMarketplace();
