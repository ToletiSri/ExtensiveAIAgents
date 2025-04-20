const API_BASE = 'http://localhost:5000';

document.addEventListener('DOMContentLoaded', () => {
    const settingsBtn = document.getElementById('settingsBtn');
    const settingsPanel = document.getElementById('settingsPanel');
    const saveSettings = document.getElementById('saveSettings');
    const cuisineInput = document.getElementById('cuisine');
    const vegToggle = document.getElementById('vegToggle');
    const submitOrder = document.getElementById('submitOrder');
    const orderInput = document.getElementById('orderInput');
    const responseBox = document.getElementById('responseBox');

    // Toggle settings panel
    settingsBtn.addEventListener('click', () => {
        settingsPanel.classList.toggle('hidden');
    });

    // Load saved settings from backend
    fetch(`${API_BASE}/preference`)
        .then(res => res.json())
        .then(data => {
            if (data.cuisine) cuisineInput.value = data.cuisine;
            if (typeof data.is_vegetarian === 'boolean') vegToggle.checked = data.is_vegetarian;
        })
        .catch(() => {});

    // Save settings to backend
    saveSettings.addEventListener('click', () => {
        const cuisine = cuisineInput.value.trim();
        const is_vegetarian = vegToggle.checked;
        fetch(`${API_BASE}/preference`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cuisine, is_vegetarian })
        })
        .then(res => res.json())
        .then(data => {
            responseBox.textContent = data.message || 'Settings saved!';
            settingsPanel.classList.add('hidden');
        })
        .catch(() => {
            responseBox.textContent = 'Failed to save settings.';
        });
    });

    // Submit order (POST to backend)
    submitOrder.addEventListener('click', () => {
        const orderText = orderInput.value.trim();
        if (!orderText) {
            responseBox.textContent = 'Please enter your order or suggestion.';
            return;
        }
        fetch(`${API_BASE}/order`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ order_text: orderText })
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                responseBox.textContent = 'Error: ' + data.error;
            } else {
                responseBox.textContent = JSON.stringify(data, null, 2);
            }
        })
        .catch(() => {
            responseBox.textContent = 'Failed to submit order.';
        });
    });
});
