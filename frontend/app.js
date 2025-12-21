/**
 * Main application JavaScript for Dealer Greeks Dashboard
 */

const API_BASE_URL = 'http://localhost:8000';

let autoRefreshInterval = null;
let gammaChart = null;
let deltaChart = null;
let currentData = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadData();
});

function initializeEventListeners() {
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', () => {
        loadData();
    });

    // Auto-refresh toggle
    document.getElementById('autoRefreshToggle').addEventListener('click', () => {
        toggleAutoRefresh();
    });

    // Symbol change
    document.getElementById('symbol').addEventListener('change', () => {
        loadData();
    });

    // Expiry change
    document.getElementById('expiry').addEventListener('change', () => {
        loadData();
    });

    // Provider change
    document.getElementById('provider').addEventListener('change', () => {
        loadData();
    });

    // Sort change
    document.getElementById('sortBy').addEventListener('change', () => {
        if (currentData) {
            renderTable(currentData);
        }
    });
}

async function loadData() {
    const symbol = document.getElementById('symbol').value.toUpperCase();
    const expiry = document.getElementById('expiry').value || null;
    const provider = document.getElementById('provider').value;

    updateStatus('Loading...', 'info');

    try {
        const params = new URLSearchParams({
            symbol: symbol,
            provider: provider
        });
        if (expiry) {
            params.append('expiry', expiry);
        }

        const response = await fetch(`${API_BASE_URL}/api/chain?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        currentData = data;
        
        renderDashboard(data);
        updateStatus('Data loaded successfully', 'success');
        
    } catch (error) {
        console.error('Error loading data:', error);
        updateStatus(`Error: ${error.message}`, 'error');
    }
}

function renderDashboard(data) {
    // Update status bar
    document.getElementById('lastUpdate').textContent = `Updated: ${new Date(data.updated_at).toLocaleTimeString()}`;
    document.getElementById('spotPrice').textContent = `Spot: $${data.spot.toFixed(2)}`;

    // Update totals
    updateTotals(data.totals);

    // Update MM response
    updateMMResponse(data.mm_response);

    // Render table
    renderTable(data);

    // Update charts
    updateCharts(data);
}

function updateTotals(totals) {
    const formatNumber = (num) => {
        if (Math.abs(num) >= 1e9) {
            return (num / 1e9).toFixed(2) + 'B';
        } else if (Math.abs(num) >= 1e6) {
            return (num / 1e6).toFixed(2) + 'M';
        } else if (Math.abs(num) >= 1e3) {
            return (num / 1e3).toFixed(2) + 'K';
        }
        return num.toFixed(2);
    };

    const deltaEl = document.getElementById('totalDelta');
    const gammaEl = document.getElementById('totalGamma');
    const vannaEl = document.getElementById('totalVanna');
    const charmEl = document.getElementById('totalCharm');

    deltaEl.textContent = formatNumber(totals.net_dealer_delta);
    deltaEl.className = 'card-value ' + (totals.net_dealer_delta >= 0 ? 'positive' : 'negative');

    gammaEl.textContent = formatNumber(totals.net_dealer_gamma);
    gammaEl.className = 'card-value ' + (totals.net_dealer_gamma >= 0 ? 'positive' : 'negative');

    vannaEl.textContent = formatNumber(totals.net_dealer_vanna);
    vannaEl.className = 'card-value ' + (totals.net_dealer_vanna >= 0 ? 'positive' : 'negative');

    charmEl.textContent = formatNumber(totals.net_dealer_charm);
    charmEl.className = 'card-value ' + (totals.net_dealer_charm >= 0 ? 'positive' : 'negative');
}

function updateMMResponse(mmResponse) {
    document.getElementById('regime').textContent = mmResponse.regime;
    
    const notesEl = document.getElementById('notes');
    if (mmResponse.notes && mmResponse.notes.length > 0) {
        notesEl.innerHTML = '<ul>' + mmResponse.notes.map(note => `<li>${note}</li>`).join('') + '</ul>';
    } else {
        notesEl.innerHTML = '<ul><li>No specific notes</li></ul>';
    }
}

function renderTable(data) {
    const tbody = document.getElementById('strikeTableBody');
    const sortBy = document.getElementById('sortBy').value;

    // Sort rows
    let sortedRows = [...data.rows];
    if (sortBy === 'strike') {
        sortedRows.sort((a, b) => a.strike - b.strike);
    } else if (sortBy === 'gamma') {
        sortedRows.sort((a, b) => Math.abs(b.dealer_gamma_exp) - Math.abs(a.dealer_gamma_exp));
    } else if (sortBy === 'delta') {
        sortedRows.sort((a, b) => Math.abs(b.dealer_delta_exp) - Math.abs(a.dealer_delta_exp));
    } else if (sortBy === 'vanna') {
        sortedRows.sort((a, b) => Math.abs(b.dealer_vanna_exp) - Math.abs(a.dealer_vanna_exp));
    }

    const formatNumber = (num) => {
        if (Math.abs(num) >= 1e9) {
            return (num / 1e9).toFixed(2) + 'B';
        } else if (Math.abs(num) >= 1e6) {
            return (num / 1e6).toFixed(2) + 'M';
        } else if (Math.abs(num) >= 1e3) {
            return (num / 1e3).toFixed(2) + 'K';
        }
        return num.toFixed(2);
    };

    tbody.innerHTML = sortedRows.map(row => {
        const deltaClass = row.dealer_delta_exp >= 0 ? 'number-positive' : 'number-negative';
        const gammaClass = row.dealer_gamma_exp >= 0 ? 'number-positive' : 'number-negative';
        const vannaClass = row.dealer_vanna_exp >= 0 ? 'number-positive' : 'number-negative';
        const charmClass = row.dealer_charm_exp >= 0 ? 'number-positive' : 'number-negative';

        return `
            <tr>
                <td><strong>${row.strike.toFixed(2)}</strong></td>
                <td class="${deltaClass}">${formatNumber(row.dealer_delta_exp)}</td>
                <td class="${gammaClass}">${formatNumber(row.dealer_gamma_exp)}</td>
                <td class="${vannaClass}">${formatNumber(row.dealer_vanna_exp)}</td>
                <td class="${charmClass}">${formatNumber(row.dealer_charm_exp)}</td>
                <td>${row.call_oi.toLocaleString()}</td>
                <td>${row.put_oi.toLocaleString()}</td>
            </tr>
        `;
    }).join('');
}

function updateCharts(data) {
    const strikes = data.rows.map(r => r.strike);
    const gammaData = data.rows.map(r => r.dealer_gamma_exp);
    const deltaData = data.rows.map(r => r.dealer_delta_exp);

    // Gamma Chart
    const gammaCtx = document.getElementById('gammaChart').getContext('2d');
    if (gammaChart) {
        gammaChart.destroy();
    }
    gammaChart = new Chart(gammaCtx, {
        type: 'bar',
        data: {
            labels: strikes,
            datasets: [{
                label: 'Dealer Gamma Exposure',
                data: gammaData,
                backgroundColor: gammaData.map(v => v >= 0 ? 'rgba(102, 187, 106, 0.6)' : 'rgba(239, 83, 80, 0.6)'),
                borderColor: gammaData.map(v => v >= 0 ? 'rgba(102, 187, 106, 1)' : 'rgba(239, 83, 80, 1)'),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        color: '#a0a0a0'
                    },
                    grid: {
                        color: '#2d3560'
                    }
                },
                x: {
                    ticks: {
                        color: '#a0a0a0',
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: {
                        color: '#2d3560'
                    }
                }
            }
        }
    });

    // Delta Chart
    const deltaCtx = document.getElementById('deltaChart').getContext('2d');
    if (deltaChart) {
        deltaChart.destroy();
    }
    deltaChart = new Chart(deltaCtx, {
        type: 'line',
        data: {
            labels: strikes,
            datasets: [{
                label: 'Dealer Delta Exposure',
                data: deltaData,
                borderColor: '#4fc3f7',
                backgroundColor: 'rgba(79, 195, 247, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        color: '#a0a0a0'
                    },
                    grid: {
                        color: '#2d3560'
                    }
                },
                x: {
                    ticks: {
                        color: '#a0a0a0',
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: {
                        color: '#2d3560'
                    }
                }
            }
        }
    });
}

function toggleAutoRefresh() {
    const toggleBtn = document.getElementById('autoRefreshToggle');
    
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        toggleBtn.textContent = 'Auto: OFF';
        toggleBtn.style.background = '#2d3560';
    } else {
        const interval = parseInt(document.getElementById('refreshInterval').value) * 1000;
        autoRefreshInterval = setInterval(() => {
            loadData();
        }, interval);
        toggleBtn.textContent = 'Auto: ON';
        toggleBtn.style.background = '#4fc3f7';
    }
}

function updateStatus(message, type) {
    const statusEl = document.getElementById('status');
    statusEl.textContent = message;
    
    if (type === 'error') {
        statusEl.style.color = '#ef5350';
    } else if (type === 'success') {
        statusEl.style.color = '#66bb6a';
    } else {
        statusEl.style.color = '#a0a0a0';
    }
}

