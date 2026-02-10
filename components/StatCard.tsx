
import React from 'react';

interface StatCardProps {
  title: string;
  value: string;
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, color }) => {
  return (
    <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-2xl border border-white/5 flex flex-col justify-between h-24">
      <p className="text-[10px] text-white/30 font-black uppercase tracking-[0.2em]">{title}</p>
      <p className={`text-2xl font-black italic tracking-tighter ${color}`}>{value}</p>
    </div>
  );
};

export default StatCard;
