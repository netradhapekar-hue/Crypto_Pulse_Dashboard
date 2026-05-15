const API = "https://crypto-pulse-api-dx3x.onrender.com";
// const API = "http://127.0.0.1:5000";

let topCryptoChart = null;

// ======================================================
// FETCH HELPER
// ======================================================

async function fetchData(endpoint) {
    try {
        const res = await fetch(`${API}${endpoint}`);

        if (!res.ok) {
            throw new Error(`${endpoint} failed`);
        }

        return await res.json();

    } catch (err) {
        console.error(`❌ Error fetching ${endpoint}:`, err);
        return null;
    }
}

// ======================================================
// FORMAT HELPERS
// ======================================================

function formatCurrency(num) {
    if (num === null || num === undefined || num === "") {
        return "N/A";
    }

    const value = Number(num);

    if (isNaN(value)) {
        return "N/A";
    }

    return `$${value.toLocaleString("en-US", {
        minimumFractionDigits: value < 1 ? 6 : 2,
        maximumFractionDigits: value < 1 ? 8 : 2
    })}`;
}

function formatPercent(num) {
    if (num === null || num === undefined) {
        return "N/A";
    }

    return `${Number(num).toFixed(2)}%`;
}

// ======================================================
// LOAD SUMMARY
// ======================================================

function renderSummary(data) {

    if (!data) return;

    document.getElementById("avgPrice").innerText =
        formatCurrency(data.avg_price);

    document.getElementById("maxPrice").innerText =
        formatCurrency(data.max_price);

    document.getElementById("minPrice").innerText =
        formatCurrency(data.min_price);
}

// ======================================================
// LOAD TRENDING
// ======================================================

function renderTrending(data) {

    if (!data || !Array.isArray(data)) return;

    const container = document.getElementById("trendingList");

    if (!container) return;

    container.innerHTML = "";

    data.forEach((coin, i) => {
        const change = Number(coin.change ?? coin.change_24h ?? 0);
        const color = change >= 0 ? "green" : "red";
        const arrow = change >= 0 ? "▲" : "▼";

        container.innerHTML += `
            <div class="insight-item">
                <div class="insight-left">
                    <span class="rank">#${i + 1}</span>

                    <img 
                        class="coin-icon"
                        src="${coin.image || ''}"
                        onerror="this.onerror=null; this.src='https://cdn-icons-png.flaticon.com/512/149/149071.png';"
                    >

                    <div>
                        <div class="insight-name">
                            ${coin.name || coin.coin || coin.symbol || "Unknown"}
                        </div>

                        <div class="coin-symbol">
                            ${coin.symbol || coin.coin || ""}
                        </div>
                    </div>
                </div>

                <div class="insight-right ${color}">
                    ${arrow} ${Math.abs(change).toFixed(2)}%
                </div>
            </div>
        `;
    });
}

// ======================================================
// LOAD TOP GAINERS
// ======================================================

function renderGainers(data) {

    if (!data || !Array.isArray(data)) return;

    const container = document.getElementById("gainersList");

    if (!container) return;

    container.innerHTML = "";

    data.forEach((coin, i) => {
        const change = Number(coin.change ?? 0);

        container.innerHTML += `
            <div class="insight-item">
                <div class="insight-left">
                    <span class="rank">#${i + 1}</span>

                    <img 
                        class="coin-icon"
                        src="${coin.image || ''}"
                        onerror="this.onerror=null; this.src='https://cdn-icons-png.flaticon.com/512/149/149071.png';"
                    >

                    <div>
                        <div class="insight-name">
                            ${coin.coin}
                        </div>
                    </div>
                </div>

                <div class="insight-right green">
                    ▲ ${change.toFixed(2)}%
                </div>
            </div>
        `;
    });
}

// ======================================================
// LOAD TOP ASSETS
// ======================================================
const lineGlowPlugin = {
    id: "lineGlowPlugin",
    beforeDatasetDraw(chart) {
        const { ctx } = chart;

        ctx.save();
        ctx.shadowColor = chart.data.datasets[0].borderColor;
        ctx.shadowBlur = 12;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
    },
    afterDatasetDraw(chart) {
        chart.ctx.restore();
    }
};

function renderTopAssets(data) {
    if (!data || !Array.isArray(data)) return;

    const container = document.getElementById("topAssets");

    if (!container) return;

    container.innerHTML = "";

    data.slice(0, 5).forEach((coin, index) => {
        const first = coin.trend?.[0] || 0;
        const last = coin.trend?.at(-1) || 0;

        const change =
            first !== 0
                ? ((last - first) / first) * 100
                : 0;

        const color =
            change >= 0
                ? "#16c784"
                : "#ea3943";

        const card = document.createElement("div");

        card.style.cursor = "pointer";

        card.onclick = () => {
            window.location.href = `coin.html?coin=${coin.coin}`;
        };

        card.className = "asset-card";

        card.innerHTML = `
            <div class="top-card-header">
                <img
                    class="top-card-icon"
                    src="${coin.image || ''}"
                    onerror="this.onerror=null; this.src='https://cdn-icons-png.flaticon.com/512/149/149071.png';"
                >
            </div>

            <div class="asset-title">
                ${coin.coin}
            </div>

            <div class="asset-price">
                ${formatCurrency(coin.latest_price)}
            </div>

            <div style="
                color:${color};
                font-size:13px;
                font-weight:600;
                margin-top:6px;
            ">
                ${change.toFixed(2)}%
            </div>

            <div class="mini-chart-wrapper">
                <canvas id="chart-${index}"></canvas>
            </div>
        `;

        container.appendChild(card);

        new Chart(document.getElementById(`chart-${index}`), {
            type: "line",
            plugins: [lineGlowPlugin],

            data: {
                labels: coin.trend.map((_, i) => i),

                datasets: [{
                    data: coin.trend,

                    borderColor: color,

                    backgroundColor: `${color}33`,

                    borderWidth: 4,

                    fill: true,

                    pointRadius: 0,

                    pointHoverRadius: 4,

                    tension: 0.45,

                    shadowOffsetX: 0,
                    shadowOffsetY: 0,
                    shadowBlur: 12,
                    shadowColor: color
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 2.5,
                animation: false,

                plugins: {
                    legend: {
                        display: false
                    },

                    tooltip: {
                        enabled: false
                    }
                },

                scales: {
                    x: {
                        display: false
                    },

                    y: {
                        display: false
                    }
                }
            }
        });
    });
}

// ======================================================
// LOAD TOP 10 BAR CHART
// ======================================================

function renderTopCryptoBarChart(data) {

    if (!data || !Array.isArray(data)) return;

    const top10 = data.slice(0, 10);

    const labels = top10.map(coin => coin.coin);

    const prices = top10.map(coin =>
        Number(coin.latest_price ?? coin.price)
    );

    const colors = [
        "#f7931a",
        "#3b82f6",
        "#8b5cf6",
        "#facc15",
        "#14b8a6",
        "#ec4899",
        "#22c55e",
        "#38bdf8",
        "#f43f5e",
        "#7c3aed"
    ];

    const ctx = document.getElementById("topCryptoChart");

    if (!ctx) {
        console.error("❌ topCryptoChart canvas not found");
        return;
    }

    if (topCryptoChart) {
        topCryptoChart.destroy();
    }

    topCryptoChart = new Chart(ctx, {
        type: "bar",

        data: {
            labels: labels,

            datasets: [{
                data: prices,
                backgroundColor: colors,
                borderRadius: 8,
                barThickness: 45
            }]
        },

        plugins: [{
            id: "barValueLabels",
            afterDatasetsDraw(chart) {
                const { ctx } = chart;

                chart.data.datasets[0].data.forEach((value, index) => {
                    const meta = chart.getDatasetMeta(0);
                    const bar = meta.data[index];

                    ctx.save();
                    ctx.fillStyle = "#ffffff";
                    ctx.font = "bold 13px Inter";
                    ctx.textAlign = "center";
                    ctx.textBaseline = "bottom";

                    ctx.fillText(
                        formatCurrency(value),
                        bar.x,
                        bar.y - 8
                    );

                    ctx.restore();
                });
            }
        }],

        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,

            layout: {
                padding: {
                    top: 30
                }
            },

            plugins: {
                legend: {
                    display: false
                },

                tooltip: {
                    backgroundColor: "#111827",
                    titleColor: "#fff",
                    bodyColor: "#fff",
                    displayColors: false,

                    callbacks: {
                        label: function(context) {
                            return `Price: ${formatCurrency(context.raw)}`;
                        }
                    }
                }
            },

            scales: {
                x: {
                    ticks: {
                        display: false
                    },

                    grid: {
                        display: false
                    }
                },

                y: {
                    beginAtZero: true,

                    ticks: {
                        color: "#9ca3af",

                        callback: function(value) {
                            return "$" + Number(value).toLocaleString("en-US");
                        }
                    },

                    grid: {
                        color: "rgba(255,255,255,0.08)"
                    }
                }
            }
        }
    });

        const labelContainer = document.getElementById("cryptoLabels");

    if (!labelContainer) return;

    labelContainer.innerHTML = "";

    top10.forEach(coin => {
        labelContainer.innerHTML += `
            <div class="crypto-label-item">
                <img 
                    src="${coin.image || ''}" 
                    onerror="this.onerror=null; this.src='https://cdn-icons-png.flaticon.com/512/149/149071.png';"
                >

                <div class="crypto-name">
                    ${coin.name || coin.coin}
                </div>
        `;
    });
}
// ======================================================
// LOAD TABLE
// ======================================================

function renderTable(data) {

    if (!data || !Array.isArray(data)) return;

    const tbody = document.getElementById("dataTable");

    if (!tbody) return;

    tbody.innerHTML = "";

    data.forEach((row, index) => {
        const change1h = row.change_1h ?? 0;
        const change24h = row.change_24h ?? 0;
        const change7d = row.change_7d ?? 0;

        const chartColor =
            change7d >= 0
                ? "#16c784"
                : "#ea3943";

        const tr = `
            <tr>
                <td class="rank">
                    ${index + 1}
                </td>

                <td>
                    <div class="coin-cell">
                        <img 
                            class="coin-icon"
                            src="${row.image || ''}"
                            onerror="this.onerror=null; this.src='https://cdn-icons-png.flaticon.com/512/149/149071.png';"
                        >

                        <div class="coin-info">
                            <div class="coin-name">
                                ${row.coin}
                            </div>

                            <div class="coin-symbol">
                                ${row.coin}
                            </div>
                        </div>
                    </div>
                </td>

                <td class="price">
                    ${formatCurrency(row.latest_price ?? row.price)}
                </td>

                <td class="${change1h >= 0 ? 'green' : 'red'}">
                    ${formatPercent(change1h)}
                </td>

                <td class="${change24h >= 0 ? 'green' : 'red'}">
                    ${formatPercent(change24h)}
                </td>

                <td class="${change7d >= 0 ? 'green' : 'red'}">
                    ${formatPercent(change7d)}
                </td>

                <td>
                    ${formatCurrency(row.volume)}
                </td>

                <td>
                    ${formatCurrency(row.market_cap)}
                </td>

                <td>
                    <div class="spark-wrapper">
                        <canvas 
                            id="spark-${index}" 
                            class="sparkline">
                        </canvas>
                    </div>
                </td>
            </tr>
        `;

        tbody.insertAdjacentHTML("beforeend", tr);

        const sparkData =
            Array.isArray(row.trend) &&
            row.trend.length > 0
                ? row.trend
                : null;

        if (!sparkData) return;

        const canvas = document.getElementById(`spark-${index}`);

        if (!canvas) return;

        new Chart(canvas, {
            type: "line",

            data: {
                labels: sparkData.map((_, i) => i),

                datasets: [{
                    data: sparkData,
                    borderColor: chartColor,
                    borderWidth: 2,
                    fill: false,
                    pointRadius: 0,
                    tension: 0.4
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,

                plugins: {
                    legend: {
                        display: false
                    },

                    tooltip: {
                        enabled: false
                    }
                },

                scales: {
                    x: {
                        display: false
                    },

                    y: {
                        display: false
                    }
                }
            }
        });
    });
}

// ======================================================
// INIT
// ======================================================

let dashboardData = null;

async function initDashboard() {
    dashboardData = await fetchData("/dashboard-data");

    if (!dashboardData) return;

    renderSummary(dashboardData.summary);
    renderTrending(dashboardData.trending);
    renderGainers(dashboardData.gainers);
    renderTopAssets(dashboardData.top_assets);
    renderTopCryptoBarChart(dashboardData.table);
    renderTable(dashboardData.table);
}

initDashboard();

// ======================================================
// AUTO REFRESH
// ======================================================

setInterval(() => {
    initDashboard();
}, 60000);

// ======================================================
//  FRONTEND RELOAD FIX
// ======================================================

window.addEventListener("pageshow", () => {
    initDashboard();
});