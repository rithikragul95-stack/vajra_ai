window.addEventListener('load', async () => {
    const tableBody = document.getElementById('suppliers-tbody');
    if (!tableBody) return;

    try {
        const response = await fetch('/api/suppliers');
        if (!response.ok) throw new Error("HTTP error " + response.status);

        const suppliers = await response.json();

        if (suppliers.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; padding: 3rem; color: var(--text-secondary);">
                        <i class="fa-solid fa-box-open" style="font-size: 2rem; margin-bottom: 1rem; color: var(--glass-border);"></i>
                        <p>No supplier assessments found in the database. Run an analysis on the Dashboard first!</p>
                    </td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = ""; // Clear loader

        suppliers.forEach(supp => {
            const tr = document.createElement('tr');

            // Format Timestamp
            const dateObj = new Date(supp.timestamp);
            const formattedDate = dateObj.toLocaleDateString() + " " + dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            // Badge CSS class mapping
            let badgeClass = "alert-normal";
            if (supp.alert_level === "Critical Alert") badgeClass = "alert-critical";
            else if (supp.alert_level === "Moderate Alert") badgeClass = "alert-moderate";
            else if (supp.alert_level === "Preventive Monitoring") badgeClass = "alert-preventive";

            tr.innerHTML = `
                <td class="supplier-id">${supp.supplier_id}</td>
                <td><i class="fa-solid fa-location-dot" style="color: var(--text-secondary); margin-right: 0.3rem;"></i>${supp.location}</td>
                <td style="color: var(--status-critical); font-weight: 500;">${supp.days_of_delay > 0 ? "+" + supp.days_of_delay + " days" : "-"}</td>
                <td class="time-col">${formattedDate}</td>
                <td><strong style="color: ${supp.exposure_gap > 0 ? "var(--status-critical)" : "var(--status-preventive)"}">${(supp.inventory_cover || 0).toFixed(1)} days</strong></td>
                <td>${(supp.supplier_risk_probability || 0).toFixed(2)} <span style="font-size: 0.8rem; color: var(--text-secondary);">(${supp.risk_classification})</span></td>
                <td><strong>${(supp.cvi_score || 0).toFixed(3)}</strong></td>
                <td><span class="alert-badge ${badgeClass}">${supp.alert_level}</span></td>
            `;

            // Add Recommendations Row directly beneath
            const trRecs = document.createElement('tr');
            trRecs.style.backgroundColor = 'rgba(0, 0, 0, 0.02)'; // Slightly offset row color

            let recsHtml = '';
            if (supp.recommendations) {
                try {
                    const parsed = JSON.parse(supp.recommendations);
                    recsHtml = parsed.map(r => `<li><i class="fa-solid fa-arrow-right" style="color:var(--accent-color); font-size:0.8rem; margin-right: 0.5rem;"></i> ${r}</li>`).join('');
                } catch (e) {
                    recsHtml = `<li>${supp.recommendations}</li>`;
                }
            } else {
                recsHtml = '<li>No recommendations recorded.</li>';
            }

            trRecs.innerHTML = `
                <td colspan="8" style="padding-top: 0.5rem; padding-bottom: 2rem; border-bottom: 2px solid var(--glass-border);">
                    <div style="font-size: 0.95rem; color: var(--text-secondary); margin-left: 1rem;">
                        <strong style="color: var(--text-primary);"><i class="fa-solid fa-list-check" style="color: var(--status-preventive); margin-right: 0.4rem;"></i>Prescriptive Action Engine:</strong>
                        <ul style="margin-top: 0.6rem; list-style: none; line-height: 1.8;">
                            ${recsHtml}
                        </ul>
                    </div>
                </td>
            `;

            // Modify original TR to drop border
            tr.querySelector('td').style.borderBottom = 'none';
            for (let td of tr.children) td.style.borderBottom = 'none';

            tableBody.appendChild(tr);
            tableBody.appendChild(trRecs);
        });

    } catch (error) {
        console.error("Error fetching suppliers:", error);
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 2rem; color: var(--status-critical);">
                    <i class="fa-solid fa-triangle-exclamation" style="font-size: 1.5rem; margin-bottom: 1rem;"></i>
                    <p>Failed to load suppliers frontend error: ${error.message}</p>
                </td>
            </tr>
        `;
    }

    // Modal and Chart Logic
    const modal = document.getElementById('chartModal');
    const closeBtn = document.getElementById('closeModal');
    let historyChart = null;

    if (closeBtn && modal) {
        closeBtn.onclick = function () {
            modal.style.display = "none";
        }

        window.onclick = function (event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }
    }

    // Attach click listeners to supplier IDs
    tableBody.addEventListener('click', async (e) => {
        if (e.target.classList.contains('supplier-id')) {
            const supplierId = e.target.innerText;
            await showSupplierHistory(supplierId);
        }
    });

    async function showSupplierHistory(supplierId) {
        try {
            document.getElementById('modalTitle').innerText = "History: " + supplierId;
            modal.style.display = "block";

            const res = await fetch(`/api/suppliers/${supplierId}/history`);
            if (!res.ok) throw new Error("History fetch failed");

            const historyData = await res.json();

            // Prepare Chart Data
            const labels = [];
            const srpData = [];
            const cviData = [];

            historyData.forEach(record => {
                const dateObj = new Date(record.timestamp);
                labels.push(dateObj.toLocaleDateString() + " " + dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
                srpData.push(record.supplier_risk_probability);
                cviData.push(record.cvi_score);
            });

            const ctx = document.getElementById('historyChart').getContext('2d');

            // Destroy existing chart if it exists
            if (historyChart) {
                historyChart.destroy();
            }

            Chart.defaults.color = "#64748b";
            Chart.defaults.font.family = "'Inter', sans-serif";

            historyChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Risk Probability (SRP)',
                            data: srpData,
                            borderColor: '#ff4d4f', // Critical Status Red
                            backgroundColor: 'rgba(255, 77, 79, 0.1)',
                            borderWidth: 2,
                            tension: 0.3,
                            fill: true,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Composite Vulnerability (CVI)',
                            data: cviData,
                            borderColor: '#faad14', // Warning Orange
                            backgroundColor: 'rgba(250, 173, 20, 0.1)',
                            borderWidth: 2,
                            tension: 0.3,
                            fill: true,
                            yAxisID: 'y'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: { position: 'bottom' }
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            grid: { color: 'rgba(0, 0, 0, 0.05)' }
                        }
                    }
                }
            });

        } catch (error) {
            console.error(error);
            alert("Error loading historical data.");
        }
    }

    // CSV Upload Logic
    const csvInput = document.getElementById('csvFileInput');
    if (csvInput) {
        csvInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append("file", file);

            try {
                // Show updating toast/loader later
                const btn = document.querySelector('button[onclick="document.getElementById(\'csvFileInput\').click()"]');
                if (btn) {
                    const origHtml = btn.innerHTML;
                    btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Uploading...';
                    btn.disabled = true;
                }

                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error("HTTP error " + response.status);
                }

                const data = await response.json();
                alert(data.message); // Will show success and error count

                // Reload page to see new data
                window.location.reload();
            } catch (error) {
                console.error(error);
                alert("Error connecting or parsing CSV. Ensure correct schema.");
            }
        });
    }
});
