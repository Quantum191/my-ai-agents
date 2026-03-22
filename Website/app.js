async function updateDashboard() {
  try {
    // Cache buster forces a fresh pull from the daemon
    const response = await fetch(`stats.json?t=${Date.now()}`);
    if (!response.ok) throw new Error('Offline');

    const data = await response.json();

    // Update Progress Bars and Titles
    updateMetric('.cpu', data.cpu, `CPU LOAD: ${Math.round(data.cpu)}%`);
    updateMetric('.ram', data.ram, `MEMORY: ${Math.round(data.ram)}%`);
    updateMetric('.storage', data.storage, `DISK: ${Math.round(data.storage)}% USED`);

    // Handle GPU N/A case
    const gpuVal = data.gpu === "N/A" ? 0 : data.gpu;
    updateMetric('.network', gpuVal, `GPU LOAD: ${gpuVal}%`);

    // Update Log Stream
    const logDisplay = document.getElementById('log-display');
    if (logDisplay && data.logs) {
      logDisplay.innerHTML = data.logs.map(log => `<div>> ${log}</div>`).join('');
    }

    document.getElementById('status-text').innerText = "ONLINE";
    document.getElementById('status-text').style.color = "#39ff14";

  } catch (error) {
    document.getElementById('status-text').innerText = "CONNECTION LOST";
    document.getElementById('status-text').style.color = "red";
  }
}

function updateMetric(selector, value, text) {
  const card = document.querySelector(selector);
  if (card) {
    const fill = card.querySelector('.fill');
    const title = card.querySelector('h3');
    if (fill) fill.style.width = value + '%';
    if (title) title.innerText = text;
  }
}

setInterval(updateDashboard, 2000);
updateDashboard();