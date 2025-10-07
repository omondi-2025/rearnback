document.getElementById("depositForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const phone = document.getElementById("phone").value.trim();
  const amount = document.getElementById("amount").value.trim();
  const messageEl = document.getElementById("message");

  messageEl.textContent = "Processing your deposit... ⏳";

  try {
    const response = await fetch("https://rearnback.onrender.com/deposit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone, amount }),
    });

    const data = await response.json();
    if (response.ok && data.redirect_url) {
      window.location.href = data.redirect_url;
    } else {
      messageEl.textContent = "⚠️ " + (data.message || "Failed to initiate deposit.");
    }
  } catch (err) {
    messageEl.textContent = "❌ Network error. Try again.";
    console.error(err);
  }
});
