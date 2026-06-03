import React from 'react';

interface SensorData {
  s1_kpa: number; // Heel
  s2_kpa: number; // Inner
  s3_kpa: number; // Outer
  s4_kpa: number; // Toe
}

interface FootHeatmapProps {
  leftSensors?: SensorData;
  rightSensors?: SensorData;
}

const FootHeatmap: React.FC<FootHeatmapProps> = ({ leftSensors, rightSensors }) => {
  const renderFoot = (side: 'left' | 'right', sensors?: SensorData) => {
    const isLeft = side === 'left';
    
    const points = [
      { id: isLeft ? 'CH0' : 'CH4', label: '발가락', type: 'toe', value: sensors?.s4_kpa || 0, color: isLeft ? '#2563eb' : '#dc2626', top: '12%', left: '50%' },
      { id: isLeft ? 'CH1' : 'CH5', label: '안쪽', type: 'inner', value: sensors?.s2_kpa || 0, color: isLeft ? '#0891b2' : '#d97706', top: '38%', left: '34%' },
      { id: isLeft ? 'CH2' : 'CH6', label: '바깥쪽', type: 'outer', value: sensors?.s3_kpa || 0, color: isLeft ? '#0284c7' : '#b45309', top: '42%', left: '67%' },
      { id: isLeft ? 'CH3' : 'CH7', label: '뒤꿈치', type: 'heel', value: sensors?.s1_kpa || 0, color: isLeft ? '#1d4ed8' : '#991b1b', top: '84%', left: '50%' },
    ];

    return (
      <div className="flex flex-col items-center gap-[10px]">
        <span className={`text-[0.7rem] font-[700] tracking-[0.06em] px-[12px] py-[3px] rounded-[20px] ${isLeft ? 'bg-[#1e3a5f] text-[#60a5fa]' : 'bg-[#3b1f1f] text-[#f87171]'}`}>
          {isLeft ? '왼발' : '오른발'}
        </span>
        <div 
          className="relative flex-shrink-0" 
          style={{ 
            width: '140px', 
            height: '280px', 
            transform: isLeft ? 'none' : 'scaleX(-1)' 
          }}
        >
          <svg className="w-full h-full" viewBox="0 0 160 320" xmlns="http://www.w3.org/2000/svg">
            <path d="M60,10 C40,10 28,30 28,55 C28,80 32,110 36,140 C38,158 36,175 34,195 C30,230 28,260 30,280 C32,300 44,312 60,312 C76,312 100,310 110,300 C120,290 124,270 122,250 C120,230 112,212 108,195 C104,175 104,155 106,138 C110,108 116,80 116,55 C116,30 104,10 80,10 Z"
              fill="#1a1f2e" stroke="#2a3040" strokeWidth="1.5"/>
          </svg>
          
          {/* Points */}
          {points.map((pt) => (
            <div 
              key={pt.id}
              className="pressure-point" 
              style={{ 
                position: 'absolute',
                top: pt.top,
                left: pt.left,
                background: pt.color, 
                boxShadow: `0 0 12px ${pt.color}90`,
                transform: `translate(-50%, -50%) ${!isLeft ? 'scaleX(-1)' : ''}`,
                width: '46px',
                height: '46px',
                borderRadius: '50%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontWeight: '700',
                transition: 'background 0.4s, box-shadow 0.4s',
                zIndex: 10
              }}
            >
              <span style={{ fontSize: '0.48rem', opacity: 0.75, marginBottom: '1px' }}>{pt.id}</span>
              <span style={{ fontSize: '0.5rem', opacity: 0.9 }}>{pt.label}</span>
              <span style={{ fontSize: '0.78rem' }}>{Math.round(pt.value)}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderLegendRow = (side: 'left' | 'right', type: 'toe' | 'inner' | 'outer' | 'heel', value: number) => {
    const isLeft = side === 'left';
    const config = {
      toe: { label: '발가락', ch: isLeft ? 'CH0' : 'CH4', color: isLeft ? '#2563eb' : '#dc2626' },
      inner: { label: '안쪽', ch: isLeft ? 'CH1' : 'CH5', color: isLeft ? '#0891b2' : '#d97706' },
      outer: { label: '바깥쪽', ch: isLeft ? 'CH2' : 'CH6', color: isLeft ? '#0284c7' : '#b45309' },
      heel: { label: '뒤꿈치', ch: isLeft ? 'CH3' : 'CH7', color: isLeft ? '#1d4ed8' : '#991b1b' },
    }[type];

    const percentage = Math.min((value / 150) * 100, 100);

    return (
      <div className="flex items-center gap-[6px] text-[0.68rem] text-[#94a3b8]">
        <div className="w-[8px] h-[8px] rounded-full flex-shrink-0" style={{ background: config.color }}></div>
        <div className="flex flex-col flex-1 gap-[2px]">
          <div className="flex justify-between items-center">
            <span><span className="text-[0.6rem] text-[#475569]">{config.ch}</span> <span className="text-[#cbd5e1]">{isLeft ? '왼발' : '오른발'} {config.label}</span></span>
            <span className="font-[600] text-[#e2e8f0] text-[0.72rem]">{Math.round(value)} kPa</span>
          </div>
          <div className="legend-bar-wrap">
            <div className="legend-bar" style={{ width: `${percentage}%`, background: config.color }}></div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="card h-full" id="heatmap-card">
      <div className="card-title">실시간 압력 히트맵</div>
      
      <div className="flex justify-center gap-[16px]">
        {renderFoot('left', leftSensors)}
        {renderFoot('right', rightSensors)}
      </div>

      <div className="grid grid-cols-2 gap-[8px_16px] mt-[20px]">
        {renderLegendRow('left', 'toe', leftSensors?.s4_kpa || 0)}
        {renderLegendRow('right', 'toe', rightSensors?.s4_kpa || 0)}
        {renderLegendRow('left', 'inner', leftSensors?.s2_kpa || 0)}
        {renderLegendRow('right', 'inner', rightSensors?.s2_kpa || 0)}
        {renderLegendRow('left', 'outer', leftSensors?.s3_kpa || 0)}
        {renderLegendRow('right', 'outer', rightSensors?.s3_kpa || 0)}
        {renderLegendRow('left', 'heel', leftSensors?.s1_kpa || 0)}
        {renderLegendRow('right', 'heel', rightSensors?.s1_kpa || 0)}
      </div>
    </div>
  );
};

export default FootHeatmap;
