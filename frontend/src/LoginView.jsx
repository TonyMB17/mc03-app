import { useState } from 'react';
import { Activity, DatabaseZap, Loader2, LockKeyhole, ShieldCheck, UserRoundCheck } from 'lucide-react';
import api, { saveAuthUser, setAuthToken } from './api/client';
import usiLogoComplete from './assets/svg/usi-logo-completo.svg';
import usiLogoIcon from './assets/svg/usi-logo-isotipo.svg';

const accessHighlights = [
  { icon: UserRoundCheck, label: 'Acceso por roles', value: 'Clinico, supervisor y administrador' },
  { icon: Activity, label: 'Seguimiento nominal', value: 'Busqueda, alertas y dashboard' },
  // { icon: DatabaseZap, label: 'Datos protegidos', value: 'Cargas versionadas y auditoria' },
];

function BrandPanel() {
  return (
    <aside className="relative hidden overflow-hidden bg-primary p-6 text-primary-content lg:block lg:p-10">
      <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(194,164,207,0.24),transparent_34%),linear-gradient(315deg,rgba(14,165,233,0.24),transparent_42%)]" />
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.06)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.06)_1px,transparent_1px)] bg-[size:32px_32px] opacity-35" />

      <div className="relative flex min-h-full flex-col justify-between gap-10">
        <div>
          <div className="max-w-md">
            <div className="grid h-36 w-36 place-items-center rounded-2xl bg-base-100 p-1 shadow-soft ring-1 ring-white/60 sm:h-52 sm:w-52 lg:h-60 lg:w-60">
              <img src={usiLogoComplete} alt="Unidad de Salud Individual" className="h-full w-full object-contain" />
            </div>
            <h1 className="mt-7 text-3xl font-bold leading-tight sm:text-4xl lg:text-[2.65rem]">
              Sistema de seguimiento de indicadores
            </h1>
            <p className="mt-4 text-sm leading-6 text-white/75">
              Plataforma operativa para monitorear paquetes de salud y alertar incumplimientos por establecimiento.
            </p>
          </div>
        </div>

        <div className="grid gap-3">
          {accessHighlights.map(({ icon: Icon, label, value }) => (
            <div key={label} className="rounded-xl border border-white/20 bg-white/10 p-4 backdrop-blur">
              <div className="flex items-start gap-3">
                <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-white/10 text-white ring-1 ring-white/20">
                  <Icon className="h-5 w-5" />
                </span>
                <div>
                  <p className="text-sm font-bold text-white">{label}</p>
                  <p className="mt-1 text-xs leading-5 text-white/70">{value}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}

function LoginField({ label, ...props }) {
  return (
    <label className="form-control w-full">
      <span className="label px-0 pb-1">
        <span className="label-text text-xs font-bold uppercase tracking-[0.18em] text-base-content/60">{label}</span>
      </span>
      <input className="input input-bordered w-full bg-base-100 font-semibold focus:border-secondary focus:outline-none" {...props} />
    </label>
  );
}

function MobileBrandCard() {
  return (
    <div className="rounded-2xl border border-base-300 bg-base-100 p-4 shadow-soft lg:hidden">
      <div className="flex items-center gap-3">
        <span className="grid h-12 w-12 shrink-0 place-items-center rounded-xl border border-base-300 bg-base-100 p-2 shadow-sm">
          <img src={usiLogoIcon} alt="USI" className="h-full w-full object-contain" />
        </span>
        <div className="min-w-0">
          <p className="text-[0.66rem] font-bold uppercase tracking-[0.14em] text-secondary">Red de Salud Abancay</p>
          <h1 className="mt-1 text-lg font-black leading-tight text-primary">Sistema de seguimiento de indicadores</h1>
        </div>
      </div>
    </div>
  );
}

function LoginView({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatus('loading');
    setError(null);

    try {
      const response = await api.post('/api/auth/login', { username, password });
      setAuthToken(response.data.access_token);
      saveAuthUser(response.data.user);
      onLogin(response.data.user);
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo iniciar sesion');
    } finally {
      setStatus('idle');
    }
  };

  return (
    <div data-theme="usiTheme" className="min-h-screen overflow-y-auto overflow-x-hidden bg-base-200 px-4 py-4 text-base-content sm:px-6 lg:py-8">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-[linear-gradient(120deg,rgba(14,165,233,0.08),transparent_36%),linear-gradient(300deg,rgba(194,164,207,0.16),transparent_42%)]" />

      <div className="mx-auto flex min-h-[calc(100vh-2rem)] w-full max-w-md flex-col justify-center gap-3 lg:grid lg:min-h-[calc(100vh-4rem)] lg:max-w-6xl lg:items-center">
        <MobileBrandCard />
        <section className="card grid overflow-hidden rounded-2xl border border-base-300 bg-base-100 shadow-soft lg:grid-cols-[1.1fr_0.9fr]">
          <BrandPanel />

          <form onSubmit={handleSubmit} className="flex flex-col justify-center p-5 sm:p-7 lg:p-10">
            <div>
              <div className="flex items-center gap-3">
                <span className="hidden h-14 w-14 place-items-center rounded-xl bg-base-100 p-2 text-secondary shadow-sm ring-1 ring-base-300 sm:grid">
                  <img src={usiLogoIcon} alt="" className="h-full w-full object-contain" aria-hidden="true" />
                </span>
                <div>
                  <h2 className="text-xl font-black text-primary sm:text-2xl">Iniciar sesion</h2>
                  <p className="hidden text-sm font-semibold text-base-content/60 sm:block">Ingresa con la cuenta asignada para tu rol.</p>
                </div>
              </div>

              <div className="mt-6 space-y-4 sm:mt-8 sm:space-y-5">
                <LoginField
                  label="Usuario"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  autoComplete="username"
                  required
                />

                <LoginField
                  label="Contrasena"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  autoComplete="current-password"
                  required
                />
              </div>

              {error && (
                <div className="alert alert-error mt-5 rounded-xl p-3 text-sm font-semibold">
                  {error}
                </div>
              )}

              <button type="submit" disabled={status === 'loading'} className="btn btn-primary mt-6 w-full normal-case disabled:opacity-50 sm:mt-7">
                {status === 'loading' ? <Loader2 className="h-4 w-4 animate-spin" /> : <LockKeyhole className="h-4 w-4" />}
                Entrar al sistema
              </button>

              {/* <p className="mt-5 hidden rounded-lg border border-base-300 bg-base-200 px-4 py-3 text-xs font-semibold leading-5 text-base-content/60 sm:block">
                El acceso esta protegido por usuario, rol y permisos. Los cambios de datos quedan asociados al usuario autenticado.
              </p> */}
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}

export default LoginView;
