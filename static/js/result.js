const raw = sessionStorage.getItem('churnResult');
const wrap = document.getElementById('resultWrap');

if (!raw) {
    wrap.innerHTML = `
        <div class="hero">
            <h1>No Result Found</h1>
            <p>Please submit a customer profile first.</p>
        </div>
        <a href="/" class="back-btn">Go to Home</a>
    `;
} else {
    const data = JSON.parse(raw);
    render(data);
}

function render(data) {
    const isChurn = data.prediction === 'Churn';
    const probPercent = (data.churn_probability * 100).toFixed(1);
    const summary = data.customer_summary;

    wrap.innerHTML = `
        <div class="result-header">
            <div>
                <h1 style="font-size:26px; font-weight:800;">Prediction Result</h1>
                <p style="color:var(--text-muted); font-size:14px; margin-top:4px;">Based on the customer profile you submitted</p>
            </div>
            <div class="risk-badge ${isChurn ? 'churn' : 'safe'}">
                ${isChurn ? '⚠️ High Churn Risk' : '✅ Low Churn Risk'}
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="card gauge-card">
                <div class="section-title" style="text-align:left; margin-bottom: 20px;">Churn Probability</div>
                <div class="gauge-number ${isChurn ? 'churn' : 'safe'}">${probPercent}%</div>
                <div class="gauge-bar-track">
                    <div class="gauge-bar-fill" style="width:${probPercent}%; background:${isChurn ? '#dc2626' : '#16a34a'};"></div>
                </div>
                <div class="gauge-caption">Decision threshold: ${(data.threshold_used * 100).toFixed(0)}% &nbsp;•&nbsp; Baseline average: ${(data.base_value * 100).toFixed(0)}%</div>
            </div>

            <div class="card">
                <div class="section-title" style="margin-bottom: 18px;">Customer Summary</div>
                <div class="summary-list">
                    <div class="summary-row"><span class="label">Tenure</span><span class="value">${summary.tenure} months</span></div>
                    <div class="summary-row"><span class="label">Contract</span><span class="value">${summary.contract}</span></div>
                    <div class="summary-row"><span class="label">Monthly Charges</span><span class="value">$${summary.monthly_charges.toFixed(2)}</span></div>
                    <div class="summary-row"><span class="label">Total Charges</span><span class="value">$${summary.total_charges.toFixed(2)}</span></div>
                    <div class="summary-row"><span class="label">Internet Service</span><span class="value">${summary.internet_service}</span></div>
                    <div class="summary-row"><span class="label">Services Subscribed</span><span class="value">${summary.total_services} of 6</span></div>
                </div>
            </div>
        </div>

        <div class="card" style="margin-top:24px;">
            <div class="section-title">What's Driving This Prediction</div>
            <div class="section-subtitle">Top factors, ranked by impact. Red pushes risk up, green pulls it down.</div>
            <div id="shapContainer"></div>
        </div>

        <a href="/" class="back-btn">Analyze Another Customer</a>
    `;

    const maxImpact = Math.max(...data.shap_explanation.map(s => Math.abs(s.shap_value)));
    const shapContainer = document.getElementById('shapContainer');

    data.shap_explanation.forEach(item => {
        const widthPct = (Math.abs(item.shap_value) / maxImpact) * 100;
        const dirClass = item.direction === 'increases' ? 'increase' : 'decrease';

        const row = document.createElement('div');
        row.className = 'shap-row';
        row.innerHTML = `
            <div>
                <span class="feature-name">${item.feature}</span>
                <span class="feature-value">${item.raw_value}</span>
            </div>
            <div class="shap-bar-track">
                <div class="shap-bar-fill ${dirClass}" style="width:${widthPct}%;"></div>
            </div>
            <div class="shap-impact ${dirClass}">${item.direction === 'increases' ? '↑' : '↓'} ${Math.abs(item.shap_value).toFixed(3)}</div>
        `;
        shapContainer.appendChild(row);
    });
}