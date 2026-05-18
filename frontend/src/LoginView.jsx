import { useState } from 'react';
import { Loader2, LockKeyhole, ShieldCheck } from 'lucide-react';
import api, { saveAuthUser, setAuthToken } from './api/client';

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
    <div className="min-h-screen bg-clinic-page px-4 py-8 text-clinic-ink sm:px-6">
      <div className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-5xl items-center">
        <section className="grid overflow-hidden rounded-2xl border border-clinic-border bg-white shadow-soft lg:grid-cols-[1fr_0.9fr]">
          <div className="bg-gradient-to-br from-clinic-navy via-[#17485A] to-clinic-teal p-8 text-white lg:p-10">
            <span className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-clinic-mint text-clinic-navy">
              <ShieldCheck className="h-6 w-6" />
            </span>
            <h1 className="mt-6 text-3xl font-bold">Sistema de seguimiento</h1>
            <p className="mt-3 max-w-md text-sm leading-6 text-white/75">
              Acceso por roles para busqueda clinica, dashboard supervisor y administracion de cargas.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="p-6 lg:p-8">
            <div className="flex items-center gap-3">
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-clinic-mint text-clinic-teal">
                <LockKeyhole className="h-5 w-5" />
              </span>
              <div>
                <h2 className="text-2xl font-bold text-clinic-ink">Iniciar sesion</h2>
                <p className="text-sm text-clinic-muted">Usa las credenciales configuradas por administracion.</p>
              </div>
            </div>

            <label className="mt-6 block">
              <span className="text-sm font-bold uppercase tracking-[0.18em] text-clinic-muted">Usuario</span>
              <input
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                className="field"
                autoComplete="username"
                required
              />
            </label>

            <label className="mt-4 block">
              <span className="text-sm font-bold uppercase tracking-[0.18em] text-clinic-muted">Contrasena</span>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="field"
                autoComplete="current-password"
                required
              />
            </label>

            {error && (
              <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm font-semibold text-red-700">
                {error}
              </div>
            )}

            <button type="submit" disabled={status === 'loading'} className="icon-button btn-primary mt-6 w-full disabled:opacity-50">
              {status === 'loading' ? <Loader2 className="h-4 w-4 animate-spin" /> : <LockKeyhole className="h-4 w-4" />}
              Entrar
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}

export default LoginView;
