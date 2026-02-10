
import React from 'react';
import CameraFeed from './CameraFeed';
import StatCard from './StatCard';
import LogPanel from './LogPanel';
import ViolationTable from './ViolationTable';
import { ThreatLevel, Detection, Violation, SystemStats } from '../types';

interface DashboardProps {
  stream: MediaStream | null;
  videoRef: React.RefObject<HTMLVideoElement | null>;
  detections: Detection[];
  logs: string[];
  violations: Violation[];
  stats: SystemStats;
  isProcessing: boolean;
  onTriggerAlert: () => void;
  onExit: () => void;
  onToggleMonitoring: () => void;
  isMonitoring: boolean;
  availableCameras: MediaDeviceInfo[];
  selectedCameraId: string;
  onCameraSelect: (id: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ 
  stream, 
  videoRef,
  detections, 
  logs, 
  violations, 
  stats,
  isProcessing,
  onTriggerAlert,
  onExit,
  onToggleMonitoring,
  isMonitoring,
  availableCameras,
  selectedCameraId,
  onCameraSelect
}) => {
  const closestDistance = detections.length > 0 ? Math.min(...detections.map(d => d.distance)) : 10;
  const globalThreat = closestDistance < 1.2 ? ThreatLevel.CRITICAL : 
                       closestDistance < 2.5 ? ThreatLevel.HIGH : ThreatLevel.LOW;

  const threatColor = globalThreat === ThreatLevel.CRITICAL ? 'bg-red-500 shadow-[0_0_15px_rgba(239,68,68,0.5)]' :
                      globalThreat === ThreatLevel.HIGH ? 'bg-orange-500 shadow-[0_0_15px_rgba(249,115,22,0.5)]' : 'bg-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.5)]';

  return (
    <div className="h-screen w-screen bg-[#050505] flex flex-col p-5 space-y-5 select-none">
      
      {/* HUD Header Controls */}
      <div className="flex justify-between items-center bg-white/5 backdrop-blur-xl p-4 rounded-3xl border border-white/10">
        <div className="flex items-center space-x-5">
          <button 
            onClick={onExit}
            className="group flex items-center gap-2 bg-white/5 hover:bg-white/10 px-5 py-3 rounded-2xl transition-all border border-white/5"
          >
            <svg className="w-5 h-5 text-white group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M15 19l-7-7 7-7" />
            </svg>
            <span className="text-xs font-black uppercase tracking-widest">Dashboard</span>
          </button>
          <div className="h-8 w-px bg-white/10 mx-2" />
          <div>
            <h1 className="text-sm font-black tracking-[0.3em] text-white">VISION_HUD_LINK</h1>
            <p className="text-[9px] text-white/30 uppercase font-black tracking-tighter">System ID: GV-990-DELTA</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <select 
            value={selectedCameraId}
            onChange={(e) => onCameraSelect(e.target.value)}
            className="bg-white/5 border border-white/10 text-[10px] font-bold uppercase rounded-xl px-4 py-2 text-white/60 focus:ring-1 ring-blue-500 outline-none"
          >
            {availableCameras.map(cam => (
              <option key={cam.deviceId} value={cam.deviceId} className="bg-slate-900">{cam.label || 'Default Link'}</option>
            ))}
          </select>

          <button 
            onClick={onToggleMonitoring}
            className={`px-6 py-2 rounded-2xl font-black text-[10px] tracking-widest uppercase transition-all ${isMonitoring ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-blue-600 text-white shadow-lg shadow-blue-500/20'}`}
          >
            {isMonitoring ? 'STOP SENSORS' : 'INIT SENSORS'}
          </button>
          
          <button 
            onClick={onTriggerAlert}
            className="bg-white text-black font-black py-2 px-6 rounded-2xl text-[10px] tracking-widest hover:scale-105 active:scale-95 transition-transform"
          >
            PANIC_OVERRIDE
          </button>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-12 gap-5 min-h-0">
        
        {/* Main Feed with Overlay */}
        <div className="col-span-12 lg:col-span-9 flex flex-col space-y-4">
          <div className="relative flex-1 bg-black rounded-[3rem] overflow-hidden border border-white/5 shadow-2xl ring-1 ring-white/10">
            <CameraFeed stream={stream} videoRef={videoRef} detections={detections} />
            
            {/* Status Overlays */}
            <div className="absolute top-10 right-10 flex flex-col items-end space-y-2 pointer-events-none">
                <div className="flex items-center space-x-3 bg-black/40 backdrop-blur-md px-4 py-2 rounded-full border border-white/10">
                   <div className={`w-2 h-2 rounded-full ${isProcessing ? 'bg-cyan-400 animate-pulse' : 'bg-emerald-500'}`} />
                   <span className="text-[10px] font-black text-white uppercase tracking-widest">Neural Link {isProcessing ? 'Active' : 'Idle'}</span>
                </div>
                {isProcessing && <div className="text-[8px] font-bold text-cyan-400/80 animate-pulse uppercase tracking-[0.2em] px-4">Analyzing Spatial Geometry...</div>}
            </div>

            {/* Immersive HUD Bottom Bar */}
            <div className="absolute bottom-0 left-0 right-0 p-10 bg-gradient-to-t from-black/95 via-black/40 to-transparent flex justify-between items-end pointer-events-none">
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                   <div className="w-1 h-1 bg-white/20 rounded-full" />
                   <p className="text-[10px] text-white/40 font-black uppercase tracking-[0.4em]">Spatial Awareness Console</p>
                </div>
                <div className="flex items-end space-x-8">
                  <div className="flex flex-col">
                     <span className={`text-8xl font-black tracking-tighter leading-none ${globalThreat === ThreatLevel.CRITICAL ? 'text-red-500' : 'text-white'}`}>
                        {closestDistance === 10 ? '--' : closestDistance.toFixed(1)}
                        <span className="text-2xl ml-2 text-white/20 uppercase font-black">Meters</span>
                     </span>
                  </div>
                  <div className="w-80 h-3 bg-white/10 rounded-full overflow-hidden border border-white/5 mb-3">
                    <div 
                      className={`h-full transition-all duration-700 ease-out ${threatColor}`}
                      style={{ width: `${Math.min(100, (2.5 / (closestDistance || 0.1)) * 100)}%` }}
                    />
                  </div>
                </div>
              </div>
              <div className="text-right space-y-2">
                <p className="text-[10px] text-white/30 font-black uppercase tracking-[0.4em]">Tactical Zone</p>
                <div className="flex items-center gap-3 justify-end">
                   <p className="text-4xl font-black text-blue-500 italic tracking-tighter uppercase">{stats.zone}</p>
                   <div className="w-2 h-10 bg-blue-500/30 rounded-full" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Sidebar Widgets */}
        <div className="col-span-12 lg:col-span-3 flex flex-col space-y-5 min-h-0">
          <div className="grid grid-cols-2 gap-4">
            <StatCard title="Velocity" value={`${stats.speed.toFixed(0)} KMH`} color="text-blue-500" />
            <StatCard title="Targets" value={stats.detectionCount.toString()} color="text-emerald-500" />
            <StatCard 
              title="Fatigue" 
              value={`${(stats.fatigue * 100).toFixed(0)}%`} 
              color={stats.fatigue > 0.8 ? 'text-red-500' : 'text-yellow-400'} 
            />
            <StatCard 
              title="PPE Check" 
              value={stats.helmetStatus ? "PASS" : "FAIL"} 
              color={stats.helmetStatus ? 'text-emerald-500' : 'text-red-500'} 
            />
          </div>

          <div className="flex-1 bg-white/5 backdrop-blur-md rounded-[2.5rem] border border-white/10 p-6 flex flex-col min-h-0 shadow-2xl">
            <div className="flex justify-between items-center mb-5">
               <h2 className="text-[10px] font-black text-white/30 uppercase tracking-[0.3em]">Violation_DB</h2>
               <div className="text-[8px] bg-red-500/10 text-red-500 px-2 py-0.5 rounded-full font-black border border-red-500/20">LIVE_RECORD</div>
            </div>
            <ViolationTable violations={violations} />
          </div>

          <div className="h-56 bg-black/40 backdrop-blur-md rounded-[2.5rem] border border-white/10 p-6 flex flex-col min-h-0">
            <h2 className="text-[10px] font-black text-white/30 uppercase tracking-[0.3em] mb-3">System_Telemetry</h2>
            <LogPanel logs={logs} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
