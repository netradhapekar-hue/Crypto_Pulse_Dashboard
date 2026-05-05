const API = "http://localhost:5000";

// 🔥 GLOBAL CHART INSTANCE (avoid duplication)
let mainChart = null;

// ======================================================
// 🔥 GENERIC FETCH HELPER
// ======================================================
async function fetchData(endpoint) {
    try {
        const res = await fetch(`${API}${endpoint}`);
        if (!res.ok) throw new Error(`${endpoint} failed`);
        return await res.json();
    } catch (err) {
        console.error(err);
        return null;
    }
}

// ======================================================
// 🔥 LOAD SUMMARY (KPI)
// ======================================================
async function loadSummary() {
    const data = await fetchData("/summary");
    if (!data) return;

    document.getElementById("avgPrice").innerText = data.avg_price.toFixed(2);
    document.getElementById("maxPrice").innerText = data.max_price.toFixed(2);
    document.getElementById("minPrice").innerText = data.min_price.toFixed(2);
}

// ======================================================
// 🔥 LOAD TOP GAINERS
// ======================================================
async function loadGainers() {
    const data = await fetchData("/top-gainers");
    if (!data) return;

    const container = document.getElementById("gainersList");
    container.innerHTML = "";

    data.forEach((coin, i) => {

        const item = `
            <div class="insight-item">
                <div class="insight-left">
                    <span class="rank">#${i + 1}</span>

                    <img 
                        src="https://cryptoicons.org/api/icon/${coin.coin.toLowerCase()}/32"
                        onerror="this.src='https://via.placeholder.com/32'"
                    >

                    <div class="insight-name">${coin.coin}</div>
                </div>

                <div class="insight-right green">
                    ▲ ${coin.change.toFixed(2)}%
                </div>
            </div>
        `;

        container.innerHTML += item;
    });
}

// ======================================================
// 🔥 LOAD TRENDING 
// ======================================================
async function loadTrending() {
    const data = await fetchData("/trending");
    if (!data) return;

    const container = document.getElementById("trendingList");
    container.innerHTML = "";

    data.forEach((coin, i) => {

        const color = coin.change >= 0 ? "green" : "red";
        const arrow = coin.change >= 0 ? "▲" : "▼";

        const item = `
            <div class="insight-item">
                <div class="insight-left">
                    <span class="rank">#${i + 1}</span>

                    <img 
                        src="https://cryptoicons.org/api/icon/${coin.symbol.toLowerCase()}/32"
                        onerror="this.src='https://via.placeholder.com/32'"
                    >

                    <div>
                        <div class="insight-name">${coin.name}</div>
                        <div class="asset-symbol">${coin.symbol}</div>
                    </div>
                </div>

                <div class="insight-right ${color}">
                    ${arrow} ${Math.abs(coin.change).toFixed(2)}%
                </div>
            </div>
        `;

        container.innerHTML += item;
    });
}

// ======================================================
// 🔥 LOAD TOP ASSETS (PREMIUM CARDS)
// ======================================================
async function loadTopAssets() {
    const data = await fetchData("/top-assets");
    if (!data) return;

    const container = document.getElementById("topAssets");
    container.innerHTML = "";

    data.forEach((coin, index) => {

        const first = coin.trend[0] || 0;
        const last = coin.trend.at(-1) || 0;

        const change = first ? ((last - first) / first) * 100 : 0;
        const color = change >= 0 ? "#00ff9f" : "#ff4d6d";

        const card = document.createElement("div");
        card.className = "asset-card";

        card.innerHTML = `
            <div class="asset-title">${coin.coin}</div>
            <div class="asset-price">$${coin.latest_price.toFixed(2)}</div>
            <div style="color:${color}; font-size:13px;">
                ${change.toFixed(2)}%
            </div>
            <canvas id="chart-${index}" height="60"></canvas>
        `;

        container.appendChild(card);

        // 🔥 Mini chart
        new Chart(document.getElementById(`chart-${index}`), {
            type: "line",
            data: {
                labels: coin.trend.map((_, i) => i),
                datasets: [{
                    data: coin.trend,
                    borderColor: color,
                    borderWidth: 2,
                    fill: true,
                    backgroundColor: `${color}22`,
                    tension: 0.4,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false }},
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });
    });
}

// ======================================================
// 🔥 LOAD TABLE (FIXED VERSION)
// ======================================================
async function loadTable() {
    const data = await fetchData("/table");
    if (!data) return;

    const tbody = document.getElementById("dataTable");
    tbody.innerHTML = "";

    data.forEach((row, index) => {

        // 🔥 Safe color handling
        const color = (row.change_7d ?? 0) >= 0 ? "#00ff9f" : "#ff4d6d";

        const tr = `
            <tr>
                <td>${index + 1}</td>

                <td>
                    <div class="coin-cell">
                        <img 
                            src="https://cryptoicons.org/api/icon/${row.coin.toLowerCase()}/32"
                            onerror="this.src='https://via.placeholder.com/32'"
                        >
                        <div>
                            <div class="coin-name">${row.coin}</div>
                            <div class="coin-symbol">${row.coin}</div>
                        </div>
                    </div>
                </td>

                <td>$${row.price?.toFixed(2) || "N/A"}</td>

                <td class="${(row.change_1h ?? 0) >= 0 ? 'green' : 'red'}">
                    ${row.change_1h?.toFixed(2) || "N/A"}%
                </td>

                <td class="${(row.change_24h ?? 0) >= 0 ? 'green' : 'red'}">
                    ${row.change_24h?.toFixed(2) || "N/A"}%
                </td>

                <td class="${(row.change_7d ?? 0) >= 0 ? 'green' : 'red'}">
                    ${row.change_7d?.toFixed(2) || "N/A"}%
                </td>

                <td>$${row.volume ?? "N/A"}</td>
                <td>$${row.market_cap ?? "N/A"}</td>

                <td>
                    <div class="spark-wrapper">
                        <canvas id="spark-${index}" class="sparkline"></canvas>
                    </div>
                </td>
            </tr>
        `;

        tbody.innerHTML += tr;

        

        // ======================================================
        // 🔥 SAFE CHART DATA HANDLING
        // ======================================================

        const sparkData = Array.isArray(row.trend) && row.trend.length > 0
            ? row.trend
            : null;

        if (!sparkData) {
            console.warn("⚠️ Missing trend data for:", row.coin);
            return; // skip chart rendering safely
        }

        // ======================================================
        // 🔥 RENDER CHART
        // ======================================================

        new Chart(document.getElementById(`spark-${index}`), {
            type: "line",
            data: {
                labels: sparkData.map((_, i) => i),
                datasets: [{
                    data: sparkData,
                    borderColor: color,
                    borderWidth: 2,
                    fill: false,
                    pointRadius: 0,
                    tension: 0.4
                }]
            },
            options: {
                plugins: { legend: { display: false }},
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });

    });
}

// ======================================================
// 🔥 LOAD MAIN CHART (DYNAMIC)
// ======================================================
async function loadChart(coin = "BTC") {
    const data = await fetchData(`/trend/${coin}`);
    if (!data) return;

    const labels = data.map(r => r.date);
    const prices = data.map(r => r.price);

    const ctx = document.getElementById("priceChart");

    // 🔥 Destroy old chart if exists
    if (mainChart) {
        mainChart.destroy();
    }

    mainChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: `${coin} Price`,
                data: prices,
                borderColor: "#7b61ff",
                backgroundColor: "rgba(123,97,255,0.2)",
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    ticks: { color: "#aaa" }
                },
                y: {
                    ticks: { color: "#aaa" }
                }
            }
        }
    });
}

// ======================================================
// 🔥 INITIAL LOAD
// ======================================================
async function initDashboard() {
    await loadSummary();
    await loadTopAssets();
    await loadTable();
    await loadChart("BTC");

    await loadTrending();   
    await loadGainers();    
}

initDashboard();