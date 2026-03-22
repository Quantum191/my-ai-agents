// --- STATE VARIABLES ---
let commandHistory = [];
let historyIndex = -1;

function updateClock() {
  const clockEl = document.getElementById('digital-clock');
  if (!clockEl) return;
  const now = new Date();
  clockEl.innerText = now.toLocaleTimeString('en-US', { hour12: false });
}

setInterval(updateClock, 1000);
updateClock();

async function updateDashboard() {
  try {
    const response = await fetch(`stats.json?t=${Date.now()}`);
    if (!response.ok) return;
    const data = await response.json();

    const statusEl = document.getElementById('status-text');
    if (statusEl && data.status) {
      statusEl.innerText = data.status;
      statusEl.classList.remove('status-idle', 'status-active', 'status-error');
      if (data.status === "Idle") statusEl.classList.add('status-idle');
      else if (data.status.toLowerCase().includes("error") || data.status.toLowerCase().includes("fail")) statusEl.classList.add('status-error');
      else statusEl.classList.add('status-active');
    }

    updateBar('.cpu', data.cpu, `CPU: ${Math.round(data.cpu)}%`);
    updateBar('.ram', data.ram, `RAM: ${Math.round(data.ram)}%`);
    updateBar('.storage', data.storage, `DISK: ${Math.round(data.storage)}%`);
    const gpuVal = data.gpu === "N/A" ? 0 : data.gpu;
    updateBar('.network', gpuVal, `GPU: ${gpuVal}%`);

    const logDisplay = document.getElementById('log-display');
    if (logDisplay && data.logs && data.logs.length > 0) {
      logDisplay.innerHTML = data.logs.map(log => `<div>> ${log}</div>`).join('');
      logDisplay.scrollTop = logDisplay.scrollHeight;
    }
  } catch (e) { }
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
  const abortBtn = document.getElementById('abort-btn');
  const resBox = document.getElementById('response-box');
  const resContent = document.getElementById('response-content');

  const prompt = input.value.trim();
  if (!prompt) return;

  if (commandHistory[commandHistory.length - 1] !== prompt) {
    commandHistory.push(prompt);
  }
  historyIndex = commandHistory.length;

  // UI Updates for Active State
  input.disabled = true;
  btn.disabled = true;
  abortBtn.classList.remove('hidden'); // SHOW ABORT BUTTON
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
      if (result.response === "MISSION ABORTED BY USER.") {
        resContent.innerHTML = `<span style="color: #ff9900;">WARNING: ${result.response}</span>`;
      } else if (result.error) {
        resContent.innerHTML = `<span style="color: #ff4444;">ERROR: ${result.error}</span>`;
      } else {
        resContent.innerHTML = `<span style="color: #39ff14;">${result.response}</span>`;
      }
    }
  } catch (e) {
    if (resBox && resContent) {
      resBox.classList.remove('hidden');
      resContent.innerHTML = `<span style="color: #ff4444;">CONNECTION ERROR.</span>`;
    }
  } finally {
    input.value = "";
    input.disabled = false;
    btn.disabled = false;
    abortBtn.classList.add('hidden'); // HIDE ABORT BUTTON
    input.focus();
  }
}

// NEW: Trigger the Abort Route
async function triggerAbort() {
  try {
    await fetch('/abort', { method: 'POST' });
    const resContent = document.getElementById('response-content');
    const resBox = document.getElementById('response-box');
    if (resBox && resContent) {
      resBox.classList.remove('hidden');
      resContent.innerHTML = `<span style="color: #ff0044;">Sending Abort Signal... Waiting for current step to finish.</span>`;
    }
  } catch (e) {
    console.error("Failed to send abort signal.");
  }
}

document.getElementById('send-btn').addEventListener('click', sendCommand);
document.getElementById('abort-btn').addEventListener('click', triggerAbort);

document.getElementById('user-input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    sendCommand();
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    if (commandHistory.length > 0 && historyIndex > 0) {
      historyIndex--;
      e.target.value = commandHistory[historyIndex];
    }
  } else if (e.key === 'ArrowDown') {
    e.preventDefault();
    if (historyIndex < commandHistory.length - 1) {
      historyIndex++;
      e.target.value = commandHistory[historyIndex];
    } else {
      historyIndex = commandHistory.length;
      e.target.value = "";
    }
  }
});

setInterval(updateDashboard, 2000);
updateDashboard();