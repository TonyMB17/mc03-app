import { useEffect, useMemo, useState } from 'react';
import { Activity, BarChart3, DatabaseZap, LogOut, Menu, PanelLeftClose, PanelLeftOpen, Search, ShieldCheck, SlidersHorizontal, UserCheck, UsersRound } from 'lucide-react';
import api, { clearAuth, loadStoredAuth, saveAuthUser, setAuthToken } from './api/client';
import IndicatorNavItem from './components/IndicatorNavItem';
import ModuleTab from './components/ModuleTab';
import PageHeader from './components/PageHeader';
import PlatformFooter from './components/PlatformFooter';
import TopbarChip from './components/TopbarChip';
import useCompactHeader from './hooks/useCompactHeader';
import useMediaQuery from './hooks/useMediaQuery';
import indicators, { indicatorList } from './indicators/registry';
import ConfigView, { ALL_PROVINCES, DEFAULT_TARGET_COVERAGE } from './pages/ConfigView';
import Dashboard from './pages/IndicatorDashboard';
import DataUploadView from './pages/DataUploadView';
import AutomationView from './pages/AutomationView';
import LoginView from './LoginView';
import SearchDNI from './pages/RecordSearch';
import SecurityUsers from './pages/SecurityUsers';
import usiLogoIcon from './assets/svg/usi-logo-isotipo.svg';

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
  automation: {
    title: 'Automatizacion',
    description: 'Ejecuta la descarga, validacion y activacion automatica de archivos semanales.',
    icon: Activity,
    permission: 'automation',
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
  const isSi02Global = selectedIndicator === 'si02' && selectedSi02Subindicator === 'all';
  const allowedViewKeys = useMemo(
    () => Object.keys(views).filter((key) => permissions.includes(views[key].permission)),
    [permissions],
  );
  const visibleViewKeys = useMemo(
    () => (isSi02Global ? allowedViewKeys.filter((key) => key === 'dashboard') : allowedViewKeys),
    [allowedViewKeys, isSi02Global],
  );
  const safeActiveView = visibleViewKeys.includes(activeView) ? activeView : (visibleViewKeys[0] ?? 'dashboard');
  const currentView = views[safeActiveView];
  const CurrentIcon = currentView.icon;
  const activeFilterLabel = selectedProvince === ALL_PROVINCES ? 'Todos los datos' : selectedProvince;
  const activeScopeLabel = selectedProvince === 'ABANCAY' ? 'RS Abancay' : activeFilterLabel;
  const headerCompact = useCompactHeader();
  const isDesktopLayout = useMediaQuery('(min-width: 1024px)');
  const compactDrawerWidth = '4.75rem';
  const expandedDrawerWidth = isDesktopLayout ? '18rem' : 'min(18rem, calc(100vw - 1rem))';
  const drawerWidth = sidebarCollapsed ? compactDrawerWidth : expandedDrawerWidth;
  const contentOffset = isDesktopLayout ? drawerWidth : '0rem';
  const navStickyTop = isDesktopLayout ? (headerCompact ? '5.5rem' : '7.75rem') : (headerCompact ? '4.75rem' : '6.75rem');

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
    if (!visibleViewKeys.length) return;
    if (!visibleViewKeys.includes(activeView)) {
      setActiveView(visibleViewKeys[0]);
    }
  }, [activeView, authStatus, visibleViewKeys]);

  useEffect(() => {
    if (!isDesktopLayout) {
      setSidebarCollapsed(true);
    }
  }, [isDesktopLayout]);

  const closeSidebarOnMobile = () => {
    if (!isDesktopLayout) setSidebarCollapsed(true);
  };

  const handleIndicatorChange = (nextIndicator, options = {}) => {
    const { closeSidebar = true } = options;
    setSelectedIndicator(nextIndicator);
    setSelectedSi02Subindicator('all');
    setSi02AccordionOpen(nextIndicator === 'si02');
    setSelectedProvince(indicators[nextIndicator].defaultProvince);
    setTargetCoverage(indicators[nextIndicator].defaultTarget);
    if (closeSidebar) closeSidebarOnMobile();
  };

  const handleSi02SubindicatorChange = (nextSubindicator) => {
    handleIndicatorChange('si02', { closeSidebar: false });
    setSelectedSi02Subindicator(nextSubindicator);
    setSi02AccordionOpen(true);
    if (safeActiveView !== 'search' && permissions.includes('dashboard')) {
      setActiveView('dashboard');
    }
    closeSidebarOnMobile();
  };

  const handleSidebarIndicatorClick = (indicator) => {
    if (indicator.code !== 'si02') {
      handleIndicatorChange(indicator.code);
      return;
    }

    handleIndicatorChange('si02', { closeSidebar: false });
    setSi02AccordionOpen(true);
    if (permissions.includes('dashboard')) {
      setActiveView('dashboard');
    }
  };

  const showModuleTab = (viewKey) => visibleViewKeys.includes(viewKey);

  const handleLogin = (nextUser) => {
    setUser(nextUser);
    setAuthStatus('ready');
  };

  const handleLogout = () => {
    clearAuth();
    setUser(null);
  };

  const handleViewChange = (nextView) => {
    setActiveView(nextView);
    closeSidebarOnMobile();
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
      {!isDesktopLayout && !sidebarCollapsed && (
        <button
          type="button"
          aria-label="Cerrar menu lateral"
          className="fixed inset-0 z-40 bg-primary/45 backdrop-blur-[1px] lg:hidden"
          onClick={() => setSidebarCollapsed(true)}
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex flex-col overflow-x-hidden border-r border-clinic-line bg-base-100 shadow-soft transition-[width,transform] duration-200 ${
          isDesktopLayout || !sidebarCollapsed ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ width: drawerWidth }}
      >
        <div className={`border-b border-clinic-line px-3 ${sidebarCollapsed ? 'flex min-h-24 flex-col items-center justify-center gap-2' : 'flex min-h-16 items-center justify-between gap-3'}`}>
          <div className={`flex min-w-0 items-center gap-3 ${sidebarCollapsed ? 'hidden' : ''}`}>
            <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl border border-base-300 bg-base-100 p-1.5 shadow-sm">
              <img src={usiLogoIcon} alt="USI" className="h-full w-full object-contain" />
            </span>
            <div className="min-w-0">
              <p className="text-xs font-bold uppercase text-clinic-muted">Red de Salud</p>
              <p className="truncate text-sm font-bold text-clinic-ink">Abancay</p>
            </div>
          </div>
          {sidebarCollapsed && (
            <span className="grid h-11 w-11 place-items-center rounded-xl border border-base-300 bg-base-100 p-1.5 shadow-sm">
              <img src={usiLogoIcon} alt="USI" className="h-full w-full object-contain" />
            </span>
          )}
          <button
            type="button"
            onClick={() => setSidebarCollapsed((current) => !current)}
            className="btn btn-square btn-ghost h-9 min-h-9 w-9 rounded-md border border-base-300 bg-base-100 text-base-content/60 hover:border-secondary hover:bg-base-200 hover:text-secondary"
            aria-label={sidebarCollapsed ? 'Expandir sidebar' : 'Minimizar sidebar'}
          >
            {sidebarCollapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
          </button>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden px-3 py-4 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          <section className="mb-4">
            {!sidebarCollapsed && <p className="mb-2 px-1 text-xs font-bold uppercase text-clinic-muted">Indicadores</p>}
            <div className="grid gap-1">
              {indicatorList.map((indicator) => {
                const isSi02 = indicator.code === 'si02';
                const active = selectedIndicator === indicator.code;
                return (
                  <div key={indicator.code}>
                    <div className="flex items-stretch">
                      {sidebarCollapsed ? (
                        <button
                          type="button"
                          title={indicator.title}
                          onClick={() => handleSidebarIndicatorClick(indicator)}
                          className={`grid h-10 w-full place-items-center rounded-md border text-sm font-bold transition ${
                            active
                              ? 'border-primary bg-primary text-primary-content'
                              : 'border-transparent text-clinic-muted hover:border-base-300 hover:bg-base-200 hover:text-clinic-ink'
                          }`}
                        >
                          {indicator.shortName.replace('-', '')}
                        </button>
                      ) : (
                        <IndicatorNavItem
                          active={active}
                          indicator={indicator}
                          expandable={isSi02}
                          expanded={si02AccordionOpen}
                          onClick={() => handleSidebarIndicatorClick(indicator)}
                        />
                      )}
                    </div>
                    {isSi02 && si02AccordionOpen && !sidebarCollapsed && (
                      <div className="ml-3 mt-1 grid gap-1 border-l border-clinic-line pl-2">
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

          {permissions.includes('automation') && (
            <section className="mb-4 border-t border-clinic-line pt-4">
              {!sidebarCollapsed && <p className="mb-2 px-1 text-xs font-bold uppercase text-clinic-muted">Procesos</p>}
              <button
                type="button"
                title="Automatizacion de carga"
                onClick={() => handleViewChange('automation')}
                className={`flex h-11 w-full items-center gap-3 rounded-md border px-3 text-sm font-bold transition ${
                  safeActiveView === 'automation'
                    ? 'border-primary bg-primary text-primary-content shadow-sm'
                    : 'border-transparent text-clinic-muted hover:border-base-300 hover:bg-base-200 hover:text-clinic-ink'
                } ${sidebarCollapsed ? 'justify-center px-0' : 'justify-start'}`}
              >
                <Activity className={`h-4 w-4 shrink-0 ${safeActiveView === 'automation' ? 'text-primary-content' : 'text-secondary'}`} />
                {!sidebarCollapsed && <span className="truncate">Automatizacion</span>}
              </button>
            </section>
          )}

          {!sidebarCollapsed && (
            <div className="rounded-lg border border-base-300 bg-base-200 p-3 text-xs leading-5 text-clinic-muted">
              Selecciona un indicador para actualizar las vistas de busqueda, tablero y carga de datos.
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
        className="fixed right-0 top-0 z-40 border-b border-primary/30 bg-primary text-primary-content shadow-soft transition-[left,height] duration-200"
        style={{ left: contentOffset }}
      >
        <div
          className={`mx-auto flex max-w-[92rem] flex-col justify-center gap-2 px-3 sm:px-6 lg:flex-row lg:items-center lg:justify-between ${
            headerCompact ? 'min-h-[4.5rem] py-2 lg:min-h-[4.75rem]' : 'min-h-[6.5rem] py-2 lg:min-h-[6.5rem] lg:py-3'
          }`}
        >
          <div className="min-w-0 max-w-4xl">
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setSidebarCollapsed(false)}
                className="btn btn-square btn-ghost h-10 min-h-10 w-10 shrink-0 rounded-xl border border-primary-content/20 bg-primary-content/10 text-primary-content hover:bg-primary-content/15 lg:hidden"
                aria-label="Abrir menu lateral"
              >
                <Menu className="h-5 w-5" />
              </button>
              <span className={`hidden w-1 rounded-full bg-secondary transition-all sm:block ${headerCompact ? 'h-8' : 'h-11'}`} />
              <div className="min-w-0">
                {!headerCompact && (
                  <p className="hidden text-xs font-bold uppercase tracking-[0.12em] text-primary-content/68 sm:block">Plataforma de indicadores</p>
                )}
                <h1 className={`truncate font-bold leading-tight text-primary-content transition-all ${headerCompact ? 'text-lg sm:text-xl' : 'text-xl sm:text-2xl'}`}>
                  {activeIndicator.title}
                </h1>
                {!headerCompact && <p className="mt-1 hidden max-w-3xl text-sm leading-5 text-primary-content/76 sm:block">{activeIndicator.description}</p>}
              </div>
            </div>
          </div>

          <div
            className={`mr-0 flex max-w-full shrink-0 flex-wrap items-center gap-y-1 rounded-xl border border-primary-content/15 bg-primary-content/10 transition-all lg:mr-4 lg:justify-end ${
              headerCompact ? 'px-3 py-1.5' : 'px-4 py-2'
            } ${headerCompact ? 'hidden sm:flex' : 'flex'}`}
          >
            <TopbarChip icon={Activity} label="Ambito" value={activeScopeLabel} />
            <TopbarChip icon={UserCheck} label={user.role_label} value={user.display_name} />
            {user.auth_enabled && (
              <TopbarChip
                as="button"
                type="button"
                onClick={handleLogout}
                className="ml-2 rounded-md border border-primary-content/25 px-3 hover:bg-primary-content/15"
              >
                <LogOut className="h-4 w-4 text-primary-content/75" />
                <span className="hidden font-bold text-primary-content sm:inline">Salir</span>
              </TopbarChip>
            )}
          </div>
        </div>
      </header>

      <div className="transition-[padding-left] duration-200" style={{ paddingLeft: contentOffset }}>
        <main
          className={`mx-auto min-w-0 max-w-[92rem] animate-fade-in px-3 pb-8 transition-[padding-top] duration-200 sm:px-6 ${
            headerCompact ? 'pt-20 lg:pt-24' : 'pt-28 lg:pt-32'
          }`}
        >
          <nav
            role="tablist"
            className="sticky z-30 mb-4 flex gap-1 overflow-x-auto rounded-xl border border-base-300 bg-base-100/95 p-1.5 shadow-soft backdrop-blur sm:p-2"
            style={{ top: navStickyTop }}
            aria-label="Modulos principales"
          >
            {showModuleTab('search') && (
              <ModuleTab active={safeActiveView === 'search'} icon={Search} onClick={() => handleViewChange('search')}>
                Busqueda DNI
              </ModuleTab>
            )}
            {showModuleTab('dashboard') && (
              <ModuleTab active={safeActiveView === 'dashboard'} icon={BarChart3} onClick={() => handleViewChange('dashboard')}>
                Dashboard
              </ModuleTab>
            )}
            {showModuleTab('config') && (
              <ModuleTab active={safeActiveView === 'config'} icon={SlidersHorizontal} onClick={() => handleViewChange('config')}>
                Configuracion
              </ModuleTab>
            )}
            {showModuleTab('data') && (
              <ModuleTab active={safeActiveView === 'data'} icon={DatabaseZap} onClick={() => handleViewChange('data')}>
                Carga datos
              </ModuleTab>
            )}
            {showModuleTab('users') && (
              <ModuleTab active={safeActiveView === 'users'} icon={UsersRound} onClick={() => handleViewChange('users')}>
                Usuarios
              </ModuleTab>
            )}
          </nav>

          <PageHeader
            icon={CurrentIcon}
            title={currentView.title}
            description={currentView.description}
          />
          {safeActiveView === 'search' && (
            <SearchDNI
              selectedProvince={selectedProvince}
              selectedIndicator={selectedIndicator}
              selectedSi02Subindicator={selectedSi02Subindicator}
            />
          )}
          {safeActiveView === 'dashboard' && (
            <Dashboard
              selectedProvince={selectedProvince}
              targetCoverage={targetCoverage}
              selectedIndicator={selectedIndicator}
              selectedSi02Subindicator={selectedSi02Subindicator}
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
          {safeActiveView === 'automation' && <AutomationView />}
          {safeActiveView === 'users' && <SecurityUsers />}
          <PlatformFooter />
        </main>
      </div>
    </div>
  );
}

export default App;
