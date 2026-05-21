function TopbarChip({ icon: Icon, label, value, as: Component = 'p', children, className = '', ...props }) {
  return (
    <Component
      className={`inline-flex min-h-9 max-w-full items-center gap-2.5 border-l border-primary-content/20 pl-4 pr-1 text-sm text-primary-content/80 first:border-l-0 first:pl-0 ${className}`.trim()}
      {...props}
    >
      {Icon && <Icon className="h-4 w-4 shrink-0 text-primary-content/70" />}
      {label && <span className="text-[0.66rem] font-bold uppercase tracking-[0.14em] text-primary-content/60">{label}</span>}
      {value && <span className="truncate font-bold text-primary-content">{value}</span>}
      {children}
    </Component>
  );
}

export default TopbarChip;
