// Track selected values for pill-based fields
const fieldValues = {
    gender: 'Female',
    SeniorCitizen: '0',
    Partner: 'No',
    Dependents: 'No',
    PaperlessBilling: 'Yes',
    Contract: 'Month-to-month',
    PaymentMethod: 'Electronic check',
    PhoneService: 'Yes',
    MultipleLines: 'No',
    InternetService: 'Fiber optic',
};

// Services default to "No"
const serviceFields = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
                        'TechSupport', 'StreamingTV', 'StreamingMovies'];
const serviceState = {};
serviceFields.forEach(f => serviceState[f] = 'No');

// Wire up pill groups
document.querySelectorAll('.pill-group').forEach(group => {
    const field = group.dataset.field;
    group.querySelectorAll('.pill').forEach(pill => {
        pill.addEventListener('click', () => {
            group.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            fieldValues[field] = pill.dataset.value;

            if (field === 'PhoneService') handlePhoneServiceChange();
            if (field === 'InternetService') handleInternetServiceChange();
        });
    });
});

function handlePhoneServiceChange() {
    const mlGroup = document.querySelector('[data-field="MultipleLines"]');
    if (fieldValues.PhoneService === 'No') {
        fieldValues.MultipleLines = 'No phone service';
        mlGroup.querySelectorAll('.pill').forEach(p => p.classList.add('disabled'));
    } else {
        mlGroup.querySelectorAll('.pill').forEach(p => p.classList.remove('disabled'));
        fieldValues.MultipleLines = 'No';
        mlGroup.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
        mlGroup.querySelector('[data-value="No"]').classList.add('active');
    }
}

function handleInternetServiceChange() {
    const chips = document.querySelectorAll('.service-chip');
    if (fieldValues.InternetService === 'No') {
        serviceFields.forEach(f => serviceState[f] = 'No internet service');
        chips.forEach(chip => {
            chip.classList.remove('active');
            chip.classList.add('disabled');
        });
    } else {
        chips.forEach(chip => chip.classList.remove('disabled'));
        serviceFields.forEach(f => serviceState[f] = 'No');
        chips.forEach(chip => chip.classList.remove('active'));
    }
}

// Wire up service chips
document.querySelectorAll('.service-chip').forEach(chip => {
    chip.addEventListener('click', () => {
        if (chip.classList.contains('disabled')) return;
        const field = chip.dataset.field;
        const isActive = chip.classList.toggle('active');
        serviceState[field] = isActive ? 'Yes' : 'No';
    });
});

// Submit handler
document.getElementById('churnForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const btn = document.getElementById('predictBtn');
    btn.disabled = true;
    btn.textContent = 'Analyzing...';

    const payload = {
        ...fieldValues,
        ...serviceState,
        SeniorCitizen: parseInt(fieldValues.SeniorCitizen),
        tenure: parseInt(document.getElementById('tenure').value),
        MonthlyCharges: parseFloat(document.getElementById('MonthlyCharges').value),
        TotalCharges: parseFloat(document.getElementById('TotalCharges').value),
    };

    try {
        const res = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error('Prediction failed');

        const data = await res.json();
        sessionStorage.setItem('churnResult', JSON.stringify(data));
        window.location.href = '/result';
    } catch (err) {
        alert('Something went wrong: ' + err.message);
        btn.disabled = false;
        btn.textContent = 'Analyze Churn Risk';
    }
});