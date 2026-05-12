import { useState } from 'react';
import { Activity, BarChart3, Baby, Search, Settings2, ShieldCheck, SlidersHorizontal } from 'lucide-react';
import ConfigView, { ALL_PROVINCES, DEFAULT_TARGET_COVERAGE } from './ConfigView';
import Dashboard from './Dashboard';
import SearchDNI from './SearchDNI';

const views = {
  search: {
    title: 'Busqueda por DNI',
    description: 'Consulta individual del recien nacido y estado del paquete MC-03.',
    icon: Search,
  },
  dashboard: {
    title: 'Dashboard del indicador',
    description: 'Seguimiento mensual del compromiso, cobertura e incumplidos del periodo de verificacion.',
    icon: BarChart3,
  },
  config: {
    title: 'Configuracion',
    description: 'Define la poblacion objetivo, meta y semaforo del indicador.',
    icon: SlidersHorizontal,
  },
};

function NavButton({ active, children, icon: Icon, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`group inline-flex min-h-11 items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition duration-200 ${
        active
          ? 'bg-white text-clinic-ink shadow-soft'
          : 'border border-white/20 bg-white/10 text-white/85 hover:-translate-y-0.5 hover:border-white/40 hover:bg-white/20 hover:text-white'
      }`}
    >
      <Icon className={`h-4 w-4 transition ${active ? 'text-clinic-teal' : 'text-clinic-mint group-hover:text-white'}`} />
      {children}
    </button>
  );
}

function App() {
  const [activeView, setActiveView] = useState('search');
  const [selectedProvince, setSelectedProvince] = useState('ABANCAY');
  const [targetCoverage, setTargetCoverage] = useState(DEFAULT_TARGET_COVERAGE);
  const currentView = views[activeView];
  const CurrentIcon = currentView.icon;
  const activeFilterLabel = selectedProvince === ALL_PROVINCES ? 'Todos los datos' : selectedProvince;

  return (
    <div className="min-h-screen overflow-hidden bg-clinic-page px-4 py-6 text-clinic-ink sm:px-6 lg:py-8">
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute left-0 top-0 h-[26rem] w-[40rem] bg-[radial-gradient(circle_at_center,rgba(250,206,255,0.32),transparent_70%)]" />
        <div className="absolute right-0 top-0 h-[26rem] w-[40rem] bg-[radial-gradient(circle_at_center,rgba(206,255,250,0.42),transparent_72%)]" />
      </div>

      <div className="mx-auto max-w-7xl space-y-6">
        <header className="animate-slide-up rounded-2xl border border-white/10 bg-gradient-to-br from-clinic-navy via-[#17485A] to-clinic-teal p-5 shadow-soft lg:p-7">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-bold uppercase tracking-[0.18em] text-white/90">
                <ShieldCheck className="h-4 w-4 text-clinic-mint" />
                Red de Salud Abancay
              </div>
              <div className="mt-5 flex items-center gap-4">
                <span className="grid h-14 w-14 shrink-0 place-items-center rounded-2xl bg-clinic-mint text-clinic-navy shadow-soft ring-1 ring-white/30">
                  <Baby className="h-7 w-7" />
                </span>
                <div>
                  <h1 className="text-3xl font-bold tracking-[-0.02em] text-white sm:text-4xl">
                    MC-03 Seguimiento Neonatal
                  </h1>
                  <p className="mt-2 text-sm leading-6 text-white/75 sm:text-base">{currentView.description}</p>
                </div>
              </div>
              <div className="mt-5 flex flex-wrap gap-3">
                <p className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-white/75">
                  <Activity className="h-4 w-4 text-clinic-mint" />
                  Filtro activo: <span className="text-white">{activeFilterLabel}</span>
                </p>
                <p className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-white/75">
                  <Settings2 className="h-4 w-4 text-clinic-mint" />
                  Meta: <span className="text-white">{targetCoverage}%</span>
                </p>
              </div>
            </div>

            <nav className="grid gap-3 sm:grid-cols-3 lg:flex" aria-label="Vistas principales">
              <NavButton active={activeView === 'search'} icon={Search} onClick={() => setActiveView('search')}>
                Busqueda DNI
              </NavButton>
              <NavButton active={activeView === 'dashboard'} icon={BarChart3} onClick={() => setActiveView('dashboard')}>
                Dashboard
              </NavButton>
              <NavButton active={activeView === 'config'} icon={SlidersHorizontal} onClick={() => setActiveView('config')}>
                Configuracion
              </NavButton>
            </nav>
          </div>
        </header>

        <main className="animate-fade-in">
          <div className="mb-4 flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-clinic-teal text-white shadow-sm ring-1 ring-clinic-border">
              <CurrentIcon className="h-5 w-5" />
            </span>
            <h2 className="text-2xl font-bold text-clinic-ink">{currentView.title}</h2>
          </div>
          {activeView === 'search' && <SearchDNI selectedProvince={selectedProvince} />}
          {activeView === 'dashboard' && (
            <Dashboard selectedProvince={selectedProvince} targetCoverage={targetCoverage} />
          )}
          {activeView === 'config' && (
            <ConfigView
              selectedProvince={selectedProvince}
              onProvinceChange={setSelectedProvince}
              targetCoverage={targetCoverage}
              onTargetCoverageChange={setTargetCoverage}
            />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
