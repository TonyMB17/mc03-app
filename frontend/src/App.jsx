import { useEffect, useMemo, useState } from 'react';
import { Activity, BarChart3, Baby, DatabaseZap, LogOut, Search, Settings2, ShieldCheck, SlidersHorizontal, UserCheck } from 'lucide-react';
import api, { clearAuth, loadStoredAuth, saveAuthUser, setAuthToken } from './api/client';
import IndicatorSelector from './components/IndicatorSelector';
import indicators, { indicatorList } from './indicators/registry';
import ConfigView, { ALL_PROVINCES, DEFAULT_TARGET_COVERAGE } from './pages/ConfigView';
import Dashboard from './pages/IndicatorDashboard';
import DataUploadView from './pages/DataUploadView';
import LoginView from './LoginView';
import SearchDNI from './pages/RecordSearch';

const views = {
  search: {
    title: 'Busqueda por DNI',
    description: 'Consulta individual y estado del paquete del indicador seleccionado.',
    icon: Search,
    permission: 'search',
  },
  dashboard: {
    title: 'Dashboard del indicador',
    description: 'Seguimiento mensual del compromiso, cobertura e incumplidos del periodo de verificacion.',
    icon: BarChart3,
    permission: 'dashboard',
  },
  config: {
    title: 'Configuracion',
    description: 'Define la poblacion objetivo, meta y semaforo del indicador.',
    icon: SlidersHorizontal,
    permission: 'config',
  },
  data: {
    title: 'Carga de datos',
    description: 'Carga, valida y activa el Excel operativo del indicador seleccionado.',
    icon: DatabaseZap,
    permission: 'data_upload',
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
  const [selectedIndicator, setSelectedIndicator] = useState('mc03');
  const [activeView, setActiveView] = useState('search');
  const [selectedProvince, setSelectedProvince] = useState('ABANCAY');
  const [targetCoverage, setTargetCoverage] = useState(DEFAULT_TARGET_COVERAGE);
  const [authStatus, setAuthStatus] = useState('loading');
  const [user, setUser] = useState(() => loadStoredAuth().user);
  const activeIndicator = indicators[selectedIndicator];
  const permissions = user?.permissions ?? [];
  const allowedViewKeys = useMemo(
    () => Object.keys(views).filter((key) => permissions.includes(views[key].permission)),
    [permissions],
  );
  const safeActiveView = allowedViewKeys.includes(activeView) ? activeView : (allowedViewKeys[0] ?? 'search');
  const currentView = views[safeActiveView];
  const CurrentIcon = currentView.icon;
  const activeFilterLabel = selectedProvince === ALL_PROVINCES ? 'Todos los datos' : selectedProvince;

  useEffect(() => {
    let cancelled = false;
    const loadSession = async () => {
      const stored = loadStoredAuth();
      if (stored.token) setAuthToken(stored.token);

      try {
        const response = await api.get('/api/auth/me');
        if (cancelled) return;
        setUser(response.data);
        saveAuthUser(response.data);
      } catch {
        if (cancelled) return;
        clearAuth();
        setUser(null);
      } finally {
        if (!cancelled) setAuthStatus('ready');
      }
    };

    loadSession();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (authStatus !== 'ready') return;
    if (!allowedViewKeys.length) return;
    if (!allowedViewKeys.includes(activeView)) {
      setActiveView(allowedViewKeys[0]);
    }
  }, [activeView, allowedViewKeys, authStatus]);

  const handleIndicatorChange = (nextIndicator) => {
    setSelectedIndicator(nextIndicator);
    setSelectedProvince(indicators[nextIndicator].defaultProvince);
    setTargetCoverage(indicators[nextIndicator].defaultTarget);
  };

  const handleLogin = (nextUser) => {
    setUser(nextUser);
    setAuthStatus('ready');
  };

  const handleLogout = () => {
    clearAuth();
    setUser(null);
  };

  if (authStatus === 'loading') {
    return (
      <div className="grid min-h-screen place-items-center bg-clinic-page px-4 text-clinic-ink">
        <div className="panel p-6 text-center">
          <ShieldCheck className="mx-auto h-8 w-8 text-clinic-teal" />
          <p className="mt-3 text-sm font-bold text-clinic-muted">Preparando sesion...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <LoginView onLogin={handleLogin} />;
  }

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
                    {activeIndicator.title}
                  </h1>
                  <p className="mt-2 text-sm leading-6 text-white/75 sm:text-base">
                    {activeIndicator.description} {currentView.description}
                  </p>
                </div>
              </div>
              <div className="mt-5 flex flex-wrap gap-3">
                <IndicatorSelector indicators={indicatorList} value={selectedIndicator} onChange={handleIndicatorChange} />
                <p className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-white/75">
                  <Activity className="h-4 w-4 text-clinic-mint" />
                  Filtro activo: <span className="text-white">{activeFilterLabel}</span>
                </p>
                <p className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-white/75">
                  <Settings2 className="h-4 w-4 text-clinic-mint" />
                  Meta: <span className="text-white">{targetCoverage}%</span>
                </p>
                <p className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-white/75">
                  <UserCheck className="h-4 w-4 text-clinic-mint" />
                  {user.role_label}: <span className="text-white">{user.display_name}</span>
                </p>
                {user.auth_enabled && (
                  <button type="button" onClick={handleLogout} className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-white/80 hover:bg-white/20">
                    <LogOut className="h-4 w-4 text-clinic-mint" />
                    Salir
                  </button>
                )}
              </div>
            </div>

            <nav className="grid gap-3 sm:grid-cols-2 lg:flex" aria-label="Vistas principales">
              {permissions.includes('search') && (
                <NavButton active={safeActiveView === 'search'} icon={Search} onClick={() => setActiveView('search')}>
                  Busqueda DNI
                </NavButton>
              )}
              {permissions.includes('dashboard') && (
                <NavButton active={safeActiveView === 'dashboard'} icon={BarChart3} onClick={() => setActiveView('dashboard')}>
                  Dashboard
                </NavButton>
              )}
              {permissions.includes('config') && (
                <NavButton active={safeActiveView === 'config'} icon={SlidersHorizontal} onClick={() => setActiveView('config')}>
                  Configuracion
                </NavButton>
              )}
              {permissions.includes('data_upload') && (
                <NavButton active={safeActiveView === 'data'} icon={DatabaseZap} onClick={() => setActiveView('data')}>
                  Carga datos
                </NavButton>
              )}
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
          {safeActiveView === 'search' && <SearchDNI selectedProvince={selectedProvince} selectedIndicator={selectedIndicator} />}
          {safeActiveView === 'dashboard' && (
            <Dashboard selectedProvince={selectedProvince} targetCoverage={targetCoverage} selectedIndicator={selectedIndicator} />
          )}
          {safeActiveView === 'config' && (
            <ConfigView
              selectedIndicator={selectedIndicator}
              selectedProvince={selectedProvince}
              onProvinceChange={setSelectedProvince}
              targetCoverage={targetCoverage}
              onTargetCoverageChange={setTargetCoverage}
            />
          )}
          {safeActiveView === 'data' && <DataUploadView selectedIndicator={selectedIndicator} />}
        </main>
      </div>
    </div>
  );
}

export default App;
