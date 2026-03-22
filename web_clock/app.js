// app.js
setInterval(() => {
  const now = new Date();
  const timeString = now.toLocaleTimeString('en-US', { hour12: false });
  document.getElementById('clock').innerText = timeString;
}, 1000);