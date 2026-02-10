
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
  const [stats, setStats] = useState<SystemStats>({
    detectionCount: 0,
    speed: 0,
    fatigue: 0.1,
    zone: "Industrial Zone A",
    helmetStatus: true
  });

  const lastViolationTimeRef = useRef<Record<string, number>>({});
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const addLog = useCallback((msg: string) => {
    const time = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    setLogs(prev => [`[${time}] ${msg}`, ...prev].slice(0, 50));
  }, []);

  const triggerViolation = useCallback((type: string, severity: ThreatLevel) => {
    const now = Date.now();
    const key = `${type}-${severity}`;
    if (lastViolationTimeRef.current[key] && now - lastViolationTimeRef.current[key] < 10000) return;
    
    lastViolationTimeRef.current[key] = now;
    const newViolation: Violation = {
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
      type,
      severity
    };
    setViolations(prev => [newViolation, ...prev].slice(0, 10));
    addLog(`VIOLATION: ${type} (${severity})`);
    
    const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.type = severity === ThreatLevel.CRITICAL ? 'sawtooth' : 'sine';
    osc.frequency.setValueAtTime(severity === ThreatLevel.CRITICAL ? 440 : 880, audioCtx.currentTime);
    gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 1);
    osc.start();
    osc.stop(audioCtx.currentTime + 1);
  }, [addLog]);

  const fetchCameras = async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const cameras = devices.filter(device => device.kind === 'videoinput');
      setAvailableCameras(cameras);
      if (cameras.length > 0 && !selectedCameraId) {
        setSelectedCameraId(cameras[0].deviceId);
      }
    } catch (err) {
      console.error("Error fetching cameras:", err);
    }
  };

  const stopMonitoring = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setIsMonitoring(false);
    setDetections([]);
    addLog("SYSTEM: Vision sensors deactivated.");
  }, [stream, addLog]);

  const startMonitoring = useCallback(async (deviceId?: string) => {
    try {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      const targetId = deviceId || selectedCameraId;
      const constraints = {
        video: targetId ? { deviceId: { exact: targetId }, width: { ideal: 1280 }, height: { ideal: 720 } } : { width: { ideal: 1280 }, height: { ideal: 720 } }
      };
      const s = await navigator.mediaDevices.getUserMedia(constraints);
      setStream(s);
      setIsMonitoring(true);
      setView('monitor');
      addLog("SYSTEM: High-precision neural link established.");
    } catch (err) {
      addLog("ERROR: Camera hardware fault. Check permissions.");
      console.error(err);
    }
  }, [selectedCameraId, stream, addLog]);

  const runInference = useCallback(async () => {
    if (!videoRef.current || isProcessing || !isMonitoring) return;

    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx || canvas.width === 0) return;

    ctx.drawImage(videoRef.current, 0, 0);
    const base64Data = canvas.toDataURL('image/jpeg', 0.6).split(',')[1];

    setIsProcessing(true);
    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      const prompt = `Act as an advanced autonomous safety system. 
      Analyze the frame for: 
      1. PERSON: Must check for 'safety_helmet'. Be extremely strict. If no helmet is visible on a person, mark 'hasHelmet': false.
      2. VEHICLE: Identify trucks, forklifts, cars.
      3. ANIMAL: Detect potential wildlife/stray interference.
      4. OBSTACLE: Identify boxes, debris, or tools on the floor.
      Only report objects you are >75% confident about. If nothing is found, return empty detections.
      Estimate distance in meters.
      Analyze the primary human face for fatigue (0 to 1).
      Return ONLY valid JSON.`;

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
                    label: { type: Type.STRING, description: "PERSON, VEHICLE, ANIMAL, or OBSTACLE" },
                    confidence: { type: Type.NUMBER },
                    x: { type: Type.NUMBER, description: "Normalized 0-1000" },
                    y: { type: Type.NUMBER, description: "Normalized 0-1000" },
                    w: { type: Type.NUMBER },
                    h: { type: Type.NUMBER },
                    distance: { type: Type.NUMBER },
                    hasHelmet: { type: Type.BOOLEAN, description: "True if helmet detected, false if missing, null if not a person" }
                  },
                  required: ["label", "confidence", "x", "y", "w", "h", "distance"]
                }
              },
              fatigue_score: { type: Type.NUMBER },
              speed_estimate: { type: Type.NUMBER }
            }
          }
        }
      });

      const result = JSON.parse(response.text || "{}");
      const mappedDetections: Detection[] = (result.detections || [])
        .filter((d: any) => d.confidence > 0.75) // Higher threshold for accuracy
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
      
      const persons = (result.detections || []).filter((d: any) => d.label.toUpperCase() === 'PERSON');
      const helmetViolation = persons.some((p: any) => p.hasHelmet === false);

      setStats(prev => ({
        ...prev,
        detectionCount: prev.detectionCount + (mappedDetections.length > 0 ? 1 : 0),
        fatigue: result.fatigue_score ?? prev.fatigue,
        speed: result.speed_estimate ?? prev.speed,
        helmetStatus: !helmetViolation
      }));

      mappedDetections.forEach(d => {
        if (d.distance < 1.0) triggerViolation(`CRITICAL: ${d.label} PROXIMITY`, ThreatLevel.CRITICAL);
        else if (d.distance < 2.5 && d.label === 'PERSON') triggerViolation("CAUTION: Person in work zone", ThreatLevel.HIGH);
      });
      
      if (helmetViolation) triggerViolation("SAFETY: PPE Missing (No Helmet)", ThreatLevel.HIGH);
      if (result.fatigue_score > 0.8) triggerViolation("DANGER: Operator Fatigue Detected", ThreatLevel.CRITICAL);
      
    } catch (err) {
      console.error("AI Analysis Error:", err);
    } finally {
      setIsProcessing(false);
    }
  }, [isProcessing, isMonitoring, triggerViolation]);

  useEffect(() => {
    fetchCameras();
    const interval = setInterval(fetchCameras, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (isMonitoring) {
      const timer = setInterval(runInference, 1500); // Fast enough for real-time but mindful of rate limits
      return () => clearInterval(timer);
    }
  }, [isMonitoring, runInference]);

  const handleExitMonitor = () => {
    stopMonitoring();
    setView('home');
    if (document.fullscreenElement) {
      document.exitFullscreen();
    }
  };

  const handleStartMonitor = async () => {
    await startMonitoring();
    try {
      await document.documentElement.requestFullscreen();
    } catch (e) {}
  };

  return (
    <div className="h-screen w-screen bg-black text-white overflow-hidden font-sans">
      {view === 'home' ? (
        <HomeDashboard 
          stats={stats} 
          violations={violations} 
          onStart={handleStartMonitor} 
          availableCameras={availableCameras}
          selectedCameraId={selectedCameraId}
          onCameraSelect={setSelectedCameraId}
        />
      ) : (
        <Dashboard 
          stream={stream}
          videoRef={videoRef}
          detections={detections}
          logs={logs}
          violations={violations}
          stats={stats}
          isProcessing={isProcessing}
          onTriggerAlert={() => triggerViolation("MANUAL OVERRIDE PANIC", ThreatLevel.CRITICAL)}
          onExit={handleExitMonitor}
          onToggleMonitoring={() => isMonitoring ? stopMonitoring() : startMonitoring()}
          isMonitoring={isMonitoring}
          availableCameras={availableCameras}
          selectedCameraId={selectedCameraId}
          onCameraSelect={(id) => {
            setSelectedCameraId(id);
            startMonitoring(id);
          }}
        />
      )}
    </div>
  );
};

export default App;
