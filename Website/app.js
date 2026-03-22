async function updateDashboard() {
  try {
    const response = await fetch(`stats.json?t=${Date.now()}`);
    if (!response.ok) return;
    const data = await response.json();

    // Status Text
    const statusEl = document.getElementById('status-text');
    if (statusEl && data.status) {
      statusEl.innerText = data.status;
      statusEl.style.color = data.status === "Idle" ? "#39ff14" : "#00d2ff";
    }

    // Hardware Bars
    updateBar('.cpu', data.cpu, `CPU: ${Math.round(data.cpu)}%`);
    updateBar('.ram', data.ram, `RAM: ${Math.round(data.ram)}%`);
    updateBar('.storage', data.storage, `DISK: ${Math.round(data.storage)}%`);

    const gpuVal = data.gpu === "N/A" ? 0 : data.gpu;
    updateBar('.network', gpuVal, `GPU: ${gpuVal}%`);

    // Thought Stream (Logs)
    const logDisplay = document.getElementById('log-display');
    if (logDisplay && data.logs) {
      logDisplay.innerHTML = data.logs.map(log => `<div>${log}</div>`).join('');
      // Keep scrolled to the bottom
      logDisplay.scrollTop = logDisplay.scrollHeight;
    }
  } catch (e) {
    console.error("Dashboard Sync Error:", e);
  }
}

function updateBar(selector, value, label) {
  const card = document.querySelector(selector);
  if (card) {
    const fill = card.querySelector('.fill');
    const title = card.querySelector('h3');
    if (fill) fill.style.width = value + '%';
    if (title) title.innerText = label;
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
  if (resBox) resBox.classList.add('hidden');

  try {
    const response = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prompt })
    });
    const result = await response.json();

    if (resBox && resContent) {
      resBox.classList.remove('hidden');
      if (result.error) {
        resContent.innerHTML = `<span style="color: #ff4444;">ERROR: ${result.error}</span>`;
      } else {
        resContent.innerHTML = `<span style="color: #39ff14;">${result.response}</span>`;
      }
    }
  } catch (e) {
    if (resBox && resContent) {
      resBox.classList.remove('hidden');
      resContent.innerHTML = `<span style="color: #ff4444;">CONNECTION ERROR: App Server offline.</span>`;
    }
  } finally {
    input.value = "";
    input.disabled = false;
    btn.disabled = false;
    input.focus();
  }
}

// Event Listeners
document.getElementById('send-btn').addEventListener('click', sendCommand);
document.getElementById('user-input').addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendCommand();
});

setInterval(updateDashboard, 2000);
updateDashboard();