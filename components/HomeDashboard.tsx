
import React from 'react';
import { SystemStats, Violation, ThreatLevel } from '../types';

interface HomeDashboardProps {
  stats: SystemStats;
  violations: Violation[];
  onStart: () => void;
  availableCameras: MediaDeviceInfo[];
  selectedCameraId: string;
  onCameraSelect: (id: string) => void;
}

const HomeDashboard: React.FC<HomeDashboardProps> = ({ 
  stats, 
  violations, 
  onStart, 
  availableCameras, 
  selectedCameraId, 
  onCameraSelect 
}) => {
  const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const currentDate = new Date().toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' });

  return (
    <div className="relative h-full w-full bg-black overflow-hidden flex flex-col items-center justify-between p-10">
      {/* iOS 18 Animated Wallpaper Effect */}
      <div className="absolute top-0 left-0 w-full h-full z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[10%] left-[20%] w-[60%] h-[60%] bg-blue-600/30 blur-[150px] rounded-full animate-pulse" />
        <div className="absolute bottom-[20%] right-[10%] w-[50%] h-[50%] bg-purple-600/20 blur-[150px] rounded-full" />
        <div className="absolute top-[50%] left-[-10%] w-[40%] h-[40%] bg-pink-600/10 blur-[150px] rounded-full" />
      </div>

      {/* iOS 18 Lock Screen Time */}
      <div className="w-full max-w-6xl flex flex-col items-center space-y-1 z-10 animate-fade-in">
        <p className="text-xl font-semibold text-white/80 tracking-wide uppercase">{currentDate}</p>
        <h1 className="text-[10rem] font-bold tracking-tighter text-white leading-none drop-shadow-[0_0_20px_rgba(255,255,255,0.2)]">
          {currentTime}
        </h1>
      </div>

      {/* iOS Control Center Styled Grid */}
      <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-4 lg:grid-cols-4 gap-6 z-10">
        
        {/* Helmet/Safety Widget */}
        <div className="col-span-1 bg-white/10 backdrop-blur-3xl border border-white/20 p-6 rounded-[2.5rem] shadow-2xl flex flex-col justify-between aspect-square transition-transform hover:scale-[1.02]">
          <div className="flex justify-between items-start">
            <div className={`p-4 rounded-2xl ${stats.helmetStatus ? 'bg-emerald-500/20' : 'bg-red-500/20'}`}>
              <svg className={`w-8 h-8 ${stats.helmetStatus ? 'text-emerald-400' : 'text-red-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
          </div>
          <div>
            <h3 className="text-3xl font-black text-white">{stats.helmetStatus ? "SECURE" : "UNSAFE"}</h3>
            <p className="text-white/50 text-xs font-bold uppercase tracking-widest mt-1">PPE Compliance</p>
          </div>
          <div className="flex gap-2">
            <div className={`h-2 flex-1 rounded-full ${stats.helmetStatus ? 'bg-emerald-500 shadow-[0_0_10px_#10b981]' : 'bg-red-500'}`} />
            <div className="h-2 flex-1 rounded-full bg-white/10" />
          </div>
        </div>

        {/* Telemetry Stats */}
        <div className="col-span-1 md:col-span-2 bg-white/10 backdrop-blur-3xl border border-white/20 p-8 rounded-[2.5rem] shadow-2xl flex flex-col justify-between transition-transform hover:scale-[1.02]">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-sm font-black text-white/40 uppercase tracking-[0.3em]">Neural Telemetry</h3>
            <span className="flex h-3 w-3 rounded-full bg-blue-500 animate-ping"></span>
          </div>
          <div className="grid grid-cols-2 gap-8">
            <div className="space-y-1">
              <p className="text-white/40 text-[10px] font-black uppercase">Rel Speed</p>
              <p className="text-5xl font-black text-white tracking-tighter">{stats.speed.toFixed(0)} <span className="text-sm font-normal text-white/30">KM/H</span></p>
            </div>
            <div className="space-y-1">
              <p className="text-white/40 text-[10px] font-black uppercase">Fatigue</p>
              <p className={`text-5xl font-black tracking-tighter ${stats.fatigue > 0.7 ? 'text-red-400' : 'text-white'}`}>
                {(stats.fatigue * 100).toFixed(0)}<span className="text-sm font-normal text-white/30">%</span>
              </p>
            </div>
          </div>
          <div className="mt-6 p-4 bg-white/5 rounded-2xl flex justify-between items-center">
             <span className="text-white/60 text-xs font-bold uppercase">System Active For</span>
             <span className="text-white font-mono text-xs">02:45:12</span>
          </div>
        </div>

        {/* Camera Selector (iOS App List Style) */}
        <div className="col-span-1 bg-white/10 backdrop-blur-3xl border border-white/20 p-6 rounded-[2.5rem] shadow-2xl flex flex-col transition-transform hover:scale-[1.02]">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-[10px] font-black text-white/40 uppercase tracking-[0.2em]">Sensor Select</h3>
            <svg className="w-5 h-5 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
            </svg>
          </div>
          <div className="flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
            {availableCameras.map(cam => (
              <button
                key={cam.deviceId}
                onClick={() => onCameraSelect(cam.deviceId)}
                className={`w-full flex items-center gap-3 p-3 rounded-2xl transition-all ${selectedCameraId === cam.deviceId ? 'bg-blue-600 text-white shadow-[0_10px_20px_rgba(37,99,235,0.4)] scale-[1.05]' : 'bg-white/5 text-white/60 hover:bg-white/10'}`}
              >
                <div className={`w-2 h-2 rounded-full ${selectedCameraId === cam.deviceId ? 'bg-white' : 'bg-white/20'}`} />
                <span className="text-xs font-bold truncate">{cam.label || 'Generic Camera'}</span>
              </button>
            ))}
            {availableCameras.length === 0 && <p className="text-white/20 text-center text-[10px] mt-10 uppercase font-black">Scanning for devices...</p>}
          </div>
        </div>
      </div>

      {/* iOS 18 Large Dynamic Start Button */}
      <div className="w-full max-w-6xl z-10 pb-6 flex justify-center">
        <button
          onClick={onStart}
          className="group relative flex items-center justify-center bg-white text-black px-16 py-8 rounded-[3rem] font-black text-3xl tracking-tighter shadow-[0_20px_60px_rgba(255,255,255,0.15)] transition-all hover:scale-105 active:scale-95"
        >
          <span className="relative z-10 flex items-center gap-5">
            INITIATE MONITORING
            <div className="bg-black text-white p-2 rounded-full">
              <svg className="w-8 h-8 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </div>
          </span>
          <div className="absolute inset-0 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 opacity-0 group-hover:opacity-10 rounded-[3rem] transition-opacity" />
        </button>
      </div>

      {/* Violation Ticker Footnote */}
      <div className="w-full max-w-6xl z-10 flex justify-center pb-2">
         <p className="text-white/20 text-[10px] font-black tracking-[0.5em] uppercase">
           GuardVision Artificial Intelligence Security Protocol Active
         </p>
      </div>
    </div>
  );
};

export default HomeDashboard;
