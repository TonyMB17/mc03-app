function PlatformFooter() {
  return (
    <footer className="mt-8 rounded-xl border border-base-300 bg-base-100 px-4 py-4 text-xs text-clinic-muted shadow-sm sm:px-5">
      <div className="flex flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="font-bold uppercase tracking-[0.14em] text-primary">Red de Salud Abancay</p>
          <p className="mt-1 leading-5">Sistema de seguimiento de indicadores sanitarios - Unidad de Salud Individual.</p>
        </div>
        <div className="flex flex-wrap gap-x-4 gap-y-1 font-semibold">
          <span>Version operativa 2026</span>
        </div>
      </div>
    </footer>
  );
}

export default PlatformFooter;
