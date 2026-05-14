function MetricCard({ title, value, icon: Icon, tone = 'lilac' }) {
  const tones = {
    lilac: 'from-clinic-lilac/70 to-white text-clinic-violet',
    pink: 'from-clinic-cream to-white text-amber-700',
    rose: 'from-clinic-mint to-white text-clinic-teal',
    blue: 'from-clinic-mint to-white text-clinic-teal',
  };

  return (
    <div className="panel group p-5 transition duration-200 hover:-translate-y-1 hover:shadow-lift">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">{title}</h3>
          <p className="mt-4 text-3xl font-bold text-clinic-ink">{value}</p>
        </div>
        <span className={`grid h-12 w-12 place-items-center rounded-xl bg-gradient-to-br ${tones[tone]} transition group-hover:scale-105`}>
          <Icon className="h-6 w-6" />
        </span>
      </div>
    </div>
  );
}

export default MetricCard;
