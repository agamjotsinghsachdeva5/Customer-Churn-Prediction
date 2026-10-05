document.getElementById('churnForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const btn = document.getElementById('predictBtn');
    btn.disabled = true;
    btn.textContent = 'Predicting...';

    const formData = new FormData(e.target);
    const payload = {};
    formData.forEach((value, key) => {
        payload[key] = key === 'SeniorCitizen' ? parseInt(value)
                      : (key === 'tenure' ? parseInt(value)
                      : (key === 'MonthlyCharges' || key === 'TotalCharges') ? parseFloat(value)
                      : value);
    });

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error('Prediction failed');

        const data = await response.json();
        displayResult(data);
    } catch (err) {
        alert('Something went wrong: ' + err.message);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Predict Churn Risk';
    }
});

function displayResult(data) {
    const resultDiv = document.getElementById('result');
    resultDiv.classList.remove('hidden');

    const label = document.getElementById('predictionLabel');
    label.textContent = data.prediction === 'Churn' ? '⚠️ High Churn Risk' : '✅ Low Churn Risk';
    label.style.color = data.prediction === 'Churn' ? '#f87171' : '#4ade80';

    const probPercent = (data.churn_probability * 100).toFixed(1);
    document.getElementById('probabilityBar').style.width = probPercent + '%';
    document.getElementById('probabilityText').textContent =
        `Churn Probability: ${probPercent}% (Threshold: ${(data.threshold_used * 100).toFixed(0)}%)`;

    const shapList = document.getElementById('shapList');
    shapList.innerHTML = '';
    data.shap_explanation.forEach(item => {
        const div = document.createElement('div');
        div.className = 'shap-item';
        const direction = item.shap_value > 0 ? 'positive' : 'negative';
        const arrow = item.shap_value > 0 ? '↑ increases risk' : '↓ decreases risk';
        div.innerHTML = `
            <span class="shap-feature">${item.feature}</span>
            <span class="shap-value ${direction}">${arrow}</span>
        `;
        shapList.appendChild(div);
    });

    resultDiv.scrollIntoView({ behavior: 'smooth' });
}