import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface PressureHistoryProps {
  history: any;
}

const PressureHistory: React.FC<PressureHistoryProps> = ({ history }) => {
  console.log('Rendering Pronation Index Chart', !!history);
  const chartData = React.useMemo(() => {
    if (!history) return { labels: [], datasets: [] };
    
    const entries = Object.values(history) as any[];
    const sortedEntries = entries.sort((a, b) => a.timestamp - b.timestamp).slice(-30);
    
    const labels = sortedEntries.map(e => new Date(e.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    
    // Pronation Index = Inner Pressure - Outer Pressure
    // Positive: Overpronation (안쪽 쏠림), Negative: Supination (바깥쪽 쏠림)
    const leftPronation = sortedEntries.map(e => e.side === 'left' ? (e.sensors.s2_kpa - e.sensors.s3_kpa) : null);
    const rightPronation = sortedEntries.map(e => e.side === 'right' ? (e.sensors.s2_kpa - e.sensors.s3_kpa) : null);

    return {
      labels,
      datasets: [
        {
          label: '왼발 내전 지수',
          data: leftPronation,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 2,
          spanGaps: true,
        },
        {
          label: '오른발 내전 지수',
          data: rightPronation,
          borderColor: '#f87171',
          backgroundColor: 'rgba(248, 113, 113, 0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 2,
          spanGaps: true,
        }
      ]
    };
  }, [history]);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index' as const, intersect: false },
    plugins: {
      legend: { 
        display: true, 
        position: 'top' as const,
        labels: { color: '#94a3b8', font: { size: 10 } }
      },
      tooltip: {
        backgroundColor: '#1e2330',
        titleColor: '#94a3b8',
        bodyColor: '#e2e8f0',
        borderColor: '#2a3040',
        borderWidth: 1,
      }
    },
    scales: {
      x: {
        ticks: { color: '#475569', font: { size: 10 }, maxRotation: 0 },
        grid: { color: '#1e2330' },
      },
      y: {
        ticks: {
          color: '#475569',
          font: { size: 10 },
          callback: (v: any) => v > 0 ? `+${v}` : v,
        },
        grid: { 
          color: (context: any) => context.tick.value === 0 ? '#475569' : '#1e2330',
          lineWidth: (context: any) => context.tick.value === 0 ? 2 : 1,
        },
        title: {
          display: true,
          text: '← 외전(요족) | 내전(평발) →',
          color: '#64748b',
          font: { size: 10 }
        }
      }
    }
  };

  return (
    <div className="card flex flex-col" id="history-card" style={{ height: '400px' }}>
      <div className="flex justify-between items-center mb-4">
        <div className="card-title m-0">보행 내전 지수 (Pronation Index)</div>
        <div className="flex gap-4 text-[0.65rem]">
          <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-[#f87171]"></div> 과내전(안쪽 쏠림)</span>
          <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-[#3b82f6]"></div> 외내전(바깥쪽 쏠림)</span>
        </div>
      </div>

      <div className="flex-1 w-full relative">
        <Line data={chartData} options={options} />
      </div>
      
      <div className="mt-4 p-3 bg-[#0d0f14] border border-[#1e2330] rounded-[8px]">
        <p className="text-[0.7rem] text-[#94a3b8] leading-relaxed">
          <strong className="text-[#e2e8f0]">💡 그래프 읽는 법:</strong> 0(중앙선)보다 높으면 발이 안쪽으로 굽는 <span className="text-[#f87171]">과내전</span>, 낮으면 바깥쪽으로 딛는 <span className="text-[#3b82f6]">외내전</span> 성향을 의미합니다. 점들이 0 근처에 머무는 것이 가장 이상적인 중립 보행입니다.
        </p>
      </div>
    </div>
  );
};

export default PressureHistory;
