import React from 'react';
import { AlertCircle, CheckCircle, Info, AlertTriangle, Activity } from 'lucide-react';

interface DiagnosisData {
  status: string;
  issue_zone: string;
  solution: string;
  is_alert: boolean;
  alert_level: 'info' | 'warning' | 'critical';
  updated_at: number;
}

interface DiagnosisCardProps {
  left?: DiagnosisData;
  right?: DiagnosisData;
}

const DiagnosisCard: React.FC<DiagnosisCardProps> = ({ left, right }) => {
  const getIcon = (level?: string) => {
    switch (level) {
      case 'critical': return <AlertCircle className="w-6 h-6 text-red-500" />;
      case 'warning': return <AlertTriangle className="w-6 h-6 text-amber-500" />;
      case 'info': return <Info className="w-6 h-6 text-blue-500" />;
      default: return <CheckCircle className="w-6 h-6 text-emerald-500" />;
    }
  };

  const getBgColor = (level?: string) => {
    switch (level) {
      case 'critical': return 'bg-red-500/5 border-red-500/20';
      case 'warning': return 'bg-amber-500/5 border-amber-500/20';
      case 'info': return 'bg-blue-500/5 border-blue-500/20';
      default: return 'bg-emerald-500/5 border-emerald-500/20';
    }
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm p-8 rounded-3xl border border-slate-700/50 h-full">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-slate-100 flex items-center gap-3">
          <Activity className="w-6 h-6 text-blue-500" />
          실시간 보행 진단
        </h3>
        <span className="text-[10px] text-slate-500 font-black uppercase tracking-widest">AI Analysis</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left Foot Diagnosis */}
        <div className={`p-5 rounded-2xl border ${getBgColor(left?.alert_level)} transition-all duration-300`}>
          <div className="flex items-center gap-3 mb-4">
            {getIcon(left?.alert_level)}
            <span className="font-black text-slate-100 uppercase tracking-tighter">왼발: {left?.status || '데이터 대기 중'}</span>
          </div>
          <div className="space-y-3">
            <div>
              <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">집중 관리 구역</p>
              <p className="text-xs text-slate-200 font-medium">{left?.issue_zone || '이상 없음'}</p>
            </div>
            <div>
              <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">전문가 처방</p>
              <p className="text-xs text-slate-400 leading-relaxed">{left?.solution || '정상적인 보행 패턴을 유지하고 있습니다.'}</p>
            </div>
          </div>
        </div>

        {/* Right Foot Diagnosis */}
        <div className={`p-5 rounded-2xl border ${getBgColor(right?.alert_level)} transition-all duration-300`}>
          <div className="flex items-center gap-3 mb-4">
            {getIcon(right?.alert_level)}
            <span className="font-black text-slate-100 uppercase tracking-tighter">오른발: {right?.status || '데이터 대기 중'}</span>
          </div>
          <div className="space-y-3">
            <div>
              <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">집중 관리 구역</p>
              <p className="text-xs text-slate-200 font-medium">{right?.issue_zone || '이상 없음'}</p>
            </div>
            <div>
              <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">전문가 처방</p>
              <p className="text-xs text-slate-400 leading-relaxed">{right?.solution || '정상적인 보행 패턴을 유지하고 있습니다.'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiagnosisCard;
