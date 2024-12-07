document.addEventListener('DOMContentLoaded', function() {
    let chart;
    
    function initChart() {
        const isDarkMode = document.documentElement.classList.contains('dark');
        const textColor = isDarkMode ? '#ffffff' : '#000000';
        
        const groupedData = {};
        
        chartData.forEach(item => {
            if (!groupedData[item.date]) {
                groupedData[item.date] = {
                    operations: [],
                    totalSum: 0,
                    totalPercent: 0,
                    totalQuantity: 0
                };
            }
            groupedData[item.date].operations.push(item);
            groupedData[item.date].totalSum += item.sum;
            groupedData[item.date].totalPercent += item.percent;
            groupedData[item.date].totalQuantity += item.quantity;
        });

        const dates = Object.keys(groupedData).sort((a, b) => new Date(a) - new Date(b));
        const series = [
            {
                name: 'Total Sum',
                data: dates.map(date => groupedData[date].totalSum)
            },
            {
                name: 'Average Percent',
                data: dates.map(date => groupedData[date].totalPercent / groupedData[date].operations.length)
            },
            {
                name: 'Total Quantity',
                data: dates.map(date => groupedData[date].totalQuantity)
            }
        ];

        const options = {
            series: series,
            chart: {
                type: 'area',
                height: 320,
                parentHeightOffset: 0,
                toolbar: {
                    show: true
                },
                foreColor: textColor,
                background: 'transparent'
            },
            grid: {
                padding: {
                    left: 0,
                    right: 0
                },
                borderColor: isDarkMode ? '#334155' : '#e2e8f0'
            },
            dataLabels: {enabled: false},
            stroke: {curve: 'smooth', width: 2, connectNulls: true},
            fill: {
                type: 'gradient',
                gradient: {
                    shadeIntensity: 1,
                    opacityFrom: 0.7,
                    opacityTo: 0.3
                }
            },
            xaxis: {
                categories: dates,
                type: 'datetime',
                tickAmount: 6,
                labels: {
                    style: {
                        colors: textColor
                    },
                    formatter: function(value) {
                        const date = new Date(value);
                        return `${String(date.getDate()).padStart(2, '0')}.${String(date.getMonth() + 1).padStart(2, '0')}`;
                    }
                }
            },
            yaxis: [
                {
                    title: {
                        text: 'Total Sum',
                        style: {
                            color: textColor
                        }
                    },
                    labels: {
                        style: {
                            colors: textColor
                        }
                    },
                    decimalsInFloat: 2
                },
                {
                    title: {
                        text: 'Average Percent',
                        style: {
                            color: textColor
                        }
                    },
                    labels: {
                        style: {
                            colors: textColor
                        }
                    },
                    decimalsInFloat: 0,
                    opposite: true
                },
                {
                    title: {
                        text: 'Total Quantity',
                        style: {
                            color: textColor
                        }
                    },
                    labels: {
                        style: {
                            colors: textColor
                        }
                    },
                    decimalsInFloat: 0,
                    opposite: true
                }
            ],
            tooltip: {
                shared: true,
                intersect: false,
                theme: isDarkMode ? 'dark' : 'light',
                y: {
                    formatter: function (value, { seriesIndex }) {
                        if (value === undefined || value === null) return '0';
                        if (seriesIndex === 0) return `$${value.toFixed(2)}`;
                        if (seriesIndex === 1) return `${value.toFixed(2)}%`;
                        return Math.round(value);
                    }
                }
            }
        };

        if (chart) {
            chart.destroy();
        }
        chart = new ApexCharts(document.querySelector("#operations-chart"), options);
        chart.render();
    }

    // Initial chart render
    initChart();

    // Watch for theme changes
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'class') {
                initChart();
            }
        });
    });

    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class']
    });
});
