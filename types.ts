
export enum ThreatLevel {
  LOW = 'LOW',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

export interface Detection {
  id: string;
  label: string;
  confidence: number;
  bbox: { x: number; y: number; width: number; height: number };
  distance: number;
}

export interface Violation {
  id: number;
  timestamp: string;
  type: string;
  severity: ThreatLevel;
}

export interface SystemStats {
  detectionCount: number;
  speed: number;
  fatigue: number;
  zone: string;
  helmetStatus: boolean;
}
