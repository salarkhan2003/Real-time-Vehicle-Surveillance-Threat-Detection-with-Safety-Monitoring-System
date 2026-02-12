
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
  onToggleFullscreen: () => void;
  isFullscreen: boolean;
  errorStatus: string | null;
  isEmergencyAlarm: boolean;
}

const Dashboard: React.FC<DashboardProps> = ({ 
  stream, videoRef, detections, logs, violations, stats, isProcessing, onTriggerAlert, onExit, onToggleMonitoring, isMonitoring, availableCameras, selectedCameraId, onCameraSelect, onToggleFullscreen, isFullscreen, errorStatus, isEmergencyAlarm
}) => {
  const closestDistance = detections.length > 0 ? Math.min(...detections.map(d => d.distance)) : 10;
  const globalThreat = isEmergencyAlarm ? ThreatLevel.CRITICAL : closestDistance < 2.5 ? ThreatLevel.HIGH : ThreatLevel.LOW;
  const threatColor = globalThreat === ThreatLevel.CRITICAL ? 'bg-red-500 shadow-[0_0_20px_#ef4444]' : globalThreat === ThreatLevel.HIGH ? 'bg-orange-500' : 'bg-emerald-500';

  return (
    <div className={`h-screen w-screen bg-[#050505] flex flex-col p-4 space-y-4 select-none animate-fade-in relative transition-colors duration-200 ${isEmergencyAlarm ? 'bg-red-950/20' : ''}`}>
      {isEmergencyAlarm && (
        <div className="absolute inset-0 pointer-events-none z-[100] border-[20px] border-red-600/50 animate-pulse flex items-center justify-center">
          <div className="bg-red-600 text-white px-12 py-6 rounded-3xl shadow-[0_0_100px_rgba(239,68,68,0.8)] border-4 border-white animate-bounce">
            <h2 className="text-7xl font-black italic tracking-tighter">COLLISION WARNING</h2>
            <p className="text-center font-black text-xl uppercase tracking-widest mt-2">FATIGUE DETECTED • OBJECT IN BLIND SPOT</p>
          </div>
        </div>
      )}

      {errorStatus && (
        <div className="absolute top-0 left-0 w-full z-[110] bg-red-600 text-white p-3 text-center text-[10px] font-black tracking-[0.2em] animate-pulse">
          SYSTEM_ALERT: {errorStatus}
        </div>
      )}

      <div className="flex justify-between items-center bg-white/5 backdrop-blur-2xl p-4 rounded-3xl border border-white/10 shadow-xl z-10">
        <div className="flex items-center space-x-4">
          <button onClick={onExit} className="p-3 bg-white/5 hover:bg-white/10 rounded-2xl transition-all border border-white/5 active:scale-90">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
          </button>
          <div className="h-8 w-px bg-white/10" />
          <div>
            <h1 className="text-xs font-black tracking-[0.4em] text-white uppercase">GuardVision_Elite_V5</h1>
            <p className="text-[9px] text-white/40 uppercase font-black">Optics: {isMonitoring ? 'Streaming' : 'Standby'}</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button onClick={onToggleFullscreen} className="p-3 bg-white/5 hover:bg-white/10 rounded-2xl transition-all border border-white/5 text-white/60 active:scale-90">{isFullscreen ? 'EXIT_FULL' : 'ENTER_FULL'}</button>
          <select value={selectedCameraId} onChange={(e) => onCameraSelect(e.target.value)} className="bg-white/5 border border-white/10 text-[10px] font-bold uppercase rounded-xl px-4 py-2.5 text-white/80 outline-none">
            {availableCameras.map(cam => (<option key={cam.deviceId} value={cam.deviceId} className="bg-slate-900">{cam.label || 'Optic 01'}</option>))}
          </select>
          <button onClick={onToggleMonitoring} className={`px-5 py-2.5 rounded-2xl font-black text-[10px] tracking-widest uppercase transition-all active:scale-95 ${isMonitoring ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-blue-600 text-white'}`}>{isMonitoring ? 'HALT' : 'ENGAGE'}</button>
          <button onClick={onTriggerAlert} className="bg-white text-black font-black py-2.5 px-6 rounded-2xl text-[10px] tracking-widest hover:bg-red-500 hover:text-white transition-colors active:scale-95">PANIC_OVERRIDE</button>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-12 gap-4 min-h-0">
        <div className="col-span-12 lg:col-span-9 flex flex-col min-h-0">
          <div className="relative flex-1 bg-black rounded-[2.5rem] overflow-hidden border border-white/10 shadow-2xl">
            <CameraFeed stream={stream} videoRef={videoRef} detections={detections} isProcessing={isProcessing} />
            <div className="absolute bottom-0 left-0 right-0 p-10 bg-gradient-to-t from-black via-black/40 to-transparent flex justify-between items-end pointer-events-none">
              <div className="space-y-2">
                <p className="text-[10px] text-white/30 font-black uppercase tracking-[0.4em]">Proximity Matrix</p>
                <div className="flex items-end space-x-6">
                  <span className={`text-9xl font-black tracking-tighter leading-none ${globalThreat === ThreatLevel.CRITICAL ? 'text-red-500' : 'text-white'}`}>
                    {closestDistance >= 10 ? 'SAFE' : closestDistance.toFixed(1)}
                    {closestDistance < 10 && <span className="text-xl ml-2 text-white/20 uppercase font-black">m</span>}
                  </span>
                  <div className="w-64 h-2.5 bg-white/10 rounded-full overflow-hidden mb-5">
                    <div 
                      className={`h-full transition-all duration-300 ${threatColor}`} 
                      style={{ width: `${Math.min(100, (3.5 / (closestDistance || 0.1)) * 100)}%` }} 
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-span-12 lg:col-span-3 flex flex-col space-y-4 min-h-0">
          <div className="grid grid-cols-2 gap-3">
            <StatCard title="Velocity" value={`${stats.speed} kmh`} color="text-blue-400" />
            <StatCard title="Entities" value={stats.detectionCount.toString()} color="text-emerald-400" />
            <StatCard title="Fatigue" value={`${(stats.fatigue * 100).toFixed(0)}%`} color={stats.fatigue > 0.6 ? 'text-red-500' : 'text-white'} />
            <StatCard title="Status" value={isEmergencyAlarm ? "DANGER" : "READY"} color={isEmergencyAlarm ? 'text-red-500' : 'text-emerald-500'} />
          </div>
          <div className="flex-1 bg-white/5 rounded-[2rem] border border-white/10 p-5 flex flex-col min-h-0"><h2 className="text-[9px] font-black text-white/30 uppercase tracking-[0.3em] mb-4">VIOLATION_DB</h2><ViolationTable violations={violations} /></div>
          <div className="h-44 bg-black/40 rounded-[2rem] border border-white/10 p-5 flex flex-col min-h-0"><h2 className="text-[9px] font-black text-white/30 uppercase tracking-[0.3em] mb-3">SYSTEM_LOGS</h2><LogPanel logs={logs} /></div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
