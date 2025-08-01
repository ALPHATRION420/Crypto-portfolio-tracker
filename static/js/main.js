let wallets = [];
let pieChart, historyChart;

window.onload = () => {
  loadWallets();
  showTab('overview');
};

function addWallet() {
  const address = document.getElementById("walletInput").value;
  if (address && !wallets.includes(address)) {
    wallets.push(address);
    saveWallets();
    renderWalletDropdown();
  }
}

function deleteWallet() {
  const selected = document.getElementById("walletDropdown").value;
  wallets = wallets.filter(w => w !== selected);
  saveWallets();
  renderWalletDropdown();
}

function saveWallets() {
  localStorage.setItem("wallets", JSON.stringify(wallets));
}

function loadWallets() {
  wallets = JSON.parse(localStorage.getItem("wallets")) || [];
  renderWalletDropdown();
  if (wallets.length) loadWallet();
}

function renderWalletDropdown() {
  const dropdown = document.getElementById("walletDropdown");
  dropdown.innerHTML = "";
  wallets.forEach(addr => {
    const opt = document.createElement("option");
    opt.value = addr;
    opt.text = addr;
    dropdown.add(opt);
  });
}

async function loadWallet() {
  const address = document.getElementById("walletDropdown").value;
  const res = await fetch("/api/wallet", {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ address })
  });
  const data = await res.json();
  document.getElementById("eth").textContent = data.eth_balance + " ETH";
  updateTokenTable(data.token_balances);
  drawPieChart(data.token_balances);
  loadHistory(data.token_balances.map(t => t.symbol));
}

function updateTokenTable(balances) {
  const tbody = document.querySelector("#tokenTable tbody");
  tbody.innerHTML = "";
  balances.forEach(t => {
    tbody.innerHTML += `<tr><td>${t.symbol}</td><td>${t.balance}</td></tr>`;
  });
}

function drawPieChart(balances) {
  const ctx = document.getElementById("chartCanvas").getContext("2d");
  if (pieChart) pieChart.destroy();
  pieChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: balances.map(b => b.symbol),
      datasets: [{
        data: balances.map(b => b.balance),
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
      }]
    }
  });
}

async function loadHistory(tokens) {
  const res = await fetch("/api/history", {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ tokens })
  });
  const historyData = await res.json();
  const ctx = document.getElementById("historyChart").getContext("2d");

  const datasets = Object.entries(historyData).map(([symbol, data]) => ({
    label: symbol,
    data: data.prices,
    borderColor: getColor(),
    fill: false,
    tension: 0.2
  }));

  if (historyChart) historyChart.destroy();
  historyChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: Array(historyData[tokens[0]].prices.length).fill().map((_, i) => i),
      datasets
    }
  });
}

function getColor() {
  return "#" + Math.floor(Math.random()*16777215).toString(16);
}

function showTab(tab) {
  document.querySelectorAll(".tab").forEach(div => div.style.display = "none");
  document.getElementById(tab).style.display = "block";
}
