function ModuleTab({ active, children, icon: Icon, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`btn btn-sm h-10 min-h-10 shrink-0 gap-2 rounded-md px-3 text-sm font-bold normal-case ${
        active
          ? 'btn-primary shadow-sm'
          : 'btn-ghost border border-base-300 bg-base-100 text-clinic-muted hover:border-primary hover:bg-clinic-mint hover:text-clinic-ink'
      }`}
    >
      <Icon className={`h-4 w-4 ${active ? 'text-primary-content' : 'text-secondary'}`} />
      {children}
    </button>
  );
}

export default ModuleTab;
