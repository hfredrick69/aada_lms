const MetricCard = ({ title, value, trend }) => {
  return (
    <div className="glass-card p-5">
      <p className="text-sm font-medium text-slate-500 uppercase tracking-wide">{title}</p>
      <p className="text-3xl font-semibold text-primary-700 mt-2">{value}</p>
      {trend && <p className="text-xs text-emerald-600 mt-1">{trend}</p>}
    </div>
  );
};

export default MetricCard;
