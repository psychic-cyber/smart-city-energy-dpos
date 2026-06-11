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

loadUserDashboard();

async function sellEnergy() {
  try {
    const response = await fetch("/api/sell-energy", {
      method: "POST",
    });

    const result = await response.json();

    if (result.success) {
      alert(`Energy Sold!\nRevenue: Rs ${result.earned}`);

      loadUserDashboard();
    } else {
      alert(result.message);
    }
  } catch (error) {
    console.error(error);
  }
}
