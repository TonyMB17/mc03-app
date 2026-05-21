const toneClass = {
  primary: 'badge-primary',
  secondary: 'badge-secondary',
  accent: 'badge-accent',
  success: 'badge-success',
  warning: 'badge-warning',
  error: 'badge-error',
  info: 'badge-info',
  neutral: 'badge-neutral',
  ghost: 'badge-ghost border-base-300 text-base-content/70',
};

function UsiBadge({ children, tone = 'ghost', className = '', icon: Icon }) {
  return (
    <span className={`badge h-auto gap-1.5 px-3 py-1.5 text-xs font-bold ${toneClass[tone] ?? toneClass.ghost} ${className}`.trim()}>
      {Icon && <Icon className="h-3.5 w-3.5" />}
      {children}
    </span>
  );
}

export default UsiBadge;
