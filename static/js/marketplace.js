async function loadMarketplace() {
  const response = await fetch("/api/marketplace");

  const data = await response.json();

  const table = document.getElementById("marketplaceTable");

  table.innerHTML = "";

  data.forEach((listing) => {
    table.innerHTML += `
      <tr>
        <td>${listing.seller}</td>
        <td>${listing.energy}</td>
        <td>Rs ${listing.price_per_kwh}</td>

        <td>
          <button
            class="btn btn-success"
            onclick="buyEnergy('${listing.seller}')"
          >
            Buy
          </button>
        </td>

      </tr>
    `;
  });
}

async function buyEnergy(seller) {
  const response = await fetch("/api/buy-energy", {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      seller,
    }),
  });

  const result = await response.json();

  alert(result.message);

  loadMarketplace();
}

loadMarketplace();
