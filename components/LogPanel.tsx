
import React from 'react';

interface LogPanelProps {
  logs: string[];
}

const LogPanel: React.FC<LogPanelProps> = ({ logs }) => {
  return (
    <div className="flex-1 overflow-y-auto font-mono text-xs space-y-1 scrollbar-hide">
      {logs.length === 0 ? (
        <p className="text-slate-600 italic">Waiting for telemetry...</p>
      ) : (
        logs.map((log, idx) => (
          <div key={idx} className="flex space-x-2">
            <span className={log.includes('VIOLATION') ? 'text-red-400 font-bold' : log.includes('ERROR') ? 'text-orange-500' : 'text-cyan-600'}>
              {log}
            </span>
          </div>
        ))
      )}
    </div>
  );
};

export default LogPanel;
