let districtChart;
let entityChart;

async function loadAnalytics() {
  const districts = await (await fetch("/api/districts")).json();

  const transactions = await (await fetch("/api/transactions")).json();

  const labels = districts.map((d) => d._id);
  const energy = districts.map((d) => Math.round(d.energy));

  if (districtChart) districtChart.destroy();

  districtChart = new Chart(document.getElementById("districtChart"), {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Energy Usage",
          data: energy,
          backgroundColor: "#38bdf8",
        },
      ],
    },
  });

  const counts = {};

  transactions.forEach((t) => {
    counts[t.entity_type] = (counts[t.entity_type] || 0) + 1;
  });

  if (entityChart) entityChart.destroy();

  entityChart = new Chart(document.getElementById("entityChart"), {
    type: "pie",
    data: {
      labels: Object.keys(counts),
      datasets: [
        {
          data: Object.values(counts),
        },
      ],
    },
  });
}

loadAnalytics();
