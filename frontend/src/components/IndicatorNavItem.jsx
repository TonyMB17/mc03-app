function IndicatorNavItem({ active, indicator, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`btn h-auto min-h-0 w-full justify-start rounded-md border px-3 py-2 text-left normal-case ${
        active
          ? 'border-primary bg-primary text-primary-content shadow-sm'
          : 'btn-ghost border-transparent text-clinic-muted hover:border-base-300 hover:bg-base-200 hover:text-clinic-ink'
      }`}
    >
      <span className="flex items-center justify-between gap-2">
        <span className="text-sm font-bold">{indicator.shortName}</span>
        <span className={`text-[0.68rem] font-bold uppercase ${active ? 'text-primary-content/75' : 'text-clinic-subtle'}`}>{indicator.defaultTarget}%</span>
      </span>
      <span className="mt-1 block text-xs leading-5">{indicator.title}</span>
    </button>
  );
}

export default IndicatorNavItem;
