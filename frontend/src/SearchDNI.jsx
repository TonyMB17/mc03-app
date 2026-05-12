import { useState } from 'react';
import axios from 'axios';
import {
  AlertTriangle,
  Baby,
  CalendarClock,
  CheckCircle2,
  ClipboardList,
  Hospital,
  IdCard,
  Loader2,
  Search,
  ShieldAlert,
  ShieldCheck,
  Syringe,
  TestTube2,
  Timer,
  UserRound,
  XCircle,
} from 'lucide-react';

const statusStyles = {
  cumple: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  advertencia: 'bg-amber-50 text-amber-700 ring-amber-200',
  programado: 'bg-blue-50 text-blue-700 ring-blue-200',
  incumplimiento: 'bg-red-50 text-red-700 ring-red-200',
  pendiente: 'bg-slate-100 text-clinic-muted ring-slate-200',
};

const statusLabels = {
  cumple: 'Cumple',
  advertencia: 'En ventana',
  programado: 'Programado',
  incumplimiento: 'Incumple',
  pendiente: 'Pendiente',
};

const statusIcons = {
  cumple: CheckCircle2,
  advertencia: AlertTriangle,
  programado: CalendarClock,
  incumplimiento: XCircle,
  pendiente: Timer,
};

function StatusPill({ estado = 'pendiente' }) {
  const Icon = statusIcons[estado] ?? statusIcons.pendiente;
  return (
    <span className={`inline-flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1 text-sm font-bold ring-1 ${statusStyles[estado] ?? statusStyles.pendiente}`}>
      <Icon className="h-4 w-4" />
      {statusLabels[estado] ?? statusLabels.pendiente}
    </span>
  );
}

function formatDate(value) {
  if (!value) return '-';
  return new Date(value).toLocaleDateString('es-PE', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function DetailMessage({ item }) {
  return (
    <div className="mt-3 rounded-xl border border-clinic-violet/10 bg-clinic-mint/35 p-3">
      <p className="text-sm leading-6 text-clinic-muted">{item.mensaje}</p>
      <p className="mt-2 inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.14em] text-clinic-muted">
        <Timer className="h-3.5 w-3.5 text-clinic-violet" />
        Ventana: {formatDate(item.fecha_inicio)} - {formatDate(item.fecha_limite)}
      </p>
    </div>
  );
}

function InfoItem({ label, value, icon: Icon }) {
  return (
    <div className="rounded-xl border border-clinic-violet/10 bg-white/62 p-4">
      <p className="inline-flex items-center gap-2 text-sm font-semibold text-clinic-muted">
        <Icon className="h-4 w-4 text-clinic-violet" />
        {label}
      </p>
      <p className="mt-2 font-bold text-clinic-ink">{value || '-'}</p>
    </div>
  );
}

function SectionTitle({ icon: Icon, title }) {
  return (
    <div className="flex items-center gap-3">
      <span className="grid h-10 w-10 place-items-center rounded-xl bg-clinic-mint text-clinic-teal ring-1 ring-teal-100">
        <Icon className="h-5 w-5" />
      </span>
      <h3 className="text-lg font-bold text-clinic-ink">{title}</h3>
    </div>
  );
}

function SearchDNI({ selectedProvince }) {
  const [dni, setDni] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (event) => {
    event.preventDefault();
    if (!dni.trim()) {
      setError('Ingrese un DNI valido');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const params = new URLSearchParams({ province: selectedProvince });
      const response = await axios.get(`/api/search/dni/${dni.trim()}?${params.toString()}`);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error en la busqueda');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel p-5 lg:p-6">
      <form onSubmit={handleSearch} className="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-end">
        <div>
          <label htmlFor="dni" className="text-sm font-bold uppercase tracking-[0.18em] text-clinic-muted">
            DNI del recien nacido
          </label>
          <div className="relative mt-2">
            <IdCard className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-clinic-violet" />
            <input
              id="dni"
              type="text"
              value={dni}
              onChange={(event) => setDni(event.target.value)}
              placeholder="Ej: 12345678"
              className="field pl-12"
            />
          </div>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="icon-button btn-primary px-6 py-3 disabled:opacity-50"
        >
          {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Search className="h-5 w-5" />}
          {loading ? 'Buscando...' : 'Buscar'}
        </button>
      </form>

      {error && (
        <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 font-semibold text-red-700">
          <span className="inline-flex items-center gap-2">
            <ShieldAlert className="h-5 w-5" />
            {error}
          </span>
        </div>
      )}

      {result && (
        <div className="mt-6 animate-slide-up space-y-5">
          <article className="inner-panel p-5">
            <SectionTitle icon={Baby} title="Datos personales" />
            <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <InfoItem icon={IdCard} label="DNI" value={result.personal.afi_DNI} />
              <InfoItem icon={ClipboardList} label="CNV" value={result.personal.NumCNV} />
              <InfoItem
                icon={UserRound}
                label="Nombre"
                value={[result.personal.afi_nombres, result.personal.afi_appaterno, result.personal.afi_apmaterno].filter(Boolean).join(' ')}
              />
              <InfoItem icon={CalendarClock} label="Fecha de nacimiento" value={result.personal.fec_Nac} />
              <InfoItem icon={Timer} label="Peso / EG" value={`${result.personal.peso || '-'} g / ${result.personal.edadGEst || '-'} sem.`} />
              <div className="rounded-xl border border-clinic-violet/10 bg-white/62 p-4">
                <p className="inline-flex items-center gap-2 text-sm font-semibold text-clinic-muted">
                  <Hospital className="h-4 w-4 text-clinic-violet" />
                  Establecimiento
                </p>
                <p className="mt-2 font-bold text-clinic-ink">{result.personal.Des_EESS || 'Sin establecimiento'}</p>
                <p className="mt-1 text-xs text-clinic-muted">
                  {result.personal.Desc_prov || '-'} / {result.personal.Des_MicroRed || '-'} / RENAES {result.personal.pre_CodigoRENAES || '-'}
                </p>
              </div>
            </div>
          </article>

          <article className="inner-panel p-5">
            <SectionTitle icon={Syringe} title="Vacunas" />
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              {['BCG', 'HVB'].map((vacuna) => {
                const data = result.vacunas[vacuna];
                return (
                  <div key={vacuna} className="rounded-xl border border-clinic-violet/10 bg-white/70 p-4 transition hover:-translate-y-0.5 hover:shadow-soft">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="font-bold text-clinic-ink">{vacuna}</p>
                        <p className="text-sm text-clinic-muted">Codigo: {data.codigo}</p>
                        <p className="text-sm text-clinic-muted">Fecha: {data.fecha || '-'}</p>
                        <p className="text-sm text-clinic-muted">Edad: {data.edad_atencion_dias ?? '-'} dias</p>
                      </div>
                      <StatusPill estado={data.estado} />
                    </div>
                    <DetailMessage item={data} />
                  </div>
                );
              })}
            </div>
          </article>

          <article className="inner-panel p-5">
            <SectionTitle icon={ClipboardList} title="Controles CRED" />
            <div className="mt-4 grid gap-4 xl:grid-cols-3">
              {result.cred_controls.map((cred) => (
                <div key={cred.numero} className="rounded-xl border border-clinic-violet/10 bg-white/70 p-4 transition hover:-translate-y-0.5 hover:shadow-soft">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-bold text-clinic-ink">CRED {cred.numero}</p>
                      <p className="mt-2 text-sm text-clinic-muted">Fecha: {cred.fecha || '-'}</p>
                      <p className="text-sm text-clinic-muted">Edad: {cred.edad_atencion_dias ?? '-'} dias</p>
                    </div>
                    <StatusPill estado={cred.estado} />
                  </div>
                  <DetailMessage item={cred} />
                </div>
              ))}
            </div>
          </article>

          <article className="inner-panel p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <SectionTitle icon={TestTube2} title="Tamizaje neonatal" />
                <p className="mt-4 text-sm text-clinic-muted">Fecha: {result.tamizaje.fecha || '-'}</p>
                <p className="text-sm text-clinic-muted">Edad: {result.tamizaje.edad_atencion_dias ?? '-'} dias</p>
              </div>
              <StatusPill estado={result.tamizaje.estado} />
            </div>
            <DetailMessage item={result.tamizaje} />
          </article>

          <article className={`rounded-xl border p-5 ${result.paquete_completo ? 'border-emerald-200 bg-emerald-50' : 'border-red-200 bg-red-50'}`}>
            <h3 className={`inline-flex items-center gap-2 text-lg font-bold ${result.paquete_completo ? 'text-emerald-700' : 'text-red-700'}`}>
              {result.paquete_completo ? <ShieldCheck className="h-5 w-5" /> : <ShieldAlert className="h-5 w-5" />}
              Estado del paquete
            </h3>
            <p className={`mt-2 text-sm font-semibold ${result.paquete_completo ? 'text-emerald-700' : 'text-red-700'}`}>
              {result.paquete_completo ? 'Paquete completo' : 'Paquete incompleto, requiere intervencion'}
            </p>
          </article>
        </div>
      )}
    </section>
  );
}

export default SearchDNI;
