const oilCtx = document.getElementById('oilChart');

new Chart(oilCtx, {
    type: 'line',
    data: {
        labels: ['Jan','Feb','Mar','Apr','May'],
        datasets: [{
            label: 'Oil Price ($)',
            data: [70, 72, 75, 73, 78],
            borderWidth: 2
        }]
    }
});

const goldCtx = document.getElementById('goldChart');

new Chart(goldCtx, {
    type: 'line',
    data: {
        labels: ['Jan','Feb','Mar','Apr','May'],
        datasets: [{
            label: 'Gold Price ($)',
            data: [1800, 1820, 1850, 1830, 1880],
            borderWidth: 2
        }]
    }
});
// Sample price data
const oilPrices = [70, 72, 75, 73, 78];
const goldPrices = [1900, 1950, 1920, 1980, 2000];

// Function to check rising/falling
function getPerformance(prices) {
    const first = prices[0];
    const last = prices[prices.length - 1];

    if (last > first) {
        return "Rising 📈";
    } else if (last < first) {
        return "Falling 📉";
    } else {
        return "Stable ➖";
    }
}

// Display results
document.getElementById("oilPerformance").innerText =
    getPerformance(oilPrices);

document.getElementById("goldPerformance").innerText =
    getPerformance(goldPrices);