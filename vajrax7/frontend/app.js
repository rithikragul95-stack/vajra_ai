document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('simulation-form');
    const resultsSection = document.getElementById('results-section');
    const analyzeBtn = document.getElementById('analyze-btn');

    // Chart instances
    let riskRadarChart = null;
    let exposureBarChart = null;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 1. Gather Data
        const payload = {
            supplier_id: document.getElementById('supplier_id').value,
            location: document.getElementById('supplier_location').value,
            operational: {
                daily_demand: parseFloat(document.getElementById('daily_demand').value),
                current_inventory: parseFloat(document.getElementById('current_inventory').value),
                safety_stock: parseFloat(document.getElementById('safety_stock').value),
                supplier_lead_time: parseFloat(document.getElementById('supplier_lead_time').value),
                days_of_delay: parseFloat(document.getElementById('days_of_delay').value)
            },
            risk: {
                flood_severity: parseFloat(document.getElementById('flood_severity').value),
                earthquake_risk: parseFloat(document.getElementById('earthquake_risk').value),
                political_instability: parseFloat(document.getElementById('political_instability').value),
                transportation_disruption: parseFloat(document.getElementById('transportation_disruption').value),
                regional_infrastructure_risk: parseFloat(document.getElementById('regional_infrastructure_risk').value)
            }
        };

        // 2. Fetch from Backend
        try {
            analyzeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';
            analyzeBtn.disabled = true;

            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error("HTTP error " + response.status);
            }

            const data = await response.json();

            // 3. Update UI
            updateUI(data);

        } catch (error) {
            console.error(error);
            alert("Error running analysis. Is the FastAPI server running?");
        } finally {
            analyzeBtn.innerHTML = '<i class="fa-solid fa-microchip"></i> Run VAJRA Analysis';
            analyzeBtn.disabled = false;
        }
    });

    function updateUI(data) {
        // Unhide results smoothly
        resultsSection.classList.remove('hidden');

        const { predictive_risk, inventory_exposure, vulnerability_integration, prescriptive_decision } = data;

        // Predictive Risk Component
        document.getElementById('srp-val').innerText = predictive_risk.supplier_risk_probability.toFixed(2);
        const riskBadge = document.getElementById('risk-badge');
        riskBadge.innerText = predictive_risk.risk_classification;

        // Coloring badge
        riskBadge.style.background = predictive_risk.risk_classification === "HIGH" ? "var(--status-critical)" :
            predictive_risk.risk_classification === "MEDIUM" ? "var(--status-moderate)" :
                "var(--status-normal)";

        // Exposure Component
        document.getElementById('ic-val').innerText = inventory_exposure.inventory_cover.toFixed(1) + " days";
        document.getElementById('eg-val').innerText = inventory_exposure.exposure_gap.toFixed(1) + " days";
        document.getElementById('eg-val').style.color = inventory_exposure.is_exposed ? "var(--status-critical)" : "var(--status-preventive)";

        // Integration (CVI)
        document.getElementById('cvi-val').innerText = vulnerability_integration.composite_vulnerability_index.toFixed(3);

        // Alert Banner
        const alertBanner = document.getElementById('alert-banner');
        const alertTitle = document.getElementById('alert-title');
        const alertDesc = document.getElementById('alert-desc');
        const alertLevel = vulnerability_integration.alert_level;

        // Clear classes
        alertBanner.className = 'alert-banner';

        if (alertLevel === "Critical Alert") {
            alertBanner.classList.add('critical');
            alertBanner.querySelector('i').className = "fa-solid fa-radiation";
            alertTitle.innerText = "Critical Alert: High Supply Chain Vulnerability";
            alertDesc.innerText = "Severe risk detected combined with insufficient inventory coverage. Immediate action required.";
        } else if (alertLevel === "Moderate Alert") {
            alertBanner.classList.add('moderate');
            alertBanner.querySelector('i').className = "fa-solid fa-triangle-exclamation";
            alertTitle.innerText = "Moderate Alert: Elevated Risk";
            alertDesc.innerText = "Supplier risks are elevated and inventory may be insufficient. Adjust operations.";
        } else if (alertLevel === "Preventive Monitoring") {
            alertBanner.classList.add('preventive');
            alertBanner.querySelector('i').className = "fa-solid fa-shield-virus";
            alertTitle.innerText = "Preventive Monitoring";
            alertDesc.innerText = "External risks are high, but current inventory covers lead time safely. Maintain surveillance.";
        } else {
            alertBanner.classList.add('normal');
            alertBanner.querySelector('i').className = "fa-solid fa-circle-check";
            alertTitle.innerText = "Normal Operations";
            alertDesc.innerText = "Inventory coverage is healthy and supplier risk is stable.";
        }

        // Prescriptive Engine Component
        document.getElementById('req-inv-val').innerText = prescriptive_decision.required_inventory.toLocaleString();
        document.getElementById('add-inv-val').innerText = prescriptive_decision.additional_inventory_needed.toLocaleString();

        const recList = document.getElementById('recommendations-list');
        recList.innerHTML = "";
        prescriptive_decision.suggested_actions.forEach(rec => {
            const li = document.createElement('li');
            li.innerHTML = rec;
            recList.appendChild(li);
        });

        // Extract Original Inputs for Charts
        const riskInputs = [
            parseFloat(document.getElementById('flood_severity').value),
            parseFloat(document.getElementById('earthquake_risk').value),
            parseFloat(document.getElementById('political_instability').value),
            parseFloat(document.getElementById('transportation_disruption').value),
            parseFloat(document.getElementById('regional_infrastructure_risk').value)
        ];

        const inventoryData = {
            current: parseFloat(document.getElementById('current_inventory').value),
            target: prescriptive_decision.required_inventory
        };

        // Render Charts
        renderCharts(riskInputs, inventoryData);

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function renderCharts(riskInputs, inventoryData) {
        // Shared options
        Chart.defaults.color = '#64748b';
        Chart.defaults.font.family = "'Inter', sans-serif";

        // 1. Risk Radar Chart
        const radarCanvas = document.getElementById('riskRadarChart').getContext('2d');
        if (riskRadarChart) riskRadarChart.destroy();

        riskRadarChart = new Chart(radarCanvas, {
            type: 'radar',
            data: {
                labels: ['Flood', 'Earthquake', 'Political', 'Transportation', 'Infrastructure'],
                datasets: [{
                    label: 'Risk Feature Severity (0-1)',
                    data: riskInputs,
                    backgroundColor: 'rgba(255, 77, 79, 0.2)',
                    borderColor: '#ff4d4f',
                    pointBackgroundColor: '#ff4d4f',
                    borderWidth: 2,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: { color: 'rgba(0, 0, 0, 0.1)' },
                        grid: { color: 'rgba(0, 0, 0, 0.1)' },
                        pointLabels: { color: '#1e293b', font: { size: 12 } },
                        min: 0,
                        max: 1,
                        ticks: { display: false }
                    }
                },
                plugins: { legend: { display: false } }
            }
        });

        // 2. Exposure Bar Chart
        const barCanvas = document.getElementById('exposureBarChart').getContext('2d');
        if (exposureBarChart) exposureBarChart.destroy();

        const deficit = Math.max(0, inventoryData.target - inventoryData.current);
        const surplus = Math.max(0, inventoryData.current - inventoryData.target);

        exposureBarChart = new Chart(barCanvas, {
            type: 'bar',
            data: {
                labels: ['Inventory Status'],
                datasets: [
                    {
                        label: 'Current Inventory',
                        data: [inventoryData.current],
                        backgroundColor: '#1890ff',
                        borderRadius: 4
                    },
                    {
                        label: 'Required Gap (Deficit)',
                        data: [deficit],
                        backgroundColor: '#ff4d4f',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { stacked: true, grid: { display: false } },
                    y: {
                        stacked: true,
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#1e293b' }
                    }
                }
            }
        });
    }

    // Handle CSV Upload
    const csvInput = document.getElementById('csv-upload-input');
    const csvBtn = document.getElementById('csv-upload-btn');

    csvInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        try {
            csvBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Uploading...';

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error("Upload failed");

            const data = await response.json();
            alert("Success: " + data.message + "\n\nNavigate to the Suppliers page to view all imported records.");

        } catch (error) {
            console.error(error);
            alert("Error processing CSV file. Please ensure columns exactly match the supplier data format.");
        } finally {
            csvBtn.innerHTML = '<i class="fa-solid fa-file-csv"></i> Batch Upload CSV<input type="file" id="csv-upload-input" accept=".csv" style="display: none;">';
            // re-attach listener since we overwrote innerHTML
            document.getElementById('csv-upload-input').addEventListener('change', e.target.onchange);
        }
    });

});
