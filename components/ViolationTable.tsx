
import React from 'react';
import { Violation, ThreatLevel } from '../types';

interface ViolationTableProps {
  violations: Violation[];
}

const ViolationTable: React.FC<ViolationTableProps> = ({ violations }) => {
  return (
    <div className="flex-1 overflow-auto">
      <table className="w-full text-left text-[11px] font-mono border-separate border-spacing-y-2">
        <thead className="sticky top-0 bg-slate-800/90 text-slate-500 uppercase">
          <tr>
            <th className="pb-2">Time</th>
            <th className="pb-2">Type</th>
            <th className="pb-2 text-right">Sev</th>
          </tr>
        </thead>
        <tbody>
          {violations.map((v) => (
            <tr key={v.id} className="bg-slate-900/40 hover:bg-slate-700/50 transition-colors">
              <td className="py-2 pl-2 rounded-l-md border-y border-l border-slate-700">{v.timestamp}</td>
              <td className="py-2 border-y border-slate-700">{v.type}</td>
              <td className="py-2 pr-2 text-right rounded-r-md border-y border-r border-slate-700">
                <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${
                  v.severity === ThreatLevel.CRITICAL ? 'bg-red-900/50 text-red-400' : 
                  v.severity === ThreatLevel.HIGH ? 'bg-orange-900/50 text-orange-400' : 'bg-emerald-900/50 text-emerald-400'
                }`}>
                  {v.severity}
                </span>
              </td>
            </tr>
          ))}
          {violations.length === 0 && (
            <tr>
              <td colSpan={3} className="py-8 text-center text-slate-600">No violations detected in current session.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default ViolationTable;
