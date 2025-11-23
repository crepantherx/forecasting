const API_URL = 'http://localhost:8000';

let currentCity = 'Sydney';
let mainChart = null;
let workloadChart = null;
let performanceChart = null;
let currentForecast = null;

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;

        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.getElementById(tab).classList.add('active');

        if (tab === 'overview') loadOverview();
        if (tab === 'engineer') loadEngineerView();
        if (tab === 'performance') loadPerformance();
    });
});

// City selector
document.getElementById('citySelect').addEventListener('change', (e) => {
    currentCity = e.target.value;
    loadOverview();
});

// Buttons
document.getElementById('generateForecastBtn').addEventListener('click', generateForecast);
document.getElementById('loadJobsBtn').addEventListener('click', loadEngineerJobs);
document.getElementById('emulateBtn').addEventListener('click', emulateDay);
document.getElementById('loadDataBtn').addEventListener('click', loadCompleteData);
document.getElementById('dataFilterCity').addEventListener('change', loadCompleteData);

// Load Overview (merged Dashboard + Forecast)
async function loadOverview() {
    showLoading();
    try {
        const response = await fetch(`${API_URL}/data/history?city=${currentCity}&days=30`);
        const result = await response.json();

        // Update stats
        const latest = result.data[result.data.length - 1];
        document.getElementById('currentStats').innerHTML = `
            <div style="font-size: 2rem; font-weight: bold; color: #667eea;">${latest.request_count} requests</div>
            <div style="font-size: 0.9rem; color: #666; margin-top: 10px;">
                📅 ${latest.date}<br>
                🌡️ ${latest.temperature_c}°C | 🌧️ ${latest.rainfall_mm}mm
            </div>
        `;

        // Update chart with historical data only (forecast will be added when generated)
        updateMainChart(result.data, null);

    } catch (error) {
        console.error('Error loading overview:', error);
        alert('Failed to load data');
    } finally {
        hideLoading();
    }
}

// Update main chart
function updateMainChart(historicalData, forecastData) {
    const histLabels = historicalData.map(d => d.date);
    const histValues = historicalData.map(d => d.request_count);

    let allLabels = histLabels;
    let histData = histValues;
    let forecastValues = [];

    if (forecastData && forecastData.length > 0) {
        const forecastLabels = forecastData.map(f => f.date);
        allLabels = [...histLabels, ...forecastLabels];
        histData = [...histValues, ...Array(forecastLabels.length).fill(null)];
        forecastValues = [...Array(histLabels.length).fill(null), ...forecastData.map(f => f.predicted_count)];
    }

    const datasets = [
        {
            label: 'Historical Demand',
            data: histData,
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            tension: 0.4,
            fill: true
        }
    ];

    if (forecastData && forecastData.length > 0) {
        datasets.push({
            label: 'Forecast',
            data: forecastValues,
            borderColor: '#F472B6',
            borderDash: [5, 5],
            backgroundColor: 'rgba(244, 114, 182, 0.1)',
            tension: 0.4,
            fill: true
        });
    }

    if (mainChart) mainChart.destroy();

    const ctx = document.getElementById('mainChart').getContext('2d');
    mainChart = new Chart(ctx, {
        type: 'line',
        data: { labels: allLabels, datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true, position: 'top' }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

// Generate forecast
async function generateForecast() {
    const model = document.getElementById('forecastModel').value;
    const horizon = parseInt(document.getElementById('forecastHorizon').value);

    showLoading();
    try {
        const response = await fetch(`${API_URL}/forecast/demand?city=${currentCity}&model=${model}&horizon=${horizon}`, {
            method: 'POST'
        });

        if (!response.ok) throw new Error('Forecast failed');

        const result = await response.json();
        currentForecast = result.forecasts;

        // Get historical data
        const histResponse = await fetch(`${API_URL}/data/history?city=${currentCity}&days=30`);
        const histData = await histResponse.json();

        // Update chart with both historical and forecast
        updateMainChart(histData.data, result.forecasts);

        alert(`✓ Forecast generated for ${currentCity} using ${model.toUpperCase()}`);

    } catch (error) {
        console.error('Error generating forecast:', error);
        alert('Failed to generate forecast');
    } finally {
        hideLoading();
    }
}

// Load Engineer View with smart allocation
async function loadEngineerJobs() {
    const location = document.getElementById('engineerLocation').value;
    const engineerName = document.getElementById('engineerName').value;

    showLoading();
    try {
        // Get demand for all cities
        const cities = ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Canberra'];
        const demands = {};

        for (const city of cities) {
            const response = await fetch(`${API_URL}/data/current?city=${city}`);
            const result = await response.json();
            demands[city] = result.data[0].request_count;
        }

        // Smart allocation: prioritize current location, then by demand
        const sortedCities = cities.sort((a, b) => {
            if (a === location) return -1;
            if (b === location) return 1;
            return demands[b] - demands[a];
        });

        // Generate job list
        let jobsHtml = '<div class="jobs-grid">';
        sortedCities.forEach((city, index) => {
            const priority = city === location ? 'HIGH' : index < 3 ? 'MEDIUM' : 'LOW';
            const priorityColor = priority === 'HIGH' ? '#48bb78' : priority === 'MEDIUM' ? '#F59E0B' : '#999';

            jobsHtml += `
                <div class="job-card" style="border-left: 4px solid ${priorityColor};">
                    <div class="job-header">
                        <h3>${city}</h3>
                        <span class="priority-badge" style="background: ${priorityColor};">${priority}</span>
                    </div>
                    <div class="job-details">
                        <p><strong>${demands[city]}</strong> pending requests</p>
                        <p>${city === location ? '📍 Your current location' : '🚗 ' + (Math.random() * 50 + 10).toFixed(0) + ' km away'}</p>
                    </div>
                    <button class="btn btn-primary" style="width: 100%; margin-top: 10px;">Accept Jobs</button>
                </div>
            `;
        });
        jobsHtml += '</div>';

        document.getElementById('jobsList').innerHTML = jobsHtml;

        // Update workload chart
        updateWorkloadChart(demands);

    } catch (error) {
        console.error('Error loading jobs:', error);
        alert('Failed to load jobs');
    } finally {
        hideLoading();
    }
}

// Update workload chart
function updateWorkloadChart(demands) {
    if (workloadChart) workloadChart.destroy();

    const ctx = document.getElementById('workloadChart').getContext('2d');
    workloadChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(demands),
            datasets: [{
                label: 'Pending Requests',
                data: Object.values(demands),
                backgroundColor: ['#667eea', '#764ba2', '#F59E0B', '#48bb78', '#F472B6', '#10B981']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Emulate day
async function emulateDay() {
    const city = document.getElementById('emulateCity').value;
    const count = parseInt(document.getElementById('emulateCount').value);
    const temp = parseFloat(document.getElementById('emulateTemp').value);
    const rain = parseFloat(document.getElementById('emulateRain').value);

    showLoading();
    try {
        const response = await fetch(`${API_URL}/emulate/day`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                city: city,
                actual_count: count,
                temperature: temp,
                rainfall: rain
            })
        });

        const result = await response.json();

        document.getElementById('emulationResults').innerHTML = `
            <div style="padding: 20px; background: #f0f9ff; border-radius: 8px;">
                <h3 style="color: #667eea; margin-bottom: 10px;">✓ New Day Emulated</h3>
                <p><strong>Date:</strong> ${result.new_date}</p>
                <p><strong>City:</strong> ${result.city}</p>
                <p><strong>Actual Requests:</strong> ${result.actual_count}</p>
            </div>
        `;

    } catch (error) {
        console.error('Error emulating day:', error);
        alert('Failed to emulate day');
    } finally {
        hideLoading();
    }
}

// Load complete data
async function loadCompleteData() {
    const filterCity = document.getElementById('dataFilterCity').value;

    showLoading();
    try {
        let url = `${API_URL}/data/history?days=365`;
        if (filterCity) url += `&city=${filterCity}`;

        const response = await fetch(url);
        const result = await response.json();

        // Create table
        let html = '<table><thead><tr>';
        html += '<th>Date</th><th>City</th><th>Requests</th><th>Temp (°C)</th><th>Rain (mm)</th><th>Weekend</th><th>Holiday</th>';
        html += '</tr></thead><tbody>';

        result.data.forEach(row => {
            html += `<tr>
                <td>${row.date}</td>
                <td>${row.city}</td>
                <td><strong>${row.request_count}</strong></td>
                <td>${row.temperature_c}</td>
                <td>${row.rainfall_mm}</td>
                <td>${row.is_weekend ? '✓' : ''}</td>
                <td>${row.is_holiday ? '✓' : ''}</td>
            </tr>`;
        });

        html += '</tbody></table>';
        html = `<p style="margin-bottom: 10px;"><strong>${result.data.length}</strong> records found</p>` + html;

        document.getElementById('dataTable').innerHTML = html;

    } catch (error) {
        console.error('Error loading data:', error);
        alert('Failed to load data');
    } finally {
        hideLoading();
    }
}

// Load performance
async function loadPerformance() {
    showLoading();
    try {
        const response = await fetch(`${API_URL}/performance/summary`);
        const result = await response.json();

        let html = '<table><thead><tr><th>Model</th><th>MAE</th><th>RMSE</th><th>MAPE (%)</th></tr></thead><tbody>';
        result.models.forEach(m => {
            html += `<tr><td>${m.name}</td><td>${m.mae}</td><td>${m.rmse}</td><td>${m.mape}</td></tr>`;
        });
        html += '</tbody></table>';
        document.getElementById('performanceTable').innerHTML = html;

        if (performanceChart) performanceChart.destroy();

        const ctx = document.getElementById('performanceChart').getContext('2d');
        performanceChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: result.models.map(m => m.name),
                datasets: [{
                    label: 'MAE',
                    data: result.models.map(m => m.mae),
                    backgroundColor: '#667eea'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true
            }
        });

    } catch (error) {
        console.error('Error loading performance:', error);
    } finally {
        hideLoading();
    }
}

function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// Initialize
loadOverview();
