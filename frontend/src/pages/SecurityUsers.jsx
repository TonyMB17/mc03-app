import { useEffect, useMemo, useState } from 'react';
import { CheckCircle2, KeyRound, Loader2, Save, ShieldCheck, ToggleLeft, ToggleRight, UserPlus, UsersRound } from 'lucide-react';
import api from '../api/client';

const emptyForm = {
  username: '',
  display_name: '',
  password: '',
  role: 'clinical',
  is_active: true,
};

function formatDate(value) {
  if (!value) return 'Sin registro';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Sin registro';
  return new Intl.DateTimeFormat('es-PE', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

function SecurityUsers() {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [passwords, setPasswords] = useState({});
  const [status, setStatus] = useState('loading');
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const roleByCode = useMemo(() => Object.fromEntries(roles.map((role) => [role.code, role])), [roles]);

  const loadSecurity = async () => {
    setStatus('loading');
    setError(null);
    try {
      const [rolesResponse, usersResponse] = await Promise.all([
        api.get('/api/security/roles'),
        api.get('/api/security/users'),
      ]);
      setRoles(rolesResponse.data.roles || []);
      setUsers(usersResponse.data.users || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo cargar la configuracion de seguridad');
    } finally {
      setStatus('idle');
    }
  };

  useEffect(() => {
    loadSecurity();
  }, []);

  const handleCreate = async (event) => {
    event.preventDefault();
    setStatus('saving');
    setError(null);
    setMessage(null);
    try {
      await api.post('/api/security/users', {
        ...form,
        username: form.username.trim(),
        display_name: form.display_name.trim(),
      });
      setForm(emptyForm);
      setMessage('Usuario creado correctamente.');
      await loadSecurity();
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo crear el usuario');
      setStatus('idle');
    }
  };

  const patchUser = async (username, payload, successMessage) => {
    setStatus('saving');
    setError(null);
    setMessage(null);
    try {
      await api.patch(`/api/security/users/${encodeURIComponent(username)}`, payload);
      setMessage(successMessage);
      await loadSecurity();
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo actualizar el usuario');
      setStatus('idle');
    }
  };

  const handlePasswordChange = async (username) => {
    const password = (passwords[username] || '').trim();
    if (!password) return;
    await patchUser(username, { password }, 'Contrasena actualizada.');
    setPasswords((current) => ({ ...current, [username]: '' }));
  };

  const busy = status === 'loading' || status === 'saving';

  return (
    <div className="space-y-5">
      <section className="panel p-5 lg:p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-clinic-mint text-clinic-teal">
                <ShieldCheck className="h-5 w-5" />
              </span>
              <div>
                <h3 className="text-xl font-bold text-clinic-ink">Control de accesos</h3>
                <p className="text-sm text-clinic-muted">Roles operativos para busqueda, tablero, carga y administracion.</p>
              </div>
            </div>
          </div>
          <button type="button" onClick={loadSecurity} disabled={busy} className="icon-button btn-secondary">
            {status === 'loading' ? <Loader2 className="h-4 w-4 animate-spin" /> : <UsersRound className="h-4 w-4" />}
            Actualizar
          </button>
        </div>

        {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</div>}
        {message && <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm font-semibold text-emerald-700">{message}</div>}

        <div className="mt-5 grid gap-3 lg:grid-cols-3">
          {roles.map((role) => (
            <article key={role.code} className="inner-panel p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h4 className="font-bold text-clinic-ink">{role.label}</h4>
                  <p className="mt-1 text-xs font-semibold uppercase tracking-[0.16em] text-clinic-muted">{role.code}</p>
                </div>
                <CheckCircle2 className="h-5 w-5 text-clinic-teal" />
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                {role.permissions.map((permission) => (
                  <span key={permission} className="rounded-full border border-clinic-border bg-clinic-rose px-2.5 py-1 text-xs font-bold text-clinic-teal">
                    {permission}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-5 lg:grid-cols-[0.9fr_1.4fr]">
        <form onSubmit={handleCreate} className="panel p-5 lg:p-6">
          <div className="flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-clinic-lilac text-clinic-violet">
              <UserPlus className="h-5 w-5" />
            </span>
            <h3 className="text-xl font-bold text-clinic-ink">Nuevo usuario</h3>
          </div>

          <label className="mt-5 block">
            <span className="text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">Usuario</span>
            <input className="field" value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} required />
          </label>

          <label className="mt-4 block">
            <span className="text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">Nombre visible</span>
            <input className="field" value={form.display_name} onChange={(event) => setForm({ ...form, display_name: event.target.value })} required />
          </label>

          <label className="mt-4 block">
            <span className="text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">Contrasena temporal</span>
            <input
              type="password"
              className="field"
              value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })}
              minLength={6}
              required
            />
          </label>

          <label className="mt-4 block">
            <span className="text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">Rol</span>
            <select className="field" value={form.role} onChange={(event) => setForm({ ...form, role: event.target.value })}>
              {roles.map((role) => (
                <option key={role.code} value={role.code}>
                  {role.label}
                </option>
              ))}
            </select>
          </label>

          <label className="mt-4 flex items-center gap-3 text-sm font-bold text-clinic-ink">
            <input type="checkbox" checked={form.is_active} onChange={(event) => setForm({ ...form, is_active: event.target.checked })} />
            Usuario activo
          </label>

          <button type="submit" disabled={busy} className="icon-button btn-primary mt-6 w-full disabled:opacity-50">
            {status === 'saving' ? <Loader2 className="h-4 w-4 animate-spin" /> : <UserPlus className="h-4 w-4" />}
            Crear usuario
          </button>
        </form>

        <section className="panel overflow-hidden">
          <div className="border-b border-clinic-border p-5 lg:p-6">
            <div className="flex items-center gap-3">
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-clinic-mint text-clinic-teal">
                <UsersRound className="h-5 w-5" />
              </span>
              <div>
                <h3 className="text-xl font-bold text-clinic-ink">Usuarios registrados</h3>
                <p className="text-sm text-clinic-muted">{users.length} cuentas disponibles</p>
              </div>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-clinic-border text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-[0.16em] text-clinic-muted">
                <tr>
                  <th className="px-5 py-3">Usuario</th>
                  <th className="px-5 py-3">Rol</th>
                  <th className="px-5 py-3">Estado</th>
                  <th className="px-5 py-3">Ultimo acceso</th>
                  <th className="px-5 py-3">Contrasena</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-clinic-border bg-white">
                {users.map((user) => (
                  <tr key={user.username} className="align-top">
                    <td className="px-5 py-4">
                      <p className="font-bold text-clinic-ink">{user.display_name}</p>
                      <p className="mt-1 text-xs font-semibold text-clinic-muted">{user.username}</p>
                    </td>
                    <td className="px-5 py-4">
                      <select
                        className="field m-0 min-w-44 py-2"
                        value={user.role}
                        onChange={(event) => patchUser(user.username, { role: event.target.value }, 'Rol actualizado.')}
                      >
                        {roles.map((role) => (
                          <option key={role.code} value={role.code}>
                            {role.label}
                          </option>
                        ))}
                      </select>
                      <p className="mt-2 text-xs text-clinic-muted">{roleByCode[user.role]?.permissions?.join(', ')}</p>
                    </td>
                    <td className="px-5 py-4">
                      <button
                        type="button"
                        onClick={() => patchUser(user.username, { is_active: !user.is_active }, user.is_active ? 'Usuario desactivado.' : 'Usuario activado.')}
                        className={`icon-button ${user.is_active ? 'btn-secondary text-clinic-teal' : 'border border-red-200 bg-red-50 text-red-700'}`}
                      >
                        {user.is_active ? <ToggleRight className="h-4 w-4" /> : <ToggleLeft className="h-4 w-4" />}
                        {user.is_active ? 'Activo' : 'Inactivo'}
                      </button>
                    </td>
                    <td className="px-5 py-4 text-clinic-muted">{formatDate(user.last_login_at)}</td>
                    <td className="px-5 py-4">
                      <div className="flex min-w-64 gap-2">
                        <input
                          type="password"
                          className="field m-0 py-2"
                          placeholder="Nueva contrasena"
                          value={passwords[user.username] || ''}
                          onChange={(event) => setPasswords((current) => ({ ...current, [user.username]: event.target.value }))}
                        />
                        <button
                          type="button"
                          onClick={() => handlePasswordChange(user.username)}
                          disabled={busy || !(passwords[user.username] || '').trim()}
                          className="icon-button btn-secondary disabled:opacity-50"
                          title="Actualizar contrasena"
                        >
                          <KeyRound className="h-4 w-4" />
                          <Save className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {!users.length && status !== 'loading' && (
                  <tr>
                    <td className="px-5 py-8 text-center text-clinic-muted" colSpan={5}>
                      No hay usuarios registrados.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </section>
    </div>
  );
}

export default SecurityUsers;
