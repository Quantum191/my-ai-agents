async function updateDashboard() {
  try {
    const response = await fetch(`stats.json?t=${Date.now()}`);
    if (!response.ok) return;
    const data = await response.json();

    // 1. Update Status Text
    const statusEl = document.getElementById('status-text');
    if (statusEl) {
      statusEl.innerText = data.status || "Idle";
      statusEl.style.color = data.status === "Idle" ? "#39ff14" : "#00d2ff";
    }

    // 2. Update Hardware
    updateBar('.cpu', data.cpu, `CPU: ${Math.round(data.cpu)}%`);
    updateBar('.ram', data.ram, `RAM: ${Math.round(data.ram)}%`);
    updateBar('.storage', data.storage, `DISK: ${Math.round(data.storage)}%`);

    const gpuVal = data.gpu === "N/A" ? 0 : data.gpu;
    updateBar('.network', gpuVal, `GPU: ${gpuVal}%`);

    // 3. Update the Thought Stream (Logs)
    const logDisplay = document.getElementById('log-display');
    if (logDisplay && data.logs && data.logs.length > 0) {
      logDisplay.innerHTML = data.logs.map(log => `<div>> ${log}</div>`).join('');
      // Auto-scroll to bottom
      logDisplay.scrollTop = logDisplay.scrollHeight;
    }
  } catch (e) { console.log("Waiting for data..."); }
}

function updateBar(selector, value, label) {
  const card = document.querySelector(selector);
  if (card) {
    card.querySelector('.fill').style.width = value + '%';
    card.querySelector('h3').innerText = label;
  }
}

async function sendCommand() {
  const input = document.getElementById('user-input');
  const btn = document.getElementById('send-btn');
  const resBox = document.getElementById('response-box');
  const resContent = document.getElementById('response-content');

  const prompt = input.value.trim();
  if (!prompt) return;

  input.disabled = true;
  btn.disabled = true;
  resBox.classList.add('hidden');

  try {
    const response = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prompt })
    });
    const result = await response.json();
    resBox.classList.remove('hidden');
    resContent.innerText = result.response || "Task Complete.";
  } catch (e) {
    resBox.classList.remove('hidden');
    resContent.innerText = "Error: Could not reach Agent.";
  } finally {
    input.value = "";
    input.disabled = false;
    btn.disabled = false;
    input.focus();
  }
}

document.getElementById('send-btn').addEventListener('click', sendCommand);
document.getElementById('user-input').addEventListener('keypress', (e) => { if (e.key === 'Enter') sendCommand(); });

setInterval(updateDashboard, 2000);
updateDashboard();