function PageHeader({ icon: Icon, title, description, aside }) {
  return (
    <div className="mb-4 flex flex-col gap-2 border-b border-clinic-line pb-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-3">
        <span className="btn btn-square btn-primary h-10 min-h-10 w-10 rounded-xl shadow-sm">
          <Icon className="h-5 w-5" />
        </span>
        <div>
          <h2 className="text-2xl font-bold text-clinic-ink">{title}</h2>
          {description && <p className="text-sm leading-6 text-clinic-muted">{description}</p>}
        </div>
      </div>
      {aside}
    </div>
  );
}

export default PageHeader;
