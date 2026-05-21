function ModuleTab({ active, children, icon: Icon, onClick }) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      onClick={onClick}
      className={`inline-flex h-11 min-h-11 shrink-0 items-center justify-center gap-2 rounded-lg border px-4 text-sm font-bold transition ${
        active
          ? 'border-primary bg-primary text-primary-content shadow-sm'
          : 'border-transparent bg-transparent text-clinic-muted hover:border-base-300 hover:bg-base-200 hover:text-clinic-ink'
      }`}
    >
      <Icon className={`h-4 w-4 ${active ? 'text-primary-content' : 'text-secondary'}`} />
      {children}
    </button>
  );
}

export default ModuleTab;
