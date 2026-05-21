function UsiStat({ icon: Icon, label, value, helper, tone = 'primary', className = '' }) {
  const toneClass = {
    primary: 'text-primary',
    secondary: 'text-secondary',
    accent: 'text-accent',
    success: 'text-success',
    warning: 'text-warning',
    error: 'text-error',
    neutral: 'text-neutral',
  };

  return (
    <div className={`stat rounded-xl border border-base-300 bg-base-100 p-4 shadow-sm ${className}`.trim()}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[0.68rem] font-bold uppercase tracking-[0.16em] text-base-content/55">{label}</p>
          <p className="mt-2 break-words text-2xl font-black text-primary">{value}</p>
          {helper && <p className="mt-1 text-xs font-semibold leading-5 text-base-content/60">{helper}</p>}
        </div>
        {Icon && <Icon className={`h-5 w-5 shrink-0 ${toneClass[tone] ?? toneClass.primary}`} />}
      </div>
    </div>
  );
}

export default UsiStat;
