async function updateDashboard() {
  try {
    const response = await fetch(`stats.json?t=${Date.now()}`);
    if (!response.ok) return;
    const data = await response.json();

    async function updateDashboard() {
      try {
        const response = await fetch(`stats.json?t=${Date.now()}`);
        if (!response.ok) return;
        const data = await response.json();

        // Update Hardware
        updateBar('.cpu', data.cpu, `CPU: ${Math.round(data.cpu)}%`);
        updateBar('.ram', data.ram, `RAM: ${Math.round(data.ram)}%`);
        updateBar('.storage', data.storage, `DISK: ${Math.round(data.storage)}%`);

        // Update Status Text (The "Step 1/15" or "Idle")
        const statusEl = document.getElementById('status-text');
        if (statusEl && data.status) {
          statusEl.innerText = data.status;
          // Change color if working
          statusEl.style.color = data.status === "Idle" ? "#39ff14" : "#00d2ff";
        }

        // Update Logs
        const logDisplay = document.getElementById('log-display');
        if (logDisplay && data.logs) {
          logDisplay.innerHTML = data.logs.map(log => `<div>> ${log}</div>`).join('');
        }
      } catch (e) { console.error("Sync error"); }
    }

    // ... (Keep your existing updateBar and sendCommand functions)

    // Update Hardware
    updateBar('.cpu', data.cpu, `CPU: ${Math.round(data.cpu)}%`);
    updateBar('.ram', data.ram, `RAM: ${Math.round(data.ram)}%`);
    updateBar('.storage', data.storage, `DISK: ${Math.round(data.storage)}%`);

    const gpuVal = data.gpu === "N/A" ? 0 : data.gpu;
    updateBar('.network', gpuVal, `GPU: ${gpuVal}%`);

    // Update Logs
    const logDisplay = document.getElementById('log-display');
    if (logDisplay && data.logs) {
      logDisplay.innerHTML = data.logs.map(log => `<div>> ${log}</div>`).join('');
    }

    document.getElementById('status-text').innerText = "ONLINE";
    document.getElementById('status-text').style.color = "#39ff14";
  } catch (e) {
    document.getElementById('status-text').innerText = "OFFLINE";
    document.getElementById('status-text').style.color = "red";
  }
}

function updateBar(selector, value, label) {
  const card = document.querySelector(selector);
  if (card) {
    card.querySelector('.fill').style.width = value + '%';
    card.querySelector('h3').innerText = label;
  }
}

// COMMAND LOGIC
async function sendCommand() {
  const input = document.getElementById('user-input');
  const btn = document.getElementById('send-btn');
  const prompt = input.value;
  if (!prompt) return;

  // UI Feedback
  input.disabled = true;
  btn.disabled = true;
  btn.innerText = "...";

  try {
    const response = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prompt })
    });
    const result = await response.json();
    // You can use an alert or log to see the final answer
    console.log("Agent:", result.response);
  } catch (e) {
    console.error("Failed to send command:", e);
  } finally {
    input.value = "";
    input.disabled = false;
    btn.disabled = false;
    btn.innerText = "EXECUTE";
    input.focus();
  }
}

document.getElementById('send-btn').addEventListener('click', sendCommand);
document.getElementById('user-input').addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendCommand();
});

setInterval(updateDashboard, 2000);
updateDashboard();