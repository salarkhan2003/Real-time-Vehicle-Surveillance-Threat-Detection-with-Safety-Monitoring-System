
import React, { useState, useEffect, useRef, useCallback } from 'react';
import Dashboard from './components/Dashboard';
import HomeDashboard from './components/HomeDashboard';
import { ThreatLevel, Detection, Violation, SystemStats } from './types';
import { GoogleGenAI, Type } from "@google/genai";
import { SpeedInsights } from '@vercel/speed-insights/react';

const App: React.FC = () => {
  const [view, setView] = useState<'home' | 'monitor'>('home');
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [availableCameras, setAvailableCameras] = useState<MediaDeviceInfo[]>([]);
  const [selectedCameraId, setSelectedCameraId] = useState<string>('');
  const [detections, setDetections] = useState<Detection[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [violations, setViolations] = useState<Violation[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [errorStatus, setErrorStatus] = useState<string | null>(null);
  const [isEmergencyAlarm, setIsEmergencyAlarm] = useState(false);
  const [isFatigueActive, setIsFatigueActive] = useState(true);
  const [isVehicleActive, setIsVehicleActive] = useState(true);
  
  // ADAS Features state
  const [enableLKA, setEnableLKA] = useState(true);  // Enable by default
  const [enableTSR, setEnableTSR] = useState(true);  // Enable by default
  const [enableIntent, setEnableIntent] = useState(true);  // Enable by default
  const [enableISP, setEnableISP] = useState(true);
  const [currentSpeed, setCurrentSpeed] = useState(60);  // Default speed for testing
  
  // ADAS data
  const [lkaData, setLkaData] = useState<any>(null);
  const [tsrData, setTsrData] = useState<any>(null);
  const [intentData, setIntentData] = useState<any[]>([]);
  const [ispData, setIspData] = useState<any>(null);
  const [blackboxSaved, setBlackboxSaved] = useState<string | null>(null);
  
  const [stats, setStats] = useState<SystemStats>({
    detectionCount: 0,
    speed: 0,
    fatigue: 0.1,
    zone: "Safety Sector Delta",
    helmetStatus: true
  });

  const lastViolationTimeRef = useRef<Record<string, number>>({});
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const alarmIntervalRef = useRef<number | null>(null);

  const initOrResumeAudio = useCallback(() => {
    if (!audioCtxRef.current) {
      const Ctx = (window as any).AudioContext || (window as any).webkitAudioContext;
      audioCtxRef.current = new Ctx();
    }
    if (audioCtxRef.current.state === 'suspended') {
      audioCtxRef.current.resume();
    }
    return audioCtxRef.current;
  }, []);

  const playTacticalBeep = useCallback((freq: number, type: OscillatorType, dur: number, vol: number) => {
    try {
      const ctx = initOrResumeAudio();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      gain.gain.setValueAtTime(0, ctx.currentTime);
      gain.gain.linearRampToValueAtTime(vol, ctx.currentTime + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + dur);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + dur);
    } catch (e) {}
  }, [initOrResumeAudio]);

  useEffect(() => {
    if (isEmergencyAlarm && isMonitoring) {
      alarmIntervalRef.current = window.setInterval(() => {
        playTacticalBeep(2200, 'square', 0.1, 0.3);
        setTimeout(() => playTacticalBeep(1800, 'square', 0.1, 0.3), 100);
      }, 250);
    } else {
      if (alarmIntervalRef.current) { clearInterval(alarmIntervalRef.current); alarmIntervalRef.current = null; }
    }
    return () => { if (alarmIntervalRef.current) clearInterval(alarmIntervalRef.current); };
  }, [isEmergencyAlarm, isMonitoring, playTacticalBeep]);

  const fetchCameras = useCallback(async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      let videoDevices = devices.filter(d => d.kind === 'videoinput');
      if (videoDevices.length > 0 && !videoDevices[0].label) {
        const tempStream = await navigator.mediaDevices.getUserMedia({ video: true });
        tempStream.getTracks().forEach(t => t.stop());
        const refreshedDevices = await navigator.mediaDevices.enumerateDevices();
        videoDevices = refreshedDevices.filter(d => d.kind === 'videoinput');
      }
      setAvailableCameras(videoDevices);
      if (videoDevices.length > 0 && !selectedCameraId) setSelectedCameraId(videoDevices[0].deviceId);
    } catch (err) {}
  }, [selectedCameraId]);

  useEffect(() => { fetchCameras(); }, [fetchCameras]);

  const addLog = useCallback((msg: string) => {
    const time = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    setLogs(prev => [`[${time}] ${msg}`, ...prev].slice(0, 50));
  }, []);

  const triggerViolation = useCallback((type: string, severity: ThreatLevel) => {
    const now = Date.now();
    const key = `${type}-${severity}`;
    if (lastViolationTimeRef.current[key] && now - lastViolationTimeRef.current[key] < 3000) return;
    lastViolationTimeRef.current[key] = now;
    setTimeout(() => {
      const newViolation: Violation = { id: Date.now(), timestamp: new Date().toLocaleTimeString(), type, severity };
      setViolations(prev => [newViolation, ...prev].slice(0, 10));
      addLog(`ALARM: ${type}`);
      if (severity === ThreatLevel.CRITICAL && !isEmergencyAlarm) playTacticalBeep(440, 'square', 0.3, 0.2);
    }, 0);
  }, [addLog, playTacticalBeep, isEmergencyAlarm]);

  const stopMonitoring = useCallback(() => {
    if (stream) stream.getTracks().forEach(track => track.stop());
    setStream(null);
    setIsMonitoring(false);
    setIsEmergencyAlarm(false);
    setDetections([]);
    setView('home'); 
    addLog("SYSTEM: Sensors standby.");
  }, [stream, addLog]);

  const startMonitoring = useCallback(async (deviceId?: string) => {
    initOrResumeAudio();
    setErrorStatus(null);
    try {
      if (stream) stream.getTracks().forEach(track => track.stop());
      const targetId = deviceId || selectedCameraId;
      const constraints = { video: targetId ? { deviceId: { exact: targetId }, width: { ideal: 1280 }, height: { ideal: 720 } } : { video: true } };
      const s = await navigator.mediaDevices.getUserMedia(constraints);
      setStream(s);
      setIsMonitoring(true);
      setView('monitor');
      addLog("SYSTEM: Neural optics active.");
      playTacticalBeep(1200, 'sine', 0.1, 0.1);
    } catch (err) { addLog("ERROR: Camera link failed."); }
  }, [selectedCameraId, stream, addLog, playTacticalBeep, initOrResumeAudio]);

  const runInference = useCallback(async () => {
    if (!videoRef.current || isProcessing || !isMonitoring) return;
    
    // Stop inference if both modes are off
    if (!isFatigueActive && !isVehicleActive) {
      setDetections([]);
      return;
    }

    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth || 640;
    canvas.height = videoRef.current.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    if (!ctx || canvas.width === 0) return;
    ctx.drawImage(videoRef.current, 0, 0);
    const base64Data = canvas.toDataURL('image/jpeg', 0.8);

    setIsProcessing(true);
    try {
      // Use YOLOv8 backend for accurate detection with mode selection + ADAS features
      const response = await fetch('http://localhost:5000/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          image: base64Data,
          modes: {
            fatigue: isFatigueActive,
            vehicle: isVehicleActive
          },
          enable_lka: enableLKA,
          enable_tsr: enableTSR,
          enable_intent: enableIntent,
          enable_isp: enableISP,
          current_speed: currentSpeed
        })
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const result = await response.json();
      setErrorStatus(null);

      // Handle fatigue data with details
      let currentFatigue = stats.fatigue;
      if (result.fatigue !== undefined) {
        currentFatigue = result.fatigue;
        
        // Log detailed fatigue info if available
        if (result.fatigueDetails) {
          const details = result.fatigueDetails;
          if (details.eyes_closed) {
            addLog("⚠️ ALERT: Eyes closed detected!");
          }
          if (details.yawning) {
            addLog("⚠️ ALERT: Yawning detected!");
          }
          if (details.head_tilted) {
            addLog("⚠️ ALERT: Head tilting detected!");
          }
        }
      }

      const mappedDetections: Detection[] = (result.detections || [])
        .filter((d: any) => {
          // ULTRA LOW threshold for maximum detection
          if (!d.label || !d.confidence) return false;
          if (d.confidence < 0.15) return false; // Ultra low for max detection
          if (d.w <= 0 || d.h <= 0) return false; // Invalid box
          if (d.x < 0 || d.y < 0 || d.x > 1000 || d.y > 1000) return false; // Out of bounds
          return true;
        })
        .map((d: any, i: number) => ({
          id: `det-${Date.now()}-${i}`,
          label: d.label.toUpperCase(),
          confidence: d.confidence,
          bbox: { 
            x: Math.max(0, (d.x / 1000) * canvas.width), 
            y: Math.max(0, (d.y / 1000) * canvas.height), 
            width: Math.min((d.w / 1000) * canvas.width, canvas.width), 
            height: Math.min((d.h / 1000) * canvas.height, canvas.height)
          },
          distance: Math.max(0.5, Math.min(d.distance, 100)) // Clamp distance
        }));

      setDetections(mappedDetections);
      
      // Handle ADAS features data
      if (result.laneKeepAssist) {
        setLkaData(result.laneKeepAssist);
        if (result.laneKeepAssist.departure_warning) {
          addLog(`⚠️ LANE DEPARTURE: ${result.laneKeepAssist.status}`);
        }
      }
      
      if (result.trafficSigns) {
        setTsrData(result.trafficSigns);
        if (result.trafficSigns.speed_warning) {
          addLog(`⚠️ ${result.trafficSigns.speed_message}`);
        }
      }
      
      if (result.pedestrianIntent) {
        setIntentData(result.pedestrianIntent);
        result.pedestrianIntent.forEach((intent: any) => {
          if (intent.warning) {
            addLog(`⚠️ PEDESTRIAN: ${intent.status} at ${intent.distance.toFixed(1)}m`);
          }
        });
      }
      
      if (result.imageProcessing) {
        setIspData(result.imageProcessing);
        if (result.imageProcessing.active) {
          // Only log once when condition changes
          if (!ispData || ispData.condition !== result.imageProcessing.condition) {
            addLog(`🌙 ISP: ${result.imageProcessing.enhancement}`);
          }
        }
      }
      
      if (result.blackboxSaved) {
        setBlackboxSaved(result.blackboxSaved);
        addLog(`📹 BLACKBOX: Event recorded - ${result.blackboxSaved}`);
      }
      
      // Only log if there are actual detections or fatigue changes
      if (mappedDetections.length > 0 || (isFatigueActive && Math.abs(currentFatigue - stats.fatigue) > 0.1)) {
        addLog(`INF: Detected ${mappedDetections.length} entities. Fatigue: ${(currentFatigue * 100).toFixed(0)}%`);
      }

      const closestDist = mappedDetections.length > 0 
        ? Math.min(...mappedDetections.map(d => d.distance)) 
        : 10;
      
      setStats(prev => ({
        ...prev,
        detectionCount: mappedDetections.length,
        fatigue: currentFatigue,
        speed: result.speed ?? prev.speed,
        helmetStatus: !mappedDetections.some(d => d.label === 'PERSON' && (d as any).hasHelmet === false)
      }));

      // Emergency alarm logic - AGGRESSIVE THRESHOLDS for safety
      let shouldTriggerAlarm = false;
      
      // Check fatigue only if fatigue mode is active - VERY AGGRESSIVE
      if (isFatigueActive && currentFatigue > 0.5) {  // Trigger at 50% (was 60%)
        shouldTriggerAlarm = true;
      }
      
      // Check collision only if vehicle mode is active - VERY AGGRESSIVE
      if (isVehicleActive && closestDist < 2.5) {  // Trigger at 2.5m (was 1.5m)
        shouldTriggerAlarm = true;
      }
      
      // Update alarm state
      if (shouldTriggerAlarm && !isEmergencyAlarm) {
        setIsEmergencyAlarm(true);
      } else if (!shouldTriggerAlarm && isEmergencyAlarm) {
        setIsEmergencyAlarm(false);
      }

      // Trigger violations only if vehicle mode is active - MORE AGGRESSIVE
      if (isVehicleActive) {
        mappedDetections.forEach(d => { 
          if (d.distance < 2.0) {  // Trigger at 2m (was 1m)
            triggerViolation(`IMMINENT: ${d.label}`, ThreatLevel.CRITICAL);
          } else if (d.distance < 3.5) {  // Warning at 3.5m
            triggerViolation(`WARNING: ${d.label} APPROACHING`, ThreatLevel.HIGH);
          }
        });
      }
      
      // Trigger violations for high fatigue
      if (isFatigueActive && currentFatigue > 0.6) {
        triggerViolation(`FATIGUE: ${(currentFatigue * 100).toFixed(0)}%`, ThreatLevel.HIGH);
      } else if (isFatigueActive && currentFatigue > 0.8) {
        triggerViolation(`CRITICAL FATIGUE: ${(currentFatigue * 100).toFixed(0)}%`, ThreatLevel.CRITICAL);
      }

    } catch (err: any) {
      if (err.message?.includes('Failed to fetch')) {
        setErrorStatus("YOLO BACKEND OFFLINE");
        addLog("ERROR: Detection server not running. Start backend/server.py");
      } else {
        setErrorStatus("DETECTION ERROR");
        addLog("SYSTEM: Processing Error.");
      }
      console.error(err);
    } finally { setIsProcessing(false); }
  }, [isProcessing, isMonitoring, triggerViolation, stats.fatigue, isEmergencyAlarm, addLog, isFatigueActive, isVehicleActive]);

  useEffect(() => {
    if (isMonitoring && (isFatigueActive || isVehicleActive)) {
      const timer = setInterval(runInference, 500); // 500ms for fast real-time detection
      return () => clearInterval(timer);
    } else if (isMonitoring && !isFatigueActive && !isVehicleActive) {
      // Clear detections when both modes are off
      setDetections([]);
    }
  }, [isMonitoring, runInference, isFatigueActive, isVehicleActive]);

  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) document.documentElement.requestFullscreen().then(() => setIsFullscreen(true));
    else document.exitFullscreen().then(() => setIsFullscreen(false));
  }, []);

  return (
    <div className="h-screen w-screen bg-black text-white overflow-hidden font-sans">
      {view === 'home' ? (
        <HomeDashboard stats={stats} violations={violations} onStart={() => startMonitoring()} availableCameras={availableCameras} selectedCameraId={selectedCameraId} onCameraSelect={setSelectedCameraId} onRefreshCameras={fetchCameras} />
      ) : (
        <Dashboard 
          stream={stream} 
          videoRef={videoRef} 
          detections={detections} 
          logs={logs} 
          violations={violations} 
          stats={stats} 
          isProcessing={isProcessing} 
          onTriggerAlert={() => { initOrResumeAudio(); triggerViolation("MANUAL OVERRIDE", ThreatLevel.CRITICAL); }} 
          onExit={stopMonitoring} 
          onToggleMonitoring={() => isMonitoring ? stopMonitoring() : startMonitoring()} 
          isMonitoring={isMonitoring} 
          availableCameras={availableCameras} 
          selectedCameraId={selectedCameraId} 
          onCameraSelect={(id) => { setSelectedCameraId(id); startMonitoring(id); }} 
          onToggleFullscreen={toggleFullscreen} 
          isFullscreen={isFullscreen} 
          errorStatus={errorStatus} 
          isEmergencyAlarm={isEmergencyAlarm}
          isFatigueActive={isFatigueActive}
          isVehicleActive={isVehicleActive}
          onToggleFatigue={() => setIsFatigueActive(!isFatigueActive)}
          onToggleVehicle={() => setIsVehicleActive(!isVehicleActive)}
          enableLKA={enableLKA}
          enableTSR={enableTSR}
          enableIntent={enableIntent}
          enableISP={enableISP}
          onToggleLKA={() => setEnableLKA(!enableLKA)}
          onToggleTSR={() => setEnableTSR(!enableTSR)}
          onToggleIntent={() => setEnableIntent(!enableIntent)}
          onToggleISP={() => setEnableISP(!enableISP)}
          lkaData={lkaData}
          tsrData={tsrData}
          intentData={intentData}
          ispData={ispData}
        />
      )}
      <SpeedInsights />
    </div>
  );
};

export default App;
