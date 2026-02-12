
import React, { useEffect } from 'react';
import { Detection } from '../types';

interface CameraFeedProps {
  stream: MediaStream | null;
  videoRef: React.RefObject<HTMLVideoElement | null>;
  detections: Detection[];
  isProcessing?: boolean;
}

const CameraFeed: React.FC<CameraFeedProps> = ({ stream, videoRef, detections, isProcessing }) => {
  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream, videoRef]);

  const getLabelColor = (label: string, distance: number) => {
    if (distance < 1.2) return '#ef4444'; 
    switch (label) {
      case 'PERSON': return '#10b981';
      case 'VEHICLE': return '#3b82f6';
      case 'ANIMAL': return '#f59e0b';
      case 'OBSTACLE': return '#a855f7';
      default: return '#ffffff';
    }
  };

  return (
    <div className="relative w-full h-full bg-[#050505]">
      {stream ? (
        <>
          <video
            ref={videoRef}
            autoPlay
            muted
            playsInline
            className="w-full h-full object-cover opacity-70 transition-opacity duration-1000"
          />
          <div className="scanline"></div>
          
          {isProcessing && (
            <div className="absolute top-4 right-4 flex items-center gap-2 bg-blue-600/20 border border-blue-500/50 px-3 py-1 rounded-full z-30 animate-pulse">
               <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping" />
               <span className="text-[9px] font-black tracking-widest text-blue-400 uppercase">Neural Analysis Active</span>
            </div>
          )}
          
          <svg 
            className="absolute inset-0 w-full h-full pointer-events-none z-10" 
            viewBox={`0 0 ${videoRef.current?.videoWidth || 1280} ${videoRef.current?.videoHeight || 720}`}
            preserveAspectRatio="xMidYMid slice"
          >
            {/* Center HUD */}
            <circle cx="50%" cy="50%" r="50" stroke="white" strokeWidth="0.5" strokeOpacity="0.1" fill="none" />
            <line x1="50%" y1="45%" x2="50%" y2="48%" stroke="white" strokeOpacity="0.2" strokeWidth="1" />
            <line x1="50%" y1="52%" x2="50%" y2="55%" stroke="white" strokeOpacity="0.2" strokeWidth="1" />

            {detections.map((det) => {
              const isCritical = det.distance < 1.2;
              const boxColor = getLabelColor(det.label, det.distance);
              
              return (
                <g key={det.id} className="transition-all duration-300">
                  <path d={`M ${det.bbox.x} ${det.bbox.y + 20} L ${det.bbox.x} ${det.bbox.y} L ${det.bbox.x + 20} ${det.bbox.y}`} fill="none" stroke={boxColor} strokeWidth="3" />
                  <path d={`M ${det.bbox.x + det.bbox.width - 20} ${det.bbox.y} L ${det.bbox.x + det.bbox.width} ${det.bbox.y} L ${det.bbox.x + det.bbox.width} ${det.bbox.y + 20}`} fill="none" stroke={boxColor} strokeWidth="3" />
                  <path d={`M ${det.bbox.x} ${det.bbox.y + det.bbox.height - 20} L ${det.bbox.x} ${det.bbox.y + det.bbox.height} L ${det.bbox.x + 20} ${det.bbox.y + det.bbox.height}`} fill="none" stroke={boxColor} strokeWidth="3" />
                  <path d={`M ${det.bbox.x + det.bbox.width - 20} ${det.bbox.y + det.bbox.height} L ${det.bbox.x + det.bbox.width} ${det.bbox.y + det.bbox.height} L ${det.bbox.x + det.bbox.width} ${det.bbox.y + det.bbox.height - 20}`} fill="none" stroke={boxColor} strokeWidth="3" />

                  <rect x={det.bbox.x} y={det.bbox.y} width={det.bbox.width} height={det.bbox.height} fill={isCritical ? 'rgba(239, 68, 68, 0.05)' : 'none'} stroke={boxColor} strokeWidth="0.5" strokeOpacity="0.3" />
                  
                  <g transform={`translate(${det.bbox.x}, ${det.bbox.y - 35})`}>
                    <rect width="160" height="28" fill="black" fillOpacity="0.85" rx="4" />
                    <line x1="0" y1="28" x2="0" y2="0" stroke={boxColor} strokeWidth="4" />
                    <text x="8" y="19" fill="white" fontSize="13" fontWeight="900" className="font-mono tracking-tighter">
                      {det.label} <tspan fill={boxColor} fillOpacity="0.6">»</tspan> {det.distance.toFixed(1)}m
                    </text>
                  </g>
                </g>
              );
            })}
          </svg>
        </>
      ) : (
        <div className="w-full h-full flex flex-col items-center justify-center space-y-6">
           <div className="relative w-20 h-20">
              <div className="absolute inset-0 border-4 border-white/5 rounded-full" />
              <div className="absolute inset-0 border-4 border-t-blue-500 rounded-full animate-spin" />
           </div>
           <div className="text-center space-y-2">
              <p className="text-white/40 font-black tracking-[0.5em] text-[10px] uppercase">Awaiting Optics Sync</p>
              <p className="text-white/10 font-mono text-[8px] uppercase tracking-widest">Protocol Version 5.0.0 (PRO)</p>
           </div>
        </div>
      )}

      <div className="absolute top-10 left-10 text-[9px] text-white/40 font-black tracking-[0.3em] z-20 space-y-3 pointer-events-none select-none">
        <div className="flex flex-col space-y-1">
           <p className="flex items-center gap-2 text-white/60">
             <span className={`w-1.5 h-1.5 rounded-full ${stream ? 'bg-emerald-500 shadow-[0_0_5px_#10b981]' : 'bg-red-500'}`}></span>
             STREAMING: {stream ? 'ENCRYPTED_PRO_LINK' : 'OFFLINE'}
           </p>
           <p>ENGINE: GEMINI_3_PRO_REASONING</p>
        </div>
        <div className="h-px w-20 bg-white/10" />
        <div className="space-y-1">
           <p>THINK_BUDGET: 4096 TOKENS</p>
           <p>SENSITIVITY: ENHANCED_LOW_LIGHT</p>
        </div>
      </div>
    </div>
  );
};

export default CameraFeed;
