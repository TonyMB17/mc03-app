function TopbarChip({ icon: Icon, label, value, as: Component = 'p', children, className = '', ...props }) {
  return (
    <Component
      className={`inline-flex min-h-9 min-w-0 max-w-[calc(100vw-7rem)] items-center gap-2 border-l border-primary-content/20 pl-3 pr-1 text-xs text-primary-content/80 first:border-l-0 first:pl-0 sm:max-w-full sm:gap-2.5 sm:pl-4 sm:text-sm ${className}`.trim()}
      {...props}
    >
      {Icon && <Icon className="h-4 w-4 shrink-0 text-primary-content/70" />}
      {label && <span className="hidden text-[0.66rem] font-bold uppercase tracking-[0.14em] text-primary-content/60 sm:inline">{label}</span>}
      {value && <span className="min-w-0 truncate font-bold text-primary-content">{value}</span>}
      {children}
    </Component>
  );
}

export default TopbarChip;
