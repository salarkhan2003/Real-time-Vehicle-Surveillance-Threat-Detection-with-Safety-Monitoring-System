
import React, { useState, useEffect, useRef, useCallback } from 'react';
import Dashboard from './components/Dashboard';
import HomeDashboard from './components/HomeDashboard';
import { ThreatLevel, Detection, Violation, SystemStats } from './types';
import { GoogleGenAI, Type } from "@google/genai";

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

    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth || 640;
    canvas.height = videoRef.current.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    if (!ctx || canvas.width === 0) return;
    ctx.drawImage(videoRef.current, 0, 0);
    const base64Data = canvas.toDataURL('image/jpeg', 0.6).split(',')[1];

    setIsProcessing(true);
    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      // Ultra-specific instruction for Gemini Flash to maximize spatial awareness
      const prompt = `Task: Specialized Safety Detection.
      1. SENSITIVITY: Detect EVERY [person, vehicle, animal, obstacle] visible.
      2. COORDINATES: Normalized bounding boxes [x, y, w, h] from 0 to 1000.
      3. BIOMETRICS: Rate driver fatigue (0.0=awake, 1.0=asleep).
      4. PPE: Set hasHelmet=true for persons with head protection.
      5. SPATIAL: Distance in meters.
      OUTPUT JSON ONLY.`;

      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: [{ parts: [{ inlineData: { data: base64Data, mimeType: "image/jpeg" } }, { text: prompt }] }],
        config: {
          responseMimeType: "application/json",
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              detections: {
                type: Type.ARRAY,
                items: {
                  type: Type.OBJECT,
                  properties: {
                    label: { type: Type.STRING },
                    confidence: { type: Type.NUMBER },
                    x: { type: Type.NUMBER }, y: { type: Type.NUMBER }, w: { type: Type.NUMBER }, h: { type: Type.NUMBER },
                    distance: { type: Type.NUMBER },
                    hasHelmet: { type: Type.BOOLEAN, nullable: true }
                  },
                  required: ["label", "confidence", "x", "y", "w", "h", "distance"]
                }
              },
              fatigue: { type: Type.NUMBER },
              speed: { type: Type.NUMBER }
            }
          }
        }
      });

      // Cleanup response text (remove markdown if model adds it)
      const cleanJson = response.text.replace(/```json|```/gi, '').trim();
      const result = JSON.parse(cleanJson || "{}");
      setErrorStatus(null);

      const mappedDetections: Detection[] = (result.detections || [])
        .filter((d: any) => d.confidence > 0.15) // High sensitivity for low light
        .map((d: any, i: number) => ({
          id: `det-${Date.now()}-${i}`,
          label: d.label.toUpperCase(),
          confidence: d.confidence,
          bbox: { 
            x: (d.x / 1000) * canvas.width, 
            y: (d.y / 1000) * canvas.height, 
            width: (d.w / 1000) * canvas.width, 
            height: (d.h / 1000) * canvas.height 
          },
          distance: d.distance
        }));

      setDetections(mappedDetections);
      addLog(`INF: Detected ${mappedDetections.length} entities.`);

      const closestDist = mappedDetections.length > 0 
        ? Math.min(...mappedDetections.map(d => d.distance)) 
        : 10;

      const currentFatigue = result.fatigue ?? stats.fatigue;
      
      setStats(prev => ({
        ...prev,
        detectionCount: mappedDetections.length,
        fatigue: currentFatigue,
        speed: result.speed ?? prev.speed,
        helmetStatus: !mappedDetections.some(d => d.label === 'PERSON' && (d as any).hasHelmet === false)
      }));

      if (currentFatigue > 0.6 || closestDist < 1.5) {
        if (!isEmergencyAlarm) setIsEmergencyAlarm(true);
      } else {
        if (isEmergencyAlarm) setIsEmergencyAlarm(false);
      }

      mappedDetections.forEach(d => { 
        if (d.distance < 1.0) triggerViolation(`IMMINENT: ${d.label}`, ThreatLevel.CRITICAL); 
      });

    } catch (err: any) {
      if (err.message?.includes('429')) {
        setErrorStatus("QUOTA EXCEEDED - CHECK PLAN");
        addLog("SYSTEM: API Limit reached.");
      } else {
        addLog("SYSTEM: Processing Error.");
      }
      console.error(err);
    } finally { setIsProcessing(false); }
  }, [isProcessing, isMonitoring, triggerViolation, stats.fatigue, isEmergencyAlarm, addLog]);

  useEffect(() => {
    if (isMonitoring) {
      const timer = setInterval(runInference, 4000); // 4s for safety
      return () => clearInterval(timer);
    }
  }, [isMonitoring, runInference]);

  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) document.documentElement.requestFullscreen().then(() => setIsFullscreen(true));
    else document.exitFullscreen().then(() => setIsFullscreen(false));
  }, []);

  return (
    <div className="h-screen w-screen bg-black text-white overflow-hidden font-sans">
      {view === 'home' ? (
        <HomeDashboard stats={stats} violations={violations} onStart={() => startMonitoring()} availableCameras={availableCameras} selectedCameraId={selectedCameraId} onCameraSelect={setSelectedCameraId} onRefreshCameras={fetchCameras} />
      ) : (
        <Dashboard stream={stream} videoRef={videoRef} detections={detections} logs={logs} violations={violations} stats={stats} isProcessing={isProcessing} onTriggerAlert={() => { initOrResumeAudio(); triggerViolation("MANUAL OVERRIDE", ThreatLevel.CRITICAL); }} onExit={stopMonitoring} onToggleMonitoring={() => isMonitoring ? stopMonitoring() : startMonitoring()} isMonitoring={isMonitoring} availableCameras={availableCameras} selectedCameraId={selectedCameraId} onCameraSelect={(id) => { setSelectedCameraId(id); startMonitoring(id); }} onToggleFullscreen={toggleFullscreen} isFullscreen={isFullscreen} errorStatus={errorStatus} isEmergencyAlarm={isEmergencyAlarm} />
      )}
    </div>
  );
};

export default App;
