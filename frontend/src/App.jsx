import { useEffect, useMemo, useState } from 'react';
import { Activity, BarChart3, Baby, ChevronDown, DatabaseZap, Layers3, LogOut, PanelLeftClose, PanelLeftOpen, Search, Settings2, ShieldCheck, SlidersHorizontal, UserCheck, UsersRound } from 'lucide-react';
import api, { clearAuth, loadStoredAuth, saveAuthUser, setAuthToken } from './api/client';
import IndicatorNavItem from './components/IndicatorNavItem';
import ModuleTab from './components/ModuleTab';
import PageHeader from './components/PageHeader';
import TopbarChip from './components/TopbarChip';
import indicators, { indicatorList } from './indicators/registry';
import ConfigView, { ALL_PROVINCES, DEFAULT_TARGET_COVERAGE } from './pages/ConfigView';
import Dashboard from './pages/IndicatorDashboard';
import DataUploadView from './pages/DataUploadView';
import LoginView from './LoginView';
import SearchDNI from './pages/RecordSearch';
import SecurityUsers from './pages/SecurityUsers';

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
  users: {
    title: 'Usuarios y permisos',
    description: 'Administra accesos, roles y permisos de la plataforma.',
    icon: UsersRound,
    permission: 'users_admin',
  },
};

function App() {
  const [selectedIndicator, setSelectedIndicator] = useState('mc03');
  const [selectedSi02Subindicator, setSelectedSi02Subindicator] = useState('all');
  const [si02AccordionOpen, setSi02AccordionOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
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
  const drawerWidth = sidebarCollapsed ? '5rem' : '18rem';

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
    setSelectedSi02Subindicator('all');
    setSi02AccordionOpen(nextIndicator === 'si02');
    setSelectedProvince(indicators[nextIndicator].defaultProvince);
    setTargetCoverage(indicators[nextIndicator].defaultTarget);
  };

  const handleSi02SubindicatorChange = (nextSubindicator) => {
    handleIndicatorChange('si02');
    setSelectedSi02Subindicator(nextSubindicator);
    setSi02AccordionOpen(true);
    if (permissions.includes('dashboard')) {
      setActiveView('dashboard');
    }
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
      <div data-theme="usiTheme" className="grid min-h-screen place-items-center bg-base-200 px-4 text-base-content">
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
    <div data-theme="usiTheme" className="app-shell min-h-screen bg-base-200">
      <aside
        className="fixed inset-y-0 left-0 z-50 flex flex-col border-r border-clinic-line bg-base-100 shadow-soft transition-[width] duration-200"
        style={{ width: drawerWidth }}
      >
        <div className={`flex min-h-16 items-center border-b border-clinic-line px-3 ${sidebarCollapsed ? 'justify-center' : 'justify-between gap-3'}`}>
          <div className={`flex min-w-0 items-center gap-3 ${sidebarCollapsed ? 'hidden' : ''}`}>
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-primary text-primary-content shadow-sm">
              <ShieldCheck className="h-5 w-5" />
            </span>
            <div className="min-w-0">
              <p className="text-xs font-bold uppercase text-clinic-muted">Red de Salud</p>
              <p className="truncate text-sm font-bold text-clinic-ink">Abancay</p>
            </div>
          </div>
          {sidebarCollapsed && (
            <span className="grid h-10 w-10 place-items-center rounded-lg bg-primary text-primary-content shadow-sm">
              <ShieldCheck className="h-5 w-5" />
            </span>
          )}
          <button
            type="button"
            onClick={() => setSidebarCollapsed((current) => !current)}
            className={`${sidebarCollapsed ? 'absolute right-2 top-3' : ''} btn btn-square btn-ghost h-9 min-h-9 w-9 rounded-md border border-base-300 bg-base-100 text-base-content/60 hover:border-secondary hover:bg-base-200 hover:text-secondary`}
            aria-label={sidebarCollapsed ? 'Expandir sidebar' : 'Minimizar sidebar'}
          >
            {sidebarCollapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
          </button>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-3 py-4">
          <div className={`mb-4 rounded-lg border border-base-300 bg-base-200 p-3 ${sidebarCollapsed ? 'px-2' : ''}`}>
            <div className={`flex items-start gap-3 ${sidebarCollapsed ? 'justify-center' : ''}`}>
              <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-secondary/10 text-secondary ring-1 ring-secondary/20">
                <Baby className="h-5 w-5" />
              </span>
              {!sidebarCollapsed && (
                <div>
                  <p className="text-xs font-bold uppercase text-clinic-muted">Indicador activo</p>
                  <p className="mt-1 text-sm font-bold leading-5 text-clinic-ink">{activeIndicator.shortName}</p>
                  <p className="mt-1 text-xs leading-5 text-clinic-muted">{activeIndicator.description}</p>
                </div>
              )}
            </div>
          </div>

          <section className="mb-4">
            {!sidebarCollapsed && <p className="mb-2 px-1 text-xs font-bold uppercase text-clinic-muted">Indicadores</p>}
            <div className="grid gap-1">
              {indicatorList.map((indicator) => {
                const isSi02 = indicator.code === 'si02';
                const active = selectedIndicator === indicator.code;
                return (
                  <div key={indicator.code}>
                    <div className="flex items-stretch gap-1">
                      {sidebarCollapsed ? (
                        <button
                          type="button"
                          title={indicator.title}
                          onClick={() => handleIndicatorChange(indicator.code)}
                          className={`grid h-10 w-full place-items-center rounded-md border text-sm font-bold transition ${
                            active
                              ? 'border-primary bg-primary text-primary-content'
                              : 'border-transparent text-clinic-muted hover:border-base-300 hover:bg-base-200 hover:text-clinic-ink'
                          }`}
                        >
                          {indicator.shortName.replace('-', '')}
                        </button>
                      ) : (
                        <IndicatorNavItem active={active} indicator={indicator} onClick={() => handleIndicatorChange(indicator.code)} />
                      )}
                      {isSi02 && !sidebarCollapsed && (
                        <button
                          type="button"
                          onClick={() => {
                            setSi02AccordionOpen((current) => !current);
                            if (!active) handleIndicatorChange('si02');
                          }}
                          className="grid w-10 shrink-0 place-items-center rounded-md border border-base-300 text-base-content/60 transition hover:border-secondary hover:bg-base-200 hover:text-secondary"
                          aria-label="Ver subindicadores SI-02"
                          aria-expanded={si02AccordionOpen}
                        >
                          <ChevronDown className={`h-4 w-4 transition ${si02AccordionOpen ? 'rotate-180' : ''}`} />
                        </button>
                      )}
                    </div>
                    {isSi02 && si02AccordionOpen && !sidebarCollapsed && (
                      <div className="ml-3 mt-1 grid gap-1 border-l border-clinic-line pl-2">
                        <button
                          type="button"
                          onClick={() => handleSi02SubindicatorChange('all')}
                          className={`flex items-center gap-2 rounded-md px-2.5 py-2 text-left text-xs font-bold transition ${
                            selectedIndicator === 'si02' && selectedSi02Subindicator === 'all'
                              ? 'bg-primary text-primary-content'
                              : 'text-clinic-muted hover:bg-base-200 hover:text-clinic-ink'
                          }`}
                        >
                          <Layers3 className="h-3.5 w-3.5 text-secondary" />
                          Global SI-02
                        </button>
                        {(indicator.subindicators ?? []).map((subindicator) => (
                          <button
                            key={subindicator.code}
                            type="button"
                            onClick={() => handleSi02SubindicatorChange(subindicator.code)}
                            className={`rounded-md px-2.5 py-2 text-left transition ${
                              selectedIndicator === 'si02' && selectedSi02Subindicator === subindicator.code
                                ? 'bg-primary text-primary-content'
                                : 'text-clinic-muted hover:bg-base-200 hover:text-clinic-ink'
                            }`}
                          >
                            <span className="block text-xs font-bold">{subindicator.officialCode}</span>
                            <span className="mt-0.5 block text-[0.68rem] leading-4">{subindicator.title}</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </section>

          {!sidebarCollapsed && (
            <div className="rounded-lg border border-base-300 bg-base-200 p-3 text-xs leading-5 text-clinic-muted">
              Los modulos principales estan fijados arriba para mantenerlos accesibles mientras navegas indicadores.
            </div>
          )}
        </div>

        <div className="border-t border-base-300 bg-base-200 p-3">
          {sidebarCollapsed ? (
            <div className="grid place-items-center">
              <UserCheck className="h-5 w-5 text-secondary" />
            </div>
          ) : (
            <>
              <p className="text-xs font-bold uppercase text-clinic-muted">Sesion</p>
              <p className="mt-1 truncate text-sm font-bold text-clinic-ink">{user.display_name}</p>
              <p className="text-xs leading-5 text-clinic-muted">{user.role_label}</p>
            </>
          )}
        </div>
      </aside>

      <header
        className="fixed right-0 top-0 z-40 border-b border-primary/40 bg-primary text-primary-content shadow-soft transition-[left] duration-200"
        style={{ left: drawerWidth }}
      >
        <div className="mx-auto grid max-w-[92rem] gap-3 px-4 py-3 sm:px-6">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex min-w-0 items-center gap-3">
              <div className="min-w-0">
                <p className="text-xs font-bold uppercase text-primary-content/70">Plataforma de indicadores</p>
                <h1 className="truncate text-lg font-bold text-primary-content sm:text-xl">{activeIndicator.title}</h1>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <TopbarChip icon={Activity} label="Filtro" value={activeFilterLabel} />
              <TopbarChip icon={Settings2} label="Meta" value={`${targetCoverage}%`} />
              <TopbarChip icon={UserCheck} label={user.role_label} value={user.display_name} />
              {user.auth_enabled && (
                <TopbarChip as="button" type="button" onClick={handleLogout} className="hover:border-secondary hover:bg-secondary/10">
                  <LogOut className="h-4 w-4 text-secondary" />
                  <span className="font-bold text-clinic-ink">Salir</span>
                </TopbarChip>
              )}
            </div>
          </div>

          <nav className="-mx-1 flex gap-2 overflow-x-auto px-1 pb-1" aria-label="Modulos principales">
            {permissions.includes('search') && (
              <ModuleTab active={safeActiveView === 'search'} icon={Search} onClick={() => setActiveView('search')}>
                Busqueda DNI
              </ModuleTab>
            )}
            {permissions.includes('dashboard') && (
              <ModuleTab active={safeActiveView === 'dashboard'} icon={BarChart3} onClick={() => setActiveView('dashboard')}>
                Dashboard
              </ModuleTab>
            )}
            {permissions.includes('config') && (
              <ModuleTab active={safeActiveView === 'config'} icon={SlidersHorizontal} onClick={() => setActiveView('config')}>
                Configuracion
              </ModuleTab>
            )}
            {permissions.includes('data_upload') && (
              <ModuleTab active={safeActiveView === 'data'} icon={DatabaseZap} onClick={() => setActiveView('data')}>
                Carga datos
              </ModuleTab>
            )}
            {permissions.includes('users_admin') && (
              <ModuleTab active={safeActiveView === 'users'} icon={UsersRound} onClick={() => setActiveView('users')}>
                Usuarios
              </ModuleTab>
            )}
          </nav>
        </div>
      </header>

      <div className="transition-[padding-left] duration-200" style={{ paddingLeft: drawerWidth }}>
        <main className="mx-auto min-w-0 max-w-[92rem] animate-fade-in px-4 pb-6 pt-44 sm:px-6 lg:pt-36">
          <PageHeader
            icon={CurrentIcon}
            title={currentView.title}
            description={currentView.description}
            aside={
              <p className="inline-flex w-fit items-center gap-2 rounded-md border border-base-300 bg-base-100 px-3 py-2 text-sm font-semibold text-clinic-muted shadow-sm">
                <Activity className="h-4 w-4 text-secondary" />
                {activeIndicator.shortName} / {activeFilterLabel}
              </p>
            }
          />
          {safeActiveView === 'search' && <SearchDNI selectedProvince={selectedProvince} selectedIndicator={selectedIndicator} />}
          {safeActiveView === 'dashboard' && (
            <Dashboard
              selectedProvince={selectedProvince}
              targetCoverage={targetCoverage}
              selectedIndicator={selectedIndicator}
              selectedSi02Subindicator={selectedSi02Subindicator}
              onSi02SubindicatorChange={setSelectedSi02Subindicator}
            />
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
          {safeActiveView === 'users' && <SecurityUsers />}
        </main>
      </div>
    </div>
  );
}

export default App;
