const MetricCard = ({ title, value, trend, onClick, actionLabel }) => {
  const content = (
    <>
      <p className="text-sm font-medium text-slate-500 uppercase tracking-wide">{title}</p>
      <p className="text-3xl font-semibold text-primary-700 mt-2">{value}</p>
      {trend && <p className="text-xs text-slate-500 mt-1">{trend}</p>}
      {onClick && (
        <span className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-primary-600">
          {actionLabel || "Review details"}
          <span aria-hidden="true">→</span>
        </span>
      )}
    </>
  );

  if (typeof onClick === "function") {
    return (
      <button
        type="button"
        onClick={onClick}
        className="glass-card p-5 text-left focus:outline-none focus:ring-2 focus:ring-primary-500 hover:shadow-lg transition"
      >
        {content}
      </button>
    );
  }

  return <div className="glass-card p-5">{content}</div>;
};

export default MetricCard;
