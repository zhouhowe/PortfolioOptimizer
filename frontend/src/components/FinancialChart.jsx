import React, { useEffect, useRef, useState } from 'react';
import { createChart, AreaSeries, LineSeries } from 'lightweight-charts';

const FinancialChart = ({ data, benchmarkData, equitySymbol }) => {
  const chartContainerRef = useRef();
  const chartRef = useRef();
  const portfolioSeriesRef = useRef();
  const benchmarkSeriesRef = useRef();
  const [activeRange, setActiveRange] = useState('ALL');

  useEffect(() => {
    if (!data || !chartContainerRef.current) return;

    // Initialize Chart
    const handleResize = () => {
      chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
    };

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { color: '#ffffff' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      timeScale: {
        borderColor: '#D1D5DB',
        timeVisible: true,
      },
      rightPriceScale: {
        borderColor: '#D1D5DB',
      },
      crosshair: {
        mode: 1, // Magnet mode
        vertLine: {
            width: 1,
            color: '#758696',
            style: 3,
            labelBackgroundColor: '#758696',
        },
        horzLine: {
            color: '#758696',
            labelBackgroundColor: '#758696',
        },
      },
    });

    chartRef.current = chart;

    // Add Portfolio Series (Area Chart for main focus)
    const portfolioSeries = chart.addSeries(AreaSeries, {
      topColor: 'rgba(30, 58, 138, 0.4)', // Indigo-800 with opacity
      bottomColor: 'rgba(30, 58, 138, 0.0)',
      lineColor: '#1E3A8A', // Indigo-900 (Dark Blue)
      lineWidth: 2,
      title: 'Portfolio Value',
    });
    
    // Map data: { date: 'yyyy-mm-dd', total_value: number } -> { time: 'yyyy-mm-dd', value: number }
    const chartData = data.map(item => ({
        time: item.date,
        value: item.total_value
    }));
    portfolioSeries.setData(chartData);
    portfolioSeriesRef.current = portfolioSeries;

    // Add Benchmark Series (Line Chart, comparison)
    if (benchmarkData) {
        const benchSeries = chart.addSeries(LineSeries, {
            color: '#DC2626', // Red-600 (High contrast vs Blue)
            lineWidth: 2,
            lineStyle: 0, // Solid line for clarity
            title: `Benchmark (${equitySymbol} Buy & Hold)`,
        });
        
        const benchChartData = benchmarkData.map(item => ({
            time: item.date,
            value: item.benchmark_value
        }));
        benchSeries.setData(benchChartData);
        benchmarkSeriesRef.current = benchSeries;
    }

    // Legend
    const legend = document.createElement('div');
    legend.style.position = 'absolute';
    legend.style.left = '12px';
    legend.style.top = '12px';
    legend.style.zIndex = 1;
    legend.style.fontSize = '12px';
    legend.style.lineHeight = '18px';
    legend.style.fontWeight = '300';
    legend.style.fontFamily = 'Inter, system-ui, sans-serif';
    chartContainerRef.current.appendChild(legend);

    const updateLegend = (param) => {
        const validCrosshairPoint = !(
            param === undefined || param.time === undefined || param.point.x < 0 || param.point.x > chartContainerRef.current.clientWidth || param.point.y < 0 || param.point.y > 400
        );

        let dateStr = '';
        let portVal = '';
        let benchVal = '';

        if (validCrosshairPoint) {
            const time = param.time;
            dateStr = time.year + '-' + String(time.month).padStart(2, '0') + '-' + String(time.day).padStart(2, '0');
            const portPrice = param.seriesData.get(portfolioSeries);
            const benchPrice = param.seriesData.get(benchmarkSeriesRef.current);
            portVal = portPrice !== undefined ? `$${portPrice.toFixed(2)}` : '';
            benchVal = benchPrice !== undefined ? `$${benchPrice.toFixed(2)}` : '';
        } else {
            // Show last values
            if (chartData.length > 0) {
                const lastItem = chartData[chartData.length - 1];
                dateStr = lastItem.time; // already string yyyy-mm-dd
                portVal = `$${lastItem.value.toFixed(2)}`;
                if (benchmarkSeriesRef.current) {
                    // Need to get data from series, but series.data() is not directly accessible like array easily in API v4+ without helper?
                    // We have the source data `benchmarkData`.
                    const lastBench = benchmarkData[benchmarkData.length - 1];
                    benchVal = `$${lastBench.benchmark_value.toFixed(2)}`;
                }
            }
        }

        legend.innerHTML = `
            <div style="display: flex; gap: 16px;">
                <div>${dateStr}</div>
                <div style="color: #1E3A8A; font-weight: 600;">
                    Portfolio: ${portVal}
                </div>
                ${benchVal ? `
                <div style="color: #DC2626; font-weight: 600;">
                    Benchmark: ${benchVal}
                </div>
                ` : ''}
            </div>
        `;
    };

    chart.subscribeCrosshairMove(updateLegend);
    updateLegend(undefined); // Initial render

    // Fit Content
    chart.timeScale().fitContent();

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
      if(legend && legend.parentNode) legend.parentNode.removeChild(legend);
    };
  }, [data, benchmarkData]); // Re-create on data change

  const setTimeRange = (months) => {
    if (!chartRef.current || !data || data.length === 0) return;
    
    let rangeLabel = 'ALL';
    if (months === 1) rangeLabel = '1M';
    if (months === 6) rangeLabel = '6M';
    if (months === 12) rangeLabel = '1Y';
    setActiveRange(rangeLabel);

    if (months === 0) {
        chartRef.current.timeScale().fitContent();
        return;
    }

    const lastDateStr = data[data.length - 1].date;
    const lastDate = new Date(lastDateStr);
    
    // Calculate start date
    const startDate = new Date(lastDate);
    startDate.setMonth(startDate.getMonth() - months);
    
    // Convert to yyyy-mm-dd for logic (approximation for logic, or use logical index)
    // Lightweight charts uses logical range mostly, but setVisibleRange takes time objects.
    // Format: { from: '2020-01-01', to: '2020-06-01' }
    
    const formatDate = (d) => d.toISOString().split('T')[0];

    chartRef.current.timeScale().setVisibleRange({
        from: formatDate(startDate),
        to: formatDate(lastDate),
    });
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-900">Portfolio Performance vs {equitySymbol} (Benchmark)</h3>
        <div className="flex space-x-2">
            {['1M', '6M', '1Y', 'ALL'].map((label) => (
                <button
                    key={label}
                    onClick={() => {
                        if(label === '1M') setTimeRange(1);
                        else if(label === '6M') setTimeRange(6);
                        else if(label === '1Y') setTimeRange(12);
                        else setTimeRange(0);
                    }}
                    className={`px-3 py-1 text-xs font-medium rounded-md ${
                        activeRange === label 
                        ? 'bg-indigo-100 text-indigo-700' 
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                >
                    {label}
                </button>
            ))}
        </div>
      </div>
      <div ref={chartContainerRef} className="w-full h-96 relative" />
    </div>
  );
};

export default FinancialChart;
