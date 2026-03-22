function updateClock() {
  const clockEl = document.getElementById('digital-clock');
  if (clockEl) clockEl.innerText = new Date().toLocaleTimeString('en-US', { hour12: false });
}
setInterval(updateClock, 1000);

async function updateDashboard() {
  try {
    const response = await fetch(`/stats.json?t=${Date.now()}`);
    const data = await response.json();

    // Update Labels
    document.getElementById('cpu-label').innerText = `CPU_LOAD: ${Math.round(data.cpu)}%`;
    document.getElementById('ram-label').innerText = `MEM_USED: ${Math.round(data.ram)}%`;
    document.getElementById('gpu-label').innerText = `4070_LOAD: ${data.gpu}%`;
    document.getElementById('temp-label').innerText = `CORE_TEMP: ${data.gpu_temp}°C`;

    // Update Progress Bars
    document.getElementById('cpu-fill').style.width = data.cpu + '%';
    document.getElementById('ram-fill').style.width = data.ram + '%';
    document.getElementById('gpu-fill').style.width = data.gpu + '%';
    document.getElementById('temp-fill').style.width = Math.min(data.gpu_temp, 100) + '%';

    // Update Logs
    const logDisplay = document.getElementById('log-display');
    if (data.logs) {
      logDisplay.innerHTML = data.logs.map(log => `<div>> ${log}</div>`).join('');
      logDisplay.scrollTop = logDisplay.scrollHeight;
    }
  } catch (e) {
    console.warn("Dashboard sync pending...");
  }
}

setInterval(updateDashboard, 2000);
updateDashboard();