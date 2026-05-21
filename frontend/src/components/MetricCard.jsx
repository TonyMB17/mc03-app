function MetricCard({ title, value, icon: Icon, tone = 'lilac' }) {
  const tones = {
    lilac: 'bg-usi-lilac/15 text-accent ring-accent/20',
    pink: 'bg-base-200 text-secondary ring-base-300',
    rose: 'bg-clinic-mint text-secondary ring-secondary/20',
    blue: 'bg-clinic-sky text-info ring-info/15',
  };

  return (
    <div className="card border border-base-300 bg-base-100 p-4 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-lift">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xs font-bold uppercase text-clinic-muted">{title}</h3>
          <p className="mt-3 text-2xl font-bold text-clinic-ink">{value}</p>
        </div>
        <span className={`grid h-11 w-11 place-items-center rounded-lg ring-1 ${tones[tone]} transition group-hover:scale-105`}>
          <Icon className="h-5 w-5" />
        </span>
      </div>
    </div>
  );
}

export default MetricCard;
