let commandHistory = [];
let historyIndex = -1;
let isFlashing = false;

// Initialize Progress Bar segments
const stepContainer = document.getElementById('step-progress');
if (stepContainer) {
  for (let i = 1; i <= 15; i++) {
    const seg = document.createElement('div');
    seg.className = 'step-segment';
    seg.id = `seg-${i}`;
    stepContainer.appendChild(seg);
  }
}

function updateClock() {
  const clockEl = document.getElementById('digital-clock');
  if (clockEl) clockEl.innerText = new Date().toLocaleTimeString('en-US', { hour12: false });
}
setInterval(updateClock, 1000);

function flashSegments(stateClass) {
  isFlashing = true;
  document.querySelectorAll('.step-segment').forEach(s => s.classList.add(stateClass));
  setTimeout(() => {
    document.querySelectorAll('.step-segment').forEach(s => s.classList.remove(stateClass));
    isFlashing = false;
  }, 2000);
}

async function updateDashboard() {
  try {
    const response = await fetch(`stats.json?t=${Date.now()}`);
    const data = await response.json();

    const statusEl = document.getElementById('status-text');
    statusEl.innerText = data.status;
    statusEl.classList.remove('status-idle', 'status-active', 'status-error');
    if (data.status === "Idle") statusEl.classList.add('status-idle');
    else if (data.status.toLowerCase().includes("error")) statusEl.classList.add('status-error');
    else statusEl.classList.add('status-active');

    if (!isFlashing) {
      const stepMatch = data.status.match(/Step (\d+)\/15/);
      let currentStep = stepMatch ? parseInt(stepMatch[1]) : 0;
      document.querySelectorAll('.step-segment').forEach((seg, i) => {
        seg.classList.toggle('active', (i + 1) <= currentStep);
      });
    }

    updateBar('.cpu', data.cpu, `CPU: ${Math.round(data.cpu)}%`);
    updateBar('.ram', data.ram, `RAM: ${Math.round(data.ram)}%`);
    updateBar('.storage', data.storage, `DISK: ${Math.round(data.storage)}%`);
    const gVal = data.gpu === "N/A" ? 0 : data.gpu;
    updateBar('.network', gVal, `GPU: ${gVal}%`);
    updateBar('.cpu-temp', Math.min(data.cpu_temp, 100), `CPU TEMP: ${data.cpu_temp}°C`);
    updateBar('.gpu-temp', Math.min(data.gpu_temp, 100), `GPU TEMP: ${data.gpu_temp}°C`);

    if (data.cpu_temp >= 80 || data.gpu_temp >= 80) document.body.classList.add('thermal-meltdown');
    else document.body.classList.remove('thermal-meltdown');

    const logDisplay = document.getElementById('log-display');
    if (logDisplay && data.logs) {
      const isAtBottom = logDisplay.scrollHeight - logDisplay.scrollTop <= logDisplay.clientHeight + 30;
      logDisplay.innerHTML = data.logs.map(log => `<div>> ${log}</div>`).join('');
      if (isAtBottom) logDisplay.scrollTop = logDisplay.scrollHeight;
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

async function sendCommand(overridePrompt = null) {
  const input = document.getElementById('user-input');
  const prompt = overridePrompt || input.value.trim();
  if (!prompt) return;

  if (!overridePrompt && commandHistory[commandHistory.length - 1] !== prompt) {
    commandHistory.push(prompt);
  }
  historyIndex = commandHistory.length;

  input.disabled = true;
  document.getElementById('abort-btn').classList.remove('hidden');

  try {
    const res = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prompt })
    });
    const result = await res.json();
    const resBox = document.getElementById('response-box');
    resBox.classList.remove('hidden');
    document.getElementById('response-content').innerText = result.response;

    if (result.response.includes("ABORTED")) flashSegments('error');
    else flashSegments('success');
  } finally {
    input.value = "";
    input.disabled = false;
    document.getElementById('abort-btn').classList.add('hidden');
    input.focus();
  }
}

// NEW: Cleanup Logic
async function triggerCleanup() {
  const confirmAction = confirm("Initiate Workspace Audit?\n\nAnti Gravity will identify junk files and move them to an archive folder.");
  if (confirmAction) {
    const cleanupPrompt = "Perform a full system audit of the current directory. Identify test files, temporary scripts (p.py, hello.sh, etc.), and junk. Create a folder named 'archive_junk' and MOVE those files into it. Provide a report of what was moved.";
    sendCommand(cleanupPrompt);
  }
}

// Event Listeners
document.getElementById('send-btn').addEventListener('click', () => sendCommand());
document.getElementById('clear-btn').addEventListener('click', () => fetch('/clear', { method: 'POST' }));
document.getElementById('abort-btn').addEventListener('click', () => fetch('/abort', { method: 'POST' }));
document.getElementById('cleanup-btn').addEventListener('click', triggerCleanup);

document.getElementById('user-input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') sendCommand();
  else if (e.key === 'ArrowUp' && historyIndex > 0) { historyIndex--; e.target.value = commandHistory[historyIndex]; }
  else if (e.key === 'ArrowDown') {
    if (historyIndex < commandHistory.length - 1) { historyIndex++; e.target.value = commandHistory[historyIndex]; }
    else { historyIndex = commandHistory.length; e.target.value = ""; }
  }
});

setInterval(updateDashboard, 2000);
updateDashboard();