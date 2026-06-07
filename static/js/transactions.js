async function loadTransactions() {
  const transactions = await (await fetch("/api/transactions")).json();

  const table = document.getElementById("transactionsTable");

  table.innerHTML = "";

  transactions.slice(0, 20).forEach((t) => {
    table.innerHTML += `
      <tr>
        <td>${t.entity_id}</td>
        <td>${t.entity_type}</td>
        <td>${t.district}</td>
        <td>${t.bill_amount}</td>
      </tr>
      `;
  });
}

loadTransactions();
