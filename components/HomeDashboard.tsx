
import React from 'react';
import { SystemStats, Violation, ThreatLevel } from '../types';

interface HomeDashboardProps {
  stats: SystemStats;
  violations: Violation[];
  onStart: () => void;
  availableCameras: MediaDeviceInfo[];
  selectedCameraId: string;
  onCameraSelect: (id: string) => void;
  onRefreshCameras: () => void;
}

const HomeDashboard: React.FC<HomeDashboardProps> = ({ 
  stats, 
  onStart, 
  availableCameras, 
  selectedCameraId, 
  onCameraSelect,
  onRefreshCameras
}) => {
  const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const currentDate = new Date().toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' });

  // Working features only
  const features = [
    'YOLOv8x Object Detection',
    'Fatigue Monitoring',
    'Lane Keep Assist',
    'Traffic Sign Recognition',
    'Pedestrian Intent Prediction',
    'Adaptive ISP Enhancement',
    'Blackbox Recording',
    'Collision Warning System'
  ];

  return (
    <div className="relative h-full w-full bg-black overflow-hidden flex flex-col items-center justify-between p-10">
      <div className="absolute top-0 left-0 w-full h-full z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[10%] left-[20%] w-[60%] h-[60%] bg-blue-600/30 blur-[150px] rounded-full animate-pulse" />
        <div className="absolute bottom-[20%] right-[10%] w-[50%] h-[50%] bg-purple-600/20 blur-[150px] rounded-full" />
      </div>

      <div className="w-full max-w-6xl flex flex-col items-center space-y-1 z-10 animate-fade-in">
        <p className="text-xl font-semibold text-white/80 tracking-wide uppercase">{currentDate}</p>
        <h1 className="text-[10rem] font-bold tracking-tighter text-white leading-none drop-shadow-[0_0_20px_rgba(255,255,255,0.2)]">
          {currentTime}
        </h1>
      </div>

      <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-4 lg:grid-cols-4 gap-6 z-10">
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
        </div>

        <div className={`col-span-1 bg-white/10 backdrop-blur-3xl border p-6 rounded-[2.5rem] shadow-2xl flex flex-col transition-transform hover:scale-[1.02] ${availableCameras.length === 0 ? 'border-red-500/50' : 'border-white/20'}`}>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-[10px] font-black text-white/40 uppercase tracking-[0.2em]">Sensor Select</h3>
            <button onClick={onRefreshCameras} className="p-1.5 hover:bg-white/10 rounded-lg transition-colors text-white/40">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
            {availableCameras.length > 0 ? (
              availableCameras.map(cam => (
                <button
                  key={cam.deviceId}
                  onClick={() => onCameraSelect(cam.deviceId)}
                  className={`w-full flex items-center gap-3 p-3 rounded-2xl transition-all ${selectedCameraId === cam.deviceId ? 'bg-blue-600 text-white shadow-[0_10px_20px_rgba(37,99,235,0.4)]' : 'bg-white/5 text-white/60 hover:bg-white/10'}`}
                >
                  <div className={`w-2 h-2 rounded-full ${selectedCameraId === cam.deviceId ? 'bg-white' : 'bg-white/20'}`} />
                  <span className="text-xs font-bold truncate">{cam.label || 'Optical Sensor'}</span>
                </button>
              ))
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center p-4">
                <p className="text-red-400 text-[10px] font-black uppercase mb-2">No Sensors Detected</p>
                <button 
                  onClick={onRefreshCameras}
                  className="text-[9px] bg-white/5 border border-white/10 px-3 py-1.5 rounded-lg hover:bg-white/10 transition-colors uppercase font-bold text-white/60"
                >
                  Request Access
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="w-full max-w-6xl z-10 pb-6 flex flex-col items-center gap-6">
        {/* Features Checklist - Compact */}
        <div className="w-full bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs font-black text-white/60 uppercase tracking-[0.3em]">System Features</h3>
            <span className="text-[10px] text-emerald-400 font-bold">{features.length} Active</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-x-6 gap-y-2">
            {features.map((feature, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <svg className="w-3 h-3 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-[11px] text-white/80 font-medium">{feature}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Monitoring Button */}
        <button
          onClick={onStart}
          disabled={availableCameras.length === 0}
          className={`group relative flex items-center justify-center px-16 py-8 rounded-[3rem] font-black text-3xl tracking-tighter shadow-[0_20px_60px_rgba(255,255,255,0.15)] transition-all hover:scale-105 active:scale-95 ${availableCameras.length === 0 ? 'bg-white/10 text-white/20 cursor-not-allowed' : 'bg-white text-black'}`}
        >
          <span className="relative z-10 flex items-center gap-5">
            INITIATE MONITORING
            <div className={`p-2 rounded-full ${availableCameras.length === 0 ? 'bg-white/5' : 'bg-black text-white'}`}>
              <svg className="w-8 h-8 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </div>
          </span>
        </button>
      </div>

      <div className="w-full max-w-6xl z-10 flex justify-center pb-2">
         <p className="text-white/20 text-[10px] font-black tracking-[0.5em] uppercase">
           GuardVision Artificial Intelligence Security Protocol Active
         </p>
      </div>
    </div>
  );
};

export default HomeDashboard;
