function TopbarChip({ icon: Icon, label, value, as: Component = 'p', children, className = '', ...props }) {
  return (
    <Component className={`badge badge-lg h-auto min-h-10 max-w-full gap-2 rounded-md border-base-300 bg-base-100 px-3 py-2 text-sm font-bold text-base-content shadow-sm ${className}`.trim()} {...props}>
      {Icon && <Icon className="h-4 w-4 text-secondary" />}
      {label && <span className="text-clinic-muted">{label}</span>}
      {value && <span className="font-bold text-clinic-ink">{value}</span>}
      {children}
    </Component>
  );
}

export default TopbarChip;
