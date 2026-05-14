const API = "https://crypto-pulse-api-dx3x.onrender.com";
//const API = "http://127.0.0.1:5000";

const params = new URLSearchParams(window.location.search);
const selectedCoinSymbol = params.get("coin");

let coinChart = null;

function formatCurrency(num) {
    if (num === null || num === undefined || num === "") return "N/A";

    const value = Number(num);
    if (isNaN(value)) return "N/A";

    return `$${value.toLocaleString("en-US", {
        minimumFractionDigits: value < 1 ? 6 : 2,
        maximumFractionDigits: value < 1 ? 8 : 2
    })}`;
}

function formatPercent(num) {
    if (num === null || num === undefined) return "N/A";
    return `${Number(num).toFixed(2)}%`;
}

async function loadCoinDetails() {
    const res = await fetch(`${API}/table`);
    const coins = await res.json();

    const coin = coins.find(c => c.coin === selectedCoinSymbol);

    if (!coin) {
        document.getElementById("coinTitle").innerText = "Coin not found";
        return;
    }

    const trend = coin.trend || [];

    const prices = trend.map(item =>
        typeof item === "object" ? Number(item.price) : Number(item)
    );

    const high = prices.length ? Math.max(...prices) : 0;
    const low = prices.length ? Math.min(...prices) : 0;

    document.getElementById("coinIcon").src = coin.image || "";
    document.getElementById("coinTitle").innerText = coin.coin;
    document.getElementById("coinSubtitle").innerText = `${coin.coin} detailed analytics`;

    document.getElementById("coinPrice").innerText = formatCurrency(coin.price);
    document.getElementById("coinChange24h").innerText = formatPercent(coin.change_24h);

    document.getElementById("coinMarketCap").innerText = formatCurrency(coin.market_cap);
    document.getElementById("coinVolume").innerText = formatCurrency(coin.volume);
    document.getElementById("coinChange1h").innerText = formatPercent(coin.change_1h);
    document.getElementById("coinChange24hCard").innerText = formatPercent(coin.change_24h);
    document.getElementById("coinChange7d").innerText = formatPercent(coin.change_7d);
    document.getElementById("coinHigh").innerText = formatCurrency(high);
    document.getElementById("coinLow").innerText = formatCurrency(low);

    document.getElementById("insightOne").innerText =
        `${coin.coin} is ${coin.change_7d >= 0 ? "up" : "down"} ${Math.abs(coin.change_7d).toFixed(2)}% in 7 days.`;

    document.getElementById("insightTwo").innerText =
        `Current volume is ${formatCurrency(coin.volume)}.`;

    document.getElementById("insightThree").innerText =
        `Latest price is ${coin.price > low ? "above" : "near"} the recent low of ${formatCurrency(low)}.`;

    loadChart(trend);
    loadTrendTable(trend);
}

function loadChart(trend) {
    const ctx = document.getElementById("coinChart");

    const labels = trend.map((item, i) =>
        typeof item === "object" ? item.time : `Record ${i + 1}`
    );

    const prices = trend.map(item =>
        typeof item === "object" ? Number(item.price) : Number(item)
    );

    if (coinChart) {
        coinChart.destroy();
    }

    coinChart = new Chart(ctx, {
        type: "line",

        data: {
            labels: labels,

            datasets: [{
                data: prices,
                borderColor: "#16c784",
                backgroundColor: "rgba(22,199,132,0.15)",
                borderWidth: 4,
                fill: true,
                tension: 0.45,
                pointRadius: 0,
                pointHoverRadius: 5
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
                        color: "#9ca3af"
                    },

                    grid: {
                        display: false
                    }
                },

                y: {
                    ticks: {
                        color: "#9ca3af",

                        callback: value =>
                            "$" + Number(value).toLocaleString("en-US")
                    },

                    grid: {
                        color: "rgba(255,255,255,0.06)"
                    }
                }
            }
        }
    });
}

function loadTrendTable(trend) {
    const tbody = document.getElementById("trendTable");
    tbody.innerHTML = "";

    trend.slice().reverse().forEach((item, index) => {
        const price =
            typeof item === "object" ? item.price : item;

        const time =
            typeof item === "object" ? item.time : `Recent Record ${index + 1}`;

        tbody.innerHTML += `
            <tr>
                <td>${index + 1}</td>
                <td>${time}</td>
                <td>${formatCurrency(price)}</td>
            </tr>
        `;
    });
}

loadCoinDetails();