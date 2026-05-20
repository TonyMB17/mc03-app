import { useState } from 'react';
import { Activity, DatabaseZap, Loader2, LockKeyhole, ShieldCheck, UserRoundCheck } from 'lucide-react';
import api, { saveAuthUser, setAuthToken } from './api/client';
import usiLogoComplete from './assets/usi-logo-completo.svg';
import usiLogoIcon from './assets/usi-logo-isotipo.svg';

const accessHighlights = [
  { icon: UserRoundCheck, label: 'Acceso por roles', value: 'Clinico, supervisor y administrador' },
  { icon: Activity, label: 'Seguimiento nominal', value: 'Busqueda, alertas y dashboard' },
  { icon: DatabaseZap, label: 'Datos protegidos', value: 'Cargas versionadas y auditoria' },
];

function BrandPanel() {
  return (
    <aside className="relative overflow-hidden bg-gradient-to-br from-clinic-navy via-[#124A68] to-[#0EA5E9] p-6 text-white sm:p-8 lg:p-10">
      <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(194,164,207,0.22),transparent_34%),linear-gradient(315deg,rgba(14,165,233,0.20),transparent_42%)]" />
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.06)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.06)_1px,transparent_1px)] bg-[size:32px_32px] opacity-35" />

      <div className="relative flex min-h-full flex-col justify-between gap-10">
        <div>
          <div className="max-w-md">
            <div className="grid h-44 w-44 place-items-center rounded-2xl bg-white p-1 shadow-soft ring-1 ring-white/60 sm:h-60 sm:w-60">
              <img src={usiLogoComplete} alt="Unidad de Salud Individual" className="h-full w-full object-contain" />
            </div>
            <h1 className="mt-7 text-3xl font-bold leading-tight tracking-[-0.02em] sm:text-4xl lg:text-[2.65rem]">
              Sistema de seguimiento de indicadores
            </h1>
            <p className="mt-4 text-sm leading-6 text-white/75">
              Plataforma operativa para monitorear paquetes de salud, cargar informacion semanal y alertar incumplimientos por establecimiento.
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
    <label className="block">
      <span className="text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">{label}</span>
      <input className="field" {...props} />
    </label>
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
    <div className="min-h-screen overflow-hidden bg-clinic-page px-4 py-6 text-clinic-ink sm:px-6 lg:py-8">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-[linear-gradient(120deg,rgba(14,165,233,0.10),transparent_36%),linear-gradient(300deg,rgba(194,164,207,0.24),transparent_42%)]" />

      <div className="mx-auto grid min-h-[calc(100vh-3rem)] max-w-6xl items-center">
        <section className="grid overflow-hidden rounded-2xl border border-white/70 bg-white/80 shadow-soft ring-1 ring-clinic-border/70 backdrop-blur-xl lg:grid-cols-[1.1fr_0.9fr]">
          <BrandPanel />

          <form onSubmit={handleSubmit} className="flex flex-col justify-center p-6 sm:p-8 lg:p-10">
            <div>
              <div className="flex items-center gap-3">
                <span className="grid h-14 w-14 place-items-center rounded-xl bg-white p-2 text-clinic-teal shadow-sm ring-1 ring-clinic-border">
                  <img src={usiLogoIcon} alt="" className="h-full w-full object-contain" aria-hidden="true" />
                </span>
                <div>
                  <h2 className="text-2xl font-bold text-clinic-ink">Iniciar sesion</h2>
                  <p className="text-sm text-clinic-muted">Ingresa con la cuenta asignada para tu rol.</p>
                </div>
              </div>

              <div className="mt-8 space-y-5">
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
                <div className="mt-5 rounded-lg border border-red-200 bg-red-50 p-3 text-sm font-semibold text-red-700">
                  {error}
                </div>
              )}

              <button type="submit" disabled={status === 'loading'} className="icon-button btn-primary mt-7 w-full disabled:opacity-50">
                {status === 'loading' ? <Loader2 className="h-4 w-4 animate-spin" /> : <LockKeyhole className="h-4 w-4" />}
                Entrar al sistema
              </button>

              <p className="mt-5 rounded-lg border border-clinic-border bg-slate-50 px-4 py-3 text-xs leading-5 text-clinic-muted">
                El acceso esta protegido por usuario, rol y permisos. Los cambios de datos quedan asociados al usuario autenticado.
              </p>
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}

export default LoginView;
