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