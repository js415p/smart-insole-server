import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  unit?: string;
  icon: LucideIcon;
  color: string;
  description?: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, unit, icon: Icon, color, description }) => {
  return (
    <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-3xl border border-slate-700/50 flex flex-col justify-between hover:bg-slate-800 transition-all duration-300 group">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">{title}</p>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-3xl font-black text-slate-100 group-hover:text-blue-400 transition-colors">{value}</span>
            {unit && <span className="text-slate-500 text-xs font-bold">{unit}</span>}
          </div>
        </div>
        <div className={`p-3 rounded-2xl ${color} bg-opacity-10 border border-white/5`}>
          <Icon className={`w-6 h-6 ${color.replace('bg-', 'text-')}`} />
        </div>
      </div>
      {description && (
        <div className="mt-4 pt-4 border-t border-slate-700/30">
          <p className="text-[10px] text-slate-500 font-medium leading-relaxed">{description}</p>
        </div>
      )}
    </div>
  );
};

export default StatCard;
