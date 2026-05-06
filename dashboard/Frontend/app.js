const API = "http://localhost:5000";

let mainChart = null;

// ======================================================
// 🔥 FETCH HELPER
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
// 🔥 FORMAT HELPERS
// ======================================================

function formatCurrency(num) {

    if (num === null || num === undefined) {
        return "N/A";
    }

    return `$${Number(num).toLocaleString("en-US", {
        maximumFractionDigits: 2
    })}`;
}

function formatPercent(num) {

    if (num === null || num === undefined) {
        return "N/A";
    }

    return `${Number(num).toFixed(2)}%`;
}

// ======================================================
// 🔥 LOAD SUMMARY
// ======================================================

async function loadSummary() {

    const data = await fetchData("/summary");

    if (!data) return;

    document.getElementById("avgPrice").innerText =
        formatCurrency(data.avg_price);

    document.getElementById("maxPrice").innerText =
        formatCurrency(data.max_price);

    document.getElementById("minPrice").innerText =
        formatCurrency(data.min_price);
}

// ======================================================
// 🔥 LOAD TRENDING
// ======================================================

async function loadTrending() {

    const data = await fetchData("/trending");

    if (!data) return;

    const container = document.getElementById("trendingList");

    if (!container) {
        console.error("❌ trendingList not found");
        return;
    }

    container.innerHTML = "";

    data.forEach((coin, i) => {

        const change = coin.change ?? 0;

        const color =
            change >= 0
                ? "green"
                : "red";

        const arrow =
            change >= 0
                ? "▲"
                : "▼";

        const item = `
            <div class="insight-item">

                <div class="insight-left">

                    <span class="rank">
                        #${i + 1}
                    </span>

                    <img 
                        class="coin-icon"
                        src="${coin.image}"
                        onerror="this.onerror=null; this.src='https://cdn-icons-png.flaticon.com/512/149/149071.png';"
                    >

                    <div>

                        <div class="insight-name">
                            ${coin.name}
                        </div>

                        <div class="coin-symbol">
                            ${coin.symbol}
                        </div>

                    </div>

                </div>

                <div class="insight-right ${color}">
                    ${arrow} ${Math.abs(change).toFixed(2)}%
                </div>

            </div>
        `;

        container.innerHTML += item;
    });
}

// ======================================================
// 🔥 LOAD TOP GAINERS
// ======================================================

async function loadGainers() {

    const data = await fetchData("/top-gainers");

    if (!data) return;

    const container = document.getElementById("gainersList");

    if (!container) {
        console.error("❌ gainersList not found");
        return;
    }

    container.innerHTML = "";

    data.forEach((coin, i) => {

        const change = coin.change ?? 0;

        const item = `
            <div class="insight-item">

                <div class="insight-left">

                    <span class="rank">
                        #${i + 1}
                    </span>

                    <img 
                        class="coin-icon"
                        src="${coin.image}"
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

        container.innerHTML += item;
    });
}

// ======================================================
// 🔥 LOAD TOP ASSETS
// ======================================================

async function loadTopAssets() {

    const data = await fetchData("/top-assets");

    if (!data) return;

    const container = document.getElementById("topAssets");

    container.innerHTML = "";

    data.forEach((coin, index) => {

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

        card.className = "asset-card";

        card.innerHTML = `

            <div class="top-card-header">

                <img
                    class="top-card-icon"
                    src="${coin.image}"
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

            data: {

                labels: coin.trend.map((_, i) => i),

                datasets: [{

                    data: coin.trend,

                    borderColor: color,

                    backgroundColor: `${color}22`,

                    borderWidth: 2,

                    fill: true,

                    pointRadius: 0,

                    tension: 0.4
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
// 🔥 LOAD TABLE
// ======================================================

async function loadTable() {

    const data = await fetchData("/table");

    if (!data) return;

    const tbody = document.getElementById("dataTable");

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
                            src="${row.image}"
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
                    ${formatCurrency(row.price)}
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
// 🔥 MAIN CHART
// ======================================================

async function loadChart(coin = "BTC") {

    // ======================================================
    // 🔥 FETCH DATA
    // ======================================================

    const data = await fetchData(`/trend/${coin}`);

    if (!data || !Array.isArray(data) || data.length === 0) {
        console.warn(`⚠️ No chart data found for ${coin}`);
        return;
    }

    // ======================================================
    // 🔥 FORMAT DATA
    // ======================================================

    const labels = data.map(r => {

    const d = new Date(r.date);

    const day = String(d.getDate()).padStart(2, "0");

    const month = d.toLocaleString("en-US", {
        month: "long"
    });

    const year = d.getFullYear();

    return `${day}-${month}-${year}`;
    });

    const prices = data.map(r => r.price);

    // ======================================================
    // 🔥 GET CANVAS
    // ======================================================

    const ctx = document.getElementById("priceChart");

    if (!ctx) {
        console.error("❌ priceChart canvas not found");
        return;
    }

    // ======================================================
    // 🔥 DESTROY OLD CHART
    // ======================================================

    if (mainChart) {
        mainChart.destroy();
    }

    // ======================================================
    // 🔥 CREATE NEW CHART
    // ======================================================

    mainChart = new Chart(ctx, {

        type: "line",

        data: {

            labels: labels,

            datasets: [{

                label: `${coin} Price`,

                data: prices,

                borderColor: "#16c784",

                backgroundColor: "rgba(22,199,132,0.12)",

                borderWidth: 3,

                fill: true,

                tension: 0.4,

                pointRadius: 0,

                pointHoverRadius: 4
            }]
        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            animation: false,

            interaction: {

                intersect: false,

                mode: "index"
            },

            elements: {

                line: {
                    capBezierPoints: true
                }
            },

            plugins: {

                legend: {
                    display: false
                },

                tooltip: {

                    enabled: true,

                    backgroundColor: "#111827",

                    borderColor: "rgba(255,255,255,0.08)",

                    borderWidth: 1,

                    titleColor: "#fff",

                    bodyColor: "#fff",

                    displayColors: false,

                    padding: 12,

                    callbacks: {

                        label: function(context) {

                            return `Price: $${Number(context.parsed.y).toLocaleString("en-US", {
                                maximumFractionDigits: 2
                            })}`;
                        }
                    }
                }
            },

            scales: {

                x: {

                    grid: {
                        display: false
                    },

                    ticks: {
                        color: "#9ca3af",
                        maxTicksLimit: 8
                    }
                },

                y: {

                    grid: {
                        color: "rgba(255,255,255,0.05)"
                    },

                    ticks: {

                        color: "#9ca3af",

                        callback: function(value) {

                            return "$" + Number(value).toLocaleString("en-US");
                        }
                    }
                }
            }
        }
    });
}
// ======================================================
// 🔥 INIT
// ======================================================

async function initDashboard() {

    await loadSummary();

    await loadTrending();

    await loadGainers();

    await loadTopAssets();

    await loadTable();

    await loadChart("BTC");
}

initDashboard();

// ======================================================
// 🔥 AUTO REFRESH
// ======================================================

setInterval(() => {

    loadSummary();

    loadTrending();

    loadGainers();

    loadTopAssets();

    loadTable();

}, 30000);