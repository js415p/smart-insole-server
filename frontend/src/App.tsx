import { useEffect, useState } from 'react';
import FootHeatmap from './components/FootHeatmap';
import PressureHistory from './components/PressureHistory';
import { subscribeToLiveUpdates, subscribeToHistory } from './firebase';

function App() {
  const [liveData, setLiveData] = useState<any>(null);
  const [historyData, setHistoryData] = useState<any>(null);
  const [userName, setUserName] = useState('BulkTestUser');
  const [useMockData, setUseMockData] = useState(false);

  const mockLiveData = {
    gait: { count: 6284, is_stepping_left: false, is_stepping_right: false },
    balance: { left_ratio: 47, right_ratio: 53, imbalance_percent: 18.4, max_pressure: 141, max_channel: 'CH7', overload_count: 3 },
    left: { sensors: { s1_kpa: 128, s2_kpa: 85, s3_kpa: 64, s4_kpa: 38 } },
    right: { sensors: { s1_kpa: 141, s2_kpa: 92, s3_kpa: 78, s4_kpa: 45 } }
  };

  useEffect(() => {
    if (useMockData) {
      setLiveData(mockLiveData);
      return;
    }
    const unsubscribeLive = subscribeToLiveUpdates(userName, (data) => {
      setLiveData(data);
    });

    const unsubscribeHistory = subscribeToHistory(userName, (data) => {
      setHistoryData(data);
    });

    return () => {
      unsubscribeLive();
      unsubscribeHistory();
    };
  }, [userName, useMockData]);

  return (
    <div className="min-h-screen bg-[#0d0f14] text-[#e2e8f0] font-sans p-6">
      <header className="flex items-center gap-[12px] mb-[28px]">
        <div className="dot"></div>
        <h1 className="text-[1.2rem] font-[600] text-[#f1f5f9]">스마트 인솔 대시보드</h1>
        <div className="ml-auto flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1 bg-slate-800/40 rounded-full border border-slate-700/50">
            <span className="text-[0.65rem] text-slate-500 font-bold uppercase tracking-wider">User:</span>
            <select 
              value={userName} 
              onChange={(e) => setUserName(e.target.value)}
              className="bg-transparent text-[0.75rem] font-bold focus:outline-none cursor-pointer text-slate-200"
            >
              <option value="BulkTestUser">BulkTestUser</option>
              <option value="RealisticUser">RealisticUser (정밀 시뮬레이션)</option>
              <option value="Taeyoung">태영</option>
            </select>
          </div>
          <button 
            onClick={() => setUseMockData(!useMockData)}
            className={`px-3 py-1 rounded-full text-[0.65rem] font-bold border transition-colors ${useMockData ? 'bg-blue-600 border-blue-500' : 'bg-slate-800 border-slate-700 text-slate-400'}`}
          >
            {useMockData ? 'LIVE' : 'DEMO'}
          </button>
          <span className="text-[0.75rem] text-[#64748b]">
            {liveData ? '연결됨' : '기기 연결 안 됨'}
          </span>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-[420px_1fr] gap-[20px]">
        
        {/* Left Column: Heatmap */}
        <div className="lg:row-span-2">
          <FootHeatmap 
            leftSensors={liveData?.left?.sensors} 
            rightSensors={liveData?.right?.sensors} 
          />
        </div>

        {/* Right Column: Steps & Balance */}
        <div className="card flex flex-col gap-[20px]" id="steps-card">
          <div className="card-title">걸음 수</div>
          
          <div className="flex items-end gap-[8px]">
            <div className="text-[3.2rem] font-[700] leading-none text-[#f1f5f9] tracking-[-0.02em]">
              {(liveData?.gait?.count || 0).toLocaleString()}
            </div>
            <div className="text-[0.95rem] text-[#64748b] pb-[5px]">걸음</div>
          </div>

          <div className="flex gap-[20px]">
            <div className="flex flex-col gap-[4px]">
              <span className="text-[0.63rem] text-[#475569]">압력 불균형률</span>
              <span className="text-[0.95rem] font-[600] text-[#cbd5e1]">{liveData?.balance?.imbalance_percent || 0} %</span>
            </div>
            <div className="flex flex-col gap-[4px]">
              <span className="text-[0.63rem] text-[#475569]">최대 압력</span>
              <span className="text-[0.95rem] font-[600] text-[#cbd5e1]">
                {liveData?.balance?.max_pressure || 0} kPa 
                <span className="text-[0.65rem] text-[#f87171] ml-1">({liveData?.balance?.max_channel || 'N/A'})</span>
              </span>
            </div>
            <div className="flex flex-col gap-[4px]">
              <span className="text-[0.63rem] text-[#475569]">과부하 경고</span>
              <span className="text-[0.95rem] font-[600] text-[#f59e0b]">{liveData?.balance?.overload_count || 0} 회</span>
            </div>
          </div>

          <div className="flex flex-col gap-[8px]">
            <div className="flex justify-between text-[0.68rem] text-[#475569]">
              <span>좌우 체중 분산</span>
              <span>CH0~3 / CH4~7</span>
            </div>
            <div className="flex h-[8px] rounded-[4px] overflow-hidden bg-[#1e2330]">
              <div className="bg-[#2563eb] transition-all duration-700" style={{ width: `${liveData?.balance?.left_ratio || 50}%` }}></div>
              <div className="bg-[#dc2626] transition-all duration-700 flex-1"></div>
            </div>
            <div className="flex justify-between text-[0.65rem] font-[600]">
              <span className="text-[#60a5fa]">왼발 {liveData?.balance?.left_ratio || 50}%</span>
              <span className="text-[#f87171]">오른발 {liveData?.balance?.right_ratio || 50}%</span>
            </div>
          </div>
        </div>

        {/* Right Column: History Chart */}
        <div className="flex flex-col">
          <PressureHistory history={historyData} />
        </div>

      </div>
    </div>
  );
}

export default App;
