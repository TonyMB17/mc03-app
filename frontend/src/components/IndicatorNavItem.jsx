import { ChevronDown } from 'lucide-react';

function IndicatorNavItem({ active, indicator, expandable = false, expanded = false, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-expanded={expandable ? expanded : undefined}
      className={`btn h-auto min-h-0 w-full justify-start rounded-md border px-3 py-2 text-left normal-case ${
        active
          ? 'border-primary bg-primary text-primary-content shadow-sm'
          : 'btn-ghost border-transparent text-clinic-muted hover:border-base-300 hover:bg-base-200 hover:text-clinic-ink'
      }`}
    >
      <span className="grid w-full min-w-0 grid-cols-[minmax(0,1fr)_auto] items-start gap-2">
        <span className="min-w-0 text-left">
          <span className="block text-sm font-bold">{indicator.shortName}</span>
          <span className="mt-1 block truncate text-xs leading-5">{indicator.title}</span>
        </span>
        {expandable && (
          <ChevronDown className={`mt-0.5 h-4 w-4 shrink-0 transition ${expanded ? 'rotate-180' : ''} ${active ? 'text-primary-content/80' : 'text-secondary'}`} />
        )}
      </span>
    </button>
  );
}

export default IndicatorNavItem;
