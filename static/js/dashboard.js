const isDarkMode = document.documentElement.classList.contains('dark');

const chartTheme = {
    mode: isDarkMode ? 'dark' : 'light',
    monochrome: {
        enabled: false
    },
    colors: isDarkMode ? ['#9333ea', '#f472b6'] : ['#c084fc', '#db2777'],
    background: 'transparent',
    foreColor: isDarkMode ? '#E2E8F0' : '#334155'
};

// Common chart settings
const commonChartSettings = {
    height: 320,
    type: 'area',
    toolbar: { show: false },
    zoom: { enabled: true },
    background: 'transparent',
    events: {
        mounted: function(chartContext, config) {
            const series = chartContext.w.config.series[0];
            if (!series.data.length || (series.data.length === 1 && series.data[0] === 0)) {
                chartContext.updateOptions({
                    annotations: {
                        position: 'center',
                        texts: [{
                            x: '40%',
                            y: '55%',
                            text: 'No data for current month',
                            style: {
                                fontSize: '18px',
                                fontFamily: 'inherit',
                                color: isDarkMode ? '#94A3B8' : '#475569'
                            }
                        }]
                    }
                });
            }
        }
    }
};


// Earnings Chart
const revenueOptions = {
    series: [{
        name: 'Earnings',
        data: chartData.sums.length ? chartData.sums : [0]
    }],
    chart: {
        ...commonChartSettings
    },
    theme: chartTheme,
    grid: {
        borderColor: isDarkMode ? '#475569' : '#CBD5E1',
        strokeDashArray: 2,
        padding: {
            left: 10,
            right: 10,
            bottom: 0
        }
    },
    dataLabels: { enabled: false },
    stroke: {
        curve: 'smooth',
        width: 3,
        colors: isDarkMode ? ['#9333ea'] : ['#c084fc']
    },
    xaxis: {
        categories: chartData.dates.length ? chartData.dates : [new Date().toISOString()],
        type: 'datetime',
        labels: {
            style: {
                colors: isDarkMode ? '#94A3B8' : '#475569'
            },
            formatter: function(value) {
                return new Date(value).toLocaleDateString('default', {
                    day: 'numeric',
                    month: 'numeric'
                });
            }
        },
        tickAmount: 6
    },
    yaxis: {
        show: false
    },
    states: {
        normal: { filter: { type: 'none' } },
        hover: { filter: { type: 'none' } },
        active: {
            allowMultipleDataPointsSelection: false,
            filter: { type: 'none' }
        }
    },
    tooltip: {
        theme: isDarkMode ? 'dark' : 'light',
        style: {
            fontSize: '12px',
            fontFamily: 'inherit'
        },
        x: {
            format: 'dd MMM'
        },
        y: {
            formatter: function(value) {
                if (value === 0) return 'No data';
                return '$' + value.toFixed(2);
            }
        },
        cssClass: 'apexcharts-tooltip',
        theme: 'dark',
        fillSeriesColor: false,
        style: {
            background: isDarkMode ? '#334155' : '#ffffff',
            color: isDarkMode ? '#e2e8f0' : '#334155'
        }
    },
    fill: {
        type: 'gradient',
        gradient: {
            shade: 'dark',
            type: 'vertical',
            shadeIntensity: 0.3,
            gradientToColors: isDarkMode ? ['#f472b6'] : ['#db2777'],
            inverseColors: false,
            opacityFrom: 0.6,
            opacityTo: 0.1
        }
    },
    noData: {
        text: 'No data available for current month',
        align: 'center',
        verticalAlign: 'middle',
        offsetX: 0,
        offsetY: 0,
        style: {
            color: isDarkMode ? '#94A3B8' : '#475569',
            fontSize: '14px',
            fontFamily: 'inherit'
        }
    }
};

// Performance Chart
const performanceOptions = {
    series: [{
        name: 'Performance',
        data: chartData.percents.length ? chartData.percents : [0]
    }],
    chart: {
        ...commonChartSettings,
        type: 'line'
    },
    theme: chartTheme,
    grid: {
        borderColor: isDarkMode ? '#475569' : '#CBD5E1',
        strokeDashArray: 2,
        padding: {
            left: 10,
            right: 10,
            bottom: 0
        }
    },
    dataLabels: { enabled: false },
    stroke: {
        curve: 'smooth',
        width: 3,
        colors: isDarkMode ? ['#9333ea'] : ['#c084fc']
    },
    xaxis: {
        categories: chartData.dates.length ? chartData.dates : [new Date().toISOString()],
        type: 'datetime',
        labels: {
            style: {
                colors: isDarkMode ? '#94A3B8' : '#475569'
            },
            formatter: function(value) {
                return new Date(value).toLocaleDateString('default', {
                    day: 'numeric',
                    month: 'numeric'
                });
            }
        },
        tickAmount: 6
    },
    yaxis: {
        show: false
    },
    states: {
        normal: { filter: { type: 'none' } },
        hover: { filter: { type: 'none' } },
        active: {
            allowMultipleDataPointsSelection: false,
            filter: { type: 'none' }
        }
    },
    tooltip: {
        theme: isDarkMode ? 'dark' : 'light',
        style: {
            fontSize: '12px',
            fontFamily: 'inherit'
        },
        x: {
            format: 'dd MMM'
        },
        y: {
            formatter: function(value) {
                if (value === 0) return 'No data';
                return value.toFixed(2) + '%';
            }
        },
        cssClass: 'apexcharts-tooltip',
        theme: 'dark',
        fillSeriesColor: false,
        style: {
            background: isDarkMode ? '#334155' : '#ffffff',
            color: isDarkMode ? '#e2e8f0' : '#334155'
        }
    },
    markers: {
        size: 4,
        colors: isDarkMode ? ['#9333ea'] : ['#c084fc'],
        strokeColors: isDarkMode ? '#9333ea' : '#c084fc',
        strokeWidth: 2
    },
    noData: {
        text: 'No data available for current month',
        align: 'center',
        verticalAlign: 'middle',
        offsetX: 0,
        offsetY: 0,
        style: {
            color: isDarkMode ? '#94A3B8' : '#475569',
            fontSize: '14px',
            fontFamily: 'inherit'
        }
    }
};

const earningsChart = new ApexCharts(document.querySelector("#earningsChart"), revenueOptions);
const performanceChart = new ApexCharts(document.querySelector("#performanceChart"), performanceOptions);

earningsChart.render();
performanceChart.render();

document.addEventListener('theme-changed', () => {
    const newIsDarkMode = document.documentElement.classList.contains('dark');
    const newTheme = {
        mode: newIsDarkMode ? 'dark' : 'light',
        monochrome: {
            enabled: false
        },
        colors: newIsDarkMode ? ['#9333ea', '#f472b6'] : ['#c084fc', '#db2777'],
        background: 'transparent',
        foreColor: newIsDarkMode ? '#E2E8F0' : '#334155'
    };
    
    earningsChart.updateOptions({ theme: newTheme });
    performanceChart.updateOptions({ theme: newTheme });
});
