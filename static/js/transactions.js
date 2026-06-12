async function loadTransactions() {
  const transactions = await (await fetch("/api/transactions")).json();

  const table = document.getElementById("transactionsTable");

  table.innerHTML = "";

  transactions.forEach((t) => {
    table.innerHTML += `
      <tr>
        <td>${t.username}</td>
        <td>${t.buyer}</td>
        <td>${t.energy_sold}</td>
        <td>${t.revenue}</td>
        <td>${t.status}</td>
      </tr>
    `;
  });
}

loadTransactions();
