import { useEffect, useMemo, useState } from 'react';
import { CheckCircle2, Fingerprint, KeyRound, Loader2, RefreshCcw, Save, ShieldCheck, ToggleLeft, ToggleRight, UserCheck, UserPlus, UserX, UsersRound } from 'lucide-react';
import api from '../api/client';
import SectionPanel from '../components/SectionPanel';

const emptyForm = {
  username: '',
  display_name: '',
  password: '',
  role: 'clinical',
  is_active: true,
};

const roleCardStyles = [
  'border-base-300 border-l-primary',
  'border-base-300 border-l-secondary',
  'border-base-300 border-l-accent',
];

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

function SecurityStatCard({ icon: Icon, label, value, description, className }) {
  return (
    <div className={`stat rounded-xl border border-base-300 bg-base-100 p-4 shadow-sm ${className}`}>
      <div className="flex items-center justify-between gap-3">
        <span className="text-xs font-bold uppercase tracking-[0.16em] opacity-75">{label}</span>
        <Icon className="h-5 w-5 opacity-80" />
      </div>
      <p className="mt-3 text-2xl font-bold">{value}</p>
      <p className="mt-1 text-xs font-semibold opacity-80">{description}</p>
    </div>
  );
}

function RoleCard({ role, index }) {
  return (
    <article className={`card rounded-xl border border-l-4 bg-base-100 p-4 shadow-sm ${roleCardStyles[index % roleCardStyles.length]}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <h4 className="font-bold text-clinic-ink">{role.label}</h4>
          <p className="mt-1 text-xs font-semibold uppercase tracking-[0.16em] text-clinic-muted">{role.code}</p>
        </div>
        <CheckCircle2 className="h-5 w-5 text-secondary" />
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        {role.permissions.map((permission) => (
          <span key={permission} className="badge badge-ghost h-auto border-base-300 px-2.5 py-1 text-xs font-bold text-clinic-ink">
            {permission}
          </span>
        ))}
      </div>
    </article>
  );
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
  const activeUsers = users.filter((user) => user.is_active).length;
  const inactiveUsers = users.length - activeUsers;
  const uniquePermissions = new Set(roles.flatMap((role) => role.permissions ?? [])).size;

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
      <SectionPanel className="overflow-hidden">
        <div className="grid lg:grid-cols-[1.05fr_0.95fr]">
          <div className="bg-primary p-5 text-primary-content lg:p-6">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="flex items-start gap-3">
                <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-white/15 text-primary-content ring-1 ring-white/20">
                  <ShieldCheck className="h-5 w-5" />
                </span>
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.18em] text-primary-content/70">Seguridad de plataforma</p>
                  <h3 className="mt-1 text-2xl font-black">Control de accesos</h3>
                  <p className="mt-2 max-w-2xl text-sm font-semibold leading-6 text-primary-content/80">
                    Roles operativos para busqueda, tablero, carga, configuracion y administracion.
                  </p>
                </div>
              </div>
              <button type="button" onClick={loadSecurity} disabled={busy} className="btn btn-sm bg-base-100 text-primary shadow-sm hover:bg-base-200 disabled:opacity-60">
                {status === 'loading' ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCcw className="h-4 w-4" />}
                Actualizar
              </button>
            </div>
          </div>

          <div className="grid gap-3 bg-base-200 p-4 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
            <SecurityStatCard
              icon={UserCheck}
              label="Activos"
              value={activeUsers}
              description="Cuentas habilitadas"
              className="border-base-300 text-success"
            />
            <SecurityStatCard
              icon={UserX}
              label="Inactivos"
              value={inactiveUsers}
              description="Cuentas suspendidas"
              className="border-base-300 text-error"
            />
            <SecurityStatCard
              icon={Fingerprint}
              label="Permisos"
              value={uniquePermissions}
              description={`${roles.length} roles definidos`}
              className="border-base-300 text-secondary"
            />
          </div>
        </div>

        <div className="p-5 lg:p-6">
          {error && <div className="alert alert-error rounded-lg py-3 text-sm font-semibold">{error}</div>}
          {message && <div className="alert alert-success rounded-lg py-3 text-sm font-semibold">{message}</div>}

          <div className="mt-5 grid gap-3 lg:grid-cols-3">
            {roles.map((role, index) => (
              <RoleCard key={role.code} role={role} index={index} />
            ))}
          </div>
        </div>
      </SectionPanel>

      <section className="grid gap-5 lg:grid-cols-[0.9fr_1.4fr]">
        <SectionPanel as="form" onSubmit={handleCreate} className="overflow-hidden">
          <div className="border-b border-base-300 bg-base-200 p-5 lg:p-6">
            <div className="flex items-center gap-3">
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-base-100 text-secondary ring-1 ring-secondary/20">
                <UserPlus className="h-5 w-5" />
              </span>
              <div>
                <h3 className="text-xl font-bold text-clinic-ink">Nuevo usuario</h3>
                <p className="text-sm font-semibold text-clinic-muted">Alta controlada con rol y estado inicial.</p>
              </div>
            </div>
          </div>

          <div className="p-5 lg:p-6">
            <label className="block">
              <span className="text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">Usuario</span>
              <input className="input input-bordered mt-1 w-full" value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} required />
            </label>

            <label className="mt-4 block">
              <span className="text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">Nombre visible</span>
              <input className="input input-bordered mt-1 w-full" value={form.display_name} onChange={(event) => setForm({ ...form, display_name: event.target.value })} required />
            </label>

            <label className="mt-4 block">
              <span className="text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">Contrasena temporal</span>
              <input
                type="password"
                className="input input-bordered mt-1 w-full"
                value={form.password}
                onChange={(event) => setForm({ ...form, password: event.target.value })}
                minLength={6}
                required
              />
            </label>

            <label className="mt-4 block">
              <span className="text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">Rol</span>
              <select className="select select-bordered mt-1 w-full" value={form.role} onChange={(event) => setForm({ ...form, role: event.target.value })}>
                {roles.map((role) => (
                  <option key={role.code} value={role.code}>
                    {role.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="mt-4 flex items-center gap-3 rounded-lg border border-base-300 bg-base-200 p-3 text-sm font-bold text-clinic-ink">
              <input className="checkbox checkbox-primary" type="checkbox" checked={form.is_active} onChange={(event) => setForm({ ...form, is_active: event.target.checked })} />
              Usuario activo al crear
            </label>

            <button type="submit" disabled={busy} className="btn btn-primary mt-6 w-full text-primary-content disabled:opacity-50">
              {status === 'saving' ? <Loader2 className="h-4 w-4 animate-spin" /> : <UserPlus className="h-4 w-4" />}
              Crear usuario
            </button>
          </div>
        </SectionPanel>

        <SectionPanel className="overflow-hidden">
          <div className="border-b border-base-300 bg-base-200 p-5 lg:p-6">
            <div className="flex items-center gap-3">
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-base-100 text-secondary ring-1 ring-secondary/20">
                <UsersRound className="h-5 w-5" />
              </span>
              <div>
                <h3 className="text-xl font-bold text-clinic-ink">Usuarios registrados</h3>
                <p className="text-sm text-clinic-muted">{users.length} cuentas disponibles</p>
              </div>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="table table-zebra table-sm min-w-full text-left text-sm">
              <thead className="bg-base-200 text-xs uppercase tracking-[0.16em] text-primary">
                <tr>
                  <th className="px-5 py-3">Usuario</th>
                  <th className="px-5 py-3">Rol</th>
                  <th className="px-5 py-3">Estado</th>
                  <th className="px-5 py-3">Ultimo acceso</th>
                  <th className="px-5 py-3">Contrasena</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.username} className="align-top transition hover:bg-base-200">
                    <td className="px-5 py-4">
                      <p className="font-bold text-clinic-ink">{user.display_name}</p>
                      <p className="mt-1 text-xs font-semibold text-clinic-muted">{user.username}</p>
                    </td>
                    <td className="px-5 py-4">
                      <select
                        className="select select-bordered select-sm min-w-44"
                        value={user.role}
                        onChange={(event) => patchUser(user.username, { role: event.target.value }, 'Rol actualizado.')}
                      >
                        {roles.map((role) => (
                          <option key={role.code} value={role.code}>
                            {role.label}
                          </option>
                        ))}
                      </select>
                      <p className="mt-2 max-w-xs text-xs leading-5 text-clinic-muted">{roleByCode[user.role]?.permissions?.join(', ')}</p>
                    </td>
                    <td className="px-5 py-4">
                      <button
                        type="button"
                        onClick={() => patchUser(user.username, { is_active: !user.is_active }, user.is_active ? 'Usuario desactivado.' : 'Usuario activado.')}
                        className={`btn btn-outline btn-sm ${user.is_active ? 'btn-success' : 'btn-error'}`}
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
                          className="input input-bordered input-sm"
                          placeholder="Nueva contrasena"
                          value={passwords[user.username] || ''}
                          onChange={(event) => setPasswords((current) => ({ ...current, [user.username]: event.target.value }))}
                        />
                        <button
                          type="button"
                          onClick={() => handlePasswordChange(user.username)}
                          disabled={busy || !(passwords[user.username] || '').trim()}
                          className="btn btn-outline btn-secondary btn-sm disabled:opacity-50"
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
        </SectionPanel>
      </section>
    </div>
  );
}

export default SecurityUsers;
