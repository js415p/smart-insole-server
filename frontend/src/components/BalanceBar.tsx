import React from 'react';

interface BalanceBarProps {
  leftRatio: number;
  rightRatio: number;
}

const BalanceBar: React.FC<BalanceBarProps> = ({ leftRatio, rightRatio }) => {
  return (
    <div className="w-full bg-slate-800/50 backdrop-blur-sm p-8 rounded-3xl border border-slate-700/50">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-slate-100">체중 분산 밸런스</h3>
        <span className="px-3 py-1 bg-blue-500/10 text-blue-400 text-[10px] font-black rounded-full border border-blue-500/20 uppercase tracking-widest">Real-time Balance</span>
      </div>
      
      <div className="relative h-12 w-full bg-slate-900 rounded-2xl overflow-hidden flex shadow-inner">
        <div 
          className="h-full bg-gradient-to-r from-blue-600 to-blue-500 transition-all duration-700 ease-out flex items-center justify-center text-sm font-black text-white"
          style={{ width: `${leftRatio}%` }}
        >
          {leftRatio > 15 && `${leftRatio}%`}
        </div>
        <div 
          className="h-full bg-gradient-to-l from-emerald-600 to-emerald-500 transition-all duration-700 ease-out flex items-center justify-center text-sm font-black text-white"
          style={{ width: `${rightRatio}%` }}
        >
          {rightRatio > 15 && `${rightRatio}%`}
        </div>
        
        {/* Center line */}
        <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-white/20 z-10 shadow-[0_0_10px_rgba(255,255,255,0.5)]"></div>
      </div>

      <div className="flex justify-between mt-4 text-xs font-black tracking-tighter">
        <div className="flex flex-col items-start">
          <span className="text-blue-400 mb-1">LEFT FOOT</span>
          <span className="text-slate-500 text-[10px]">왼발 지지율</span>
        </div>
        <div className="flex flex-col items-end">
          <span className="text-emerald-400 mb-1">RIGHT FOOT</span>
          <span className="text-slate-500 text-[10px]">오른발 지지율</span>
        </div>
      </div>
    </div>
  );
};

export default BalanceBar;
