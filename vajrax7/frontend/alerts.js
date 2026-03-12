document.addEventListener('DOMContentLoaded', fetchAlerts);

async function fetchAlerts() {
    const loading = document.getElementById('alerts-loading');
    const container = document.getElementById('alerts-container');
    const noAlertsView = document.getElementById('no-alerts-view');

    loading.classList.remove('hidden');
    container.classList.add('hidden');
    container.innerHTML = '';
    noAlertsView.classList.add('hidden');

    try {
        const response = await fetch('/api/suppliers');
        if (!response.ok) throw new Error("HTTP error " + response.status);

        const suppliers = await response.json();

        // Filter out suppliers that are Normal or Preventive Monitoring
        const activeAlerts = suppliers.filter(s => 
            s.alert_level === 'Critical Alert' || s.alert_level === 'Moderate Alert'
        );

        if (activeAlerts.length === 0) {
            loading.classList.add('hidden');
            noAlertsView.classList.remove('hidden');
            return;
        }

        // Generate Cards
        activeAlerts.forEach(supp => {
            const isCritical = supp.alert_level === 'Critical Alert';
            const cardClass = isCritical ? 'critical' : 'moderate';

            const card = document.createElement('div');
            card.className = `alert-card ${cardClass} glass-panel`;

            let recsHtml = '';
            if (supp.recommendations) {
                try {
                    const parsed = JSON.parse(supp.recommendations);
                    recsHtml = parsed.map(r => `<li><i class="fa-solid fa-arrow-right"></i> <span>${r}</span></li>`).join('');
                } catch (e) {
                    recsHtml = `<li><i class="fa-solid fa-arrow-right"></i> <span>${supp.recommendations}</span></li>`;
                }
            }

            card.innerHTML = `
                <div class="alert-header">
                    <h3><i class="fa-solid fa-triangle-exclamation" style="margin-right: 0.5rem; color: ${isCritical ? 'var(--status-critical)' : 'var(--status-moderate)'};"></i> ${supp.supplier_id}</h3>
                    <div class="alert-badge">${supp.alert_level}</div>
                </div>
                
                <div>
                    <div class="metric-row">
                        <span class="metric-label">Supplier Risk (SRP)</span>
                        <span class="metric-value bad-value">${supp.supplier_risk_probability.toFixed(2)} (${supp.risk_classification})</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Inv. Cover (Days)</span>
                        <span class="metric-value ${supp.exposure_gap > 0 ? "bad-value" : ""}">${supp.inventory_cover.toFixed(1)}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Exposure Gap (Days)</span>
                        <span class="metric-value ${supp.exposure_gap > 0 ? "bad-value" : ""}">${supp.exposure_gap.toFixed(1)}</span>
                    </div>
                    <div class="metric-row" style="border-bottom: none;">
                        <span class="metric-label">Vuln. Score (CVI)</span>
                        <span class="metric-value">${supp.cvi_score.toFixed(3)}</span>
                    </div>
                </div>

                <div class="recs-box">
                    <strong style="color: var(--text-secondary); font-family: 'Outfit', sans-serif;">Action Required:</strong>
                    <ul>${recsHtml}</ul>
                </div>
            `;

            container.appendChild(card);
        });

        loading.classList.add('hidden');
        container.classList.remove('hidden');

    } catch (error) {
        console.error("Error fetching alerts:", error);
        loading.classList.add('hidden');
        container.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; color: var(--status-critical); padding: 3rem;">
                <i class="fa-solid fa-circle-exclamation" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                <p>Unable to retrieve active threats from the API. Check connection.</p>
            </div>
        `;
        container.classList.remove('hidden');
    }
}
