
import React from 'react';
import { Violation, ThreatLevel } from '../types';

interface ViolationTableProps {
  violations: Violation[];
}

const ViolationTable: React.FC<ViolationTableProps> = ({ violations }) => {
  return (
    <div className="w-full h-full overflow-y-auto overflow-x-hidden">
      <table className="w-full text-left text-[10px] font-mono">
        <thead className="sticky top-0 bg-slate-900/95 backdrop-blur-sm z-10">
          <tr className="border-b border-white/10">
            <th className="pb-3 pt-1 px-2 text-white/40 font-black uppercase tracking-wider text-[8px]">Time</th>
            <th className="pb-3 pt-1 px-2 text-white/40 font-black uppercase tracking-wider text-[8px]">Type</th>
            <th className="pb-3 pt-1 px-2 text-right text-white/40 font-black uppercase tracking-wider text-[8px]">Severity</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {violations.map((v) => (
            <tr key={v.id} className="hover:bg-white/5 transition-colors">
              <td className="py-3 px-2 text-white/60 font-mono text-[9px]">{v.timestamp}</td>
              <td className="py-3 px-2 text-white font-medium text-[9px] truncate max-w-[120px]" title={v.type}>{v.type}</td>
              <td className="py-3 px-2 text-right">
                <span className={`px-2 py-1 rounded-lg text-[8px] font-black uppercase tracking-wider inline-block ${
                  v.severity === ThreatLevel.CRITICAL ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 
                  v.severity === ThreatLevel.HIGH ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' : 
                  'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                }`}>
                  {v.severity}
                </span>
              </td>
            </tr>
          ))}
          {violations.length === 0 && (
            <tr>
              <td colSpan={3} className="py-12 text-center">
                <div className="flex flex-col items-center justify-center space-y-2">
                  <svg className="w-12 h-12 text-white/10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-white/30 text-[10px] font-bold uppercase tracking-wider">No violations detected</p>
                  <p className="text-white/20 text-[8px]">System monitoring active</p>
                </div>
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default ViolationTable;
