import { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import {
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  Download,
  FileSpreadsheet,
  Hospital,
  Loader2,
  Target,
  TrendingUp,
  UsersRound,
  XCircle,
} from 'lucide-react';

const PAGE_SIZE = 10;

const semaphoreStyles = {
  green: {
    badge: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
    border: 'border-emerald-300',
    dot: 'bg-emerald-500',
    icon: CheckCircle2,
    label: 'Cumple',
  },
  red: {
    badge: 'bg-red-50 text-red-700 ring-red-200',
    border: 'border-red-300',
    dot: 'bg-red-500',
    icon: XCircle,
    label: 'No cumple',
  },
};

function StatusCard({ title, value, icon: Icon, tone = 'lilac' }) {
  const tones = {
    lilac: 'from-clinic-lilac/70 to-white text-clinic-violet',
    pink: 'from-clinic-cream to-white text-amber-700',
    rose: 'from-clinic-mint to-white text-clinic-teal',
    blue: 'from-clinic-mint to-white text-clinic-teal',
  };

  return (
    <div className="panel group p-5 transition duration-200 hover:-translate-y-1 hover:shadow-lift">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">{title}</h3>
          <p className="mt-4 text-3xl font-bold text-clinic-ink">{value}</p>
        </div>
        <span className={`grid h-12 w-12 place-items-center rounded-xl bg-gradient-to-br ${tones[tone]} transition group-hover:scale-105`}>
          <Icon className="h-6 w-6" />
        </span>
      </div>
    </div>
  );
}

function PeriodBadge({ inVerificationPeriod }) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold uppercase tracking-[0.12em] ${
      inVerificationPeriod ? 'bg-clinic-mint text-clinic-teal ring-1 ring-teal-100' : 'bg-slate-100 text-clinic-muted ring-1 ring-slate-200'
    }`}>
      <CalendarDays className="h-3.5 w-3.5" />
      {inVerificationPeriod ? 'Verificacion' : 'Historico'}
    </span>
  );
}

function SemaphoreBadge({ value }) {
  const style = semaphoreStyles[value] ?? semaphoreStyles.red;
  const Icon = style.icon;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-bold ring-1 ${style.badge}`}>
      <Icon className="h-4 w-4" />
      {style.label}
    </span>
  );
}

function buildMonthKey(item) {
  const monthNumber = {
    enero: 1,
    febrero: 2,
    marzo: 3,
    abril: 4,
    mayo: 5,
    junio: 6,
    julio: 7,
    agosto: 8,
    setiembre: 9,
    octubre: 10,
    noviembre: 11,
  }[item.month];
  return `${item.year}_${monthNumber}`;
}

function MiniMonthCard({ item }) {
  const style = semaphoreStyles[item.semaphore] ?? semaphoreStyles.red;
  return (
    <div className={`inner-panel border-l-4 ${style.border} p-4 transition hover:-translate-y-0.5 hover:shadow-soft`}>
      <div className="flex items-center justify-between gap-3">
        <p className="font-bold capitalize text-clinic-ink">{item.month}</p>
        <span className={`h-2.5 w-2.5 rounded-full ${style.dot}`} aria-hidden="true" />
      </div>
      <p className="mt-3 text-2xl font-bold text-clinic-ink">{item.coverage}%</p>
      <p className="text-sm text-clinic-muted">{item.numerator} de {item.denominator}</p>
      <div className="mt-3">
        <SemaphoreBadge value={item.semaphore} />
      </div>
    </div>
  );
}

function Dashboard({ selectedProvince, targetCoverage }) {
  const [status, setStatus] = useState('cargando...');
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState('');
  const [page, setPage] = useState(1);

  useEffect(() => {
    setError(null);
    setStatus('cargando...');
    const params = new URLSearchParams({ province: selectedProvince, target: targetCoverage });
    axios
      .get(`/api/report/summary?${params.toString()}`)
      .then((response) => {
        setSummary(response.data);
        setStatus('Conectado');
      })
      .catch((err) => {
        setStatus('Error');
        setError(err.message);
      });
  }, [selectedProvince, targetCoverage]);

  useEffect(() => {
    if (!summary?.monthly?.length) return;

    const cutoffMonthKey = summary.cut_off_date
      ? `${new Date(summary.cut_off_date).getUTCFullYear()}_${new Date(summary.cut_off_date).getUTCMonth() + 1}`
      : '';
    const availableCutoffMonth = summary.monthly.find((item) => buildMonthKey(item) === cutoffMonthKey);
    const fallbackMonth = [...summary.monthly].reverse().find((item) => item.denominator > 0) ?? summary.monthly[0];
    setSelectedMonth(buildMonthKey(availableCutoffMonth ?? fallbackMonth));
    setPage(1);
  }, [summary]);

  const incumplidosCount = summary?.omisos?.length ?? 0;
  const historicalMonths = summary?.monthly?.filter((item) => !item.in_verification_period) ?? [];
  const verificationMonths = summary?.monthly?.filter((item) => item.in_verification_period) ?? [];
  const activeTarget = summary?.target_coverage ?? targetCoverage;

  const selectedMonthItem = summary?.monthly?.find((item) => buildMonthKey(item) === selectedMonth);
  const selectedMonthLabel = selectedMonthItem ? `${selectedMonthItem.month} ${selectedMonthItem.year}` : 'mes seleccionado';

  const monthIncumplidos = useMemo(
    () => summary?.omisos?.filter((item) => item.Mes_eva === selectedMonth) ?? [],
    [summary, selectedMonth],
  );

  const totalPages = Math.max(1, Math.ceil(monthIncumplidos.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const paginatedIncumplidos = monthIncumplidos.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);
  const displayStart = monthIncumplidos.length === 0 ? 0 : (safePage - 1) * PAGE_SIZE + 1;
  const displayEnd = Math.min(safePage * PAGE_SIZE, monthIncumplidos.length);
  const downloadParams = new URLSearchParams({ province: selectedProvince, month: selectedMonth });

  const handleMonthChange = (event) => {
    setSelectedMonth(event.target.value);
    setPage(1);
  };

  return (
    <section className="space-y-6">
      <section className="grid gap-4 md:grid-cols-4">
        <StatusCard title="Estado API" value={summary ? 'Conectado' : status} icon={summary ? CheckCircle2 : Loader2} tone="blue" />
        <StatusCard title="Meta" value={`${activeTarget}%`} icon={Target} tone="lilac" />
        <StatusCard title="Meses cumplidos" value={summary ? `${summary.months_met}/${summary.months_evaluated}` : '-'} icon={TrendingUp} tone="pink" />
        <StatusCard title="Incumplidos total" value={summary ? incumplidosCount : '-'} icon={UsersRound} tone="rose" />
      </section>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
          No se pudo conectar con el backend: {error}
        </div>
      )}

      <section className="panel p-5 lg:p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-2xl font-bold text-clinic-ink">Avance del indicador</h2>
            <p className="mt-1 text-sm text-clinic-muted">
              {summary?.committed ? 'Compromiso cumplido' : 'Compromiso pendiente'} segun meta de {activeTarget}% y regla 5 de 6 meses.
            </p>
          </div>
          <span className="inline-flex items-center gap-2 rounded-full border border-clinic-violet/15 bg-white/70 px-4 py-2 text-sm font-semibold text-clinic-muted">
            <CalendarDays className="h-4 w-4 text-clinic-violet" />
            {summary?.cut_off_date
              ? `Corte: ${new Date(summary.cut_off_date).toLocaleDateString('es-PE', { year: 'numeric', month: 'long', day: 'numeric' })}`
              : 'Periodo oficial: Junio - Noviembre 2026'}
          </span>
        </div>

        <div className="mt-5 grid gap-3 text-sm md:grid-cols-2">
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 font-semibold text-emerald-700">
            Cumple: cobertura mayor o igual a {activeTarget}%.
          </div>
          <div className="rounded-xl border border-red-200 bg-red-50 p-3 font-semibold text-red-700">
            No cumple: cobertura menor a {activeTarget}%.
          </div>
        </div>

        <div className="mt-6 overflow-hidden rounded-xl border border-clinic-border bg-white/70">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-clinic-border text-sm">
              <thead className="bg-slate-100">
                <tr className="text-left text-clinic-ink">
                  <th className="px-4 py-3 font-bold">Mes</th>
                  <th className="px-4 py-3 font-bold">Periodo</th>
                  <th className="px-4 py-3 font-bold">Cobertura</th>
                  <th className="px-4 py-3 font-bold">Numerador</th>
                  <th className="px-4 py-3 font-bold">Denominador</th>
                  <th className="px-4 py-3 font-bold">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-clinic-border bg-white">
                {summary?.monthly?.map((item) => (
                  <tr key={`${item.month}-${item.year}`} className={`border-l-4 ${semaphoreStyles[item.semaphore]?.border ?? semaphoreStyles.red.border} text-clinic-muted transition hover:bg-clinic-lilac/10`}>
                    <td className="px-4 py-3 font-bold capitalize text-clinic-ink">{item.month} {item.year}</td>
                    <td className="px-4 py-3"><PeriodBadge inVerificationPeriod={item.in_verification_period} /></td>
                    <td className="px-4 py-3 font-semibold text-clinic-ink">{item.coverage}%</td>
                    <td className="px-4 py-3">{item.numerator}</td>
                    <td className="px-4 py-3">{item.denominator}</td>
                    <td className="px-4 py-3"><SemaphoreBadge value={item.semaphore} /></td>
                  </tr>
                )) ?? (
                  <tr>
                    <td className="px-4 py-4 text-clinic-muted" colSpan="6">Cargando historial mensual...</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <article className="panel p-5 lg:p-6">
          <h2 className="text-2xl font-bold text-clinic-ink">Historial previo</h2>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            {historicalMonths.map((item) => (
              <MiniMonthCard key={`${item.month}-${item.year}`} item={item} />
            ))}
          </div>
        </article>

        <article className="panel p-5 lg:p-6">
          <h2 className="text-2xl font-bold text-clinic-ink">Periodo de verificacion</h2>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            {verificationMonths.map((item) => (
              <MiniMonthCard key={`${item.month}-${item.year}`} item={item} />
            ))}
          </div>
        </article>
      </section>

      <section className="panel p-5 lg:p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h2 className="text-2xl font-bold text-clinic-ink">Incumplidos por mes de evaluacion</h2>
            <p className="mt-1 text-sm text-clinic-muted">
              Mostrando registros incumplidos del mes de evaluacion {selectedMonthLabel}.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <label className="block">
              <span className="text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">Mes evaluacion</span>
              <select value={selectedMonth} onChange={handleMonthChange} className="field min-w-48">
                {summary?.monthly?.map((item) => (
                  <option key={buildMonthKey(item)} value={buildMonthKey(item)}>
                    {item.month} {item.year}
                  </option>
                ))}
              </select>
            </label>
            <a
              href={`/api/report/incumplidos.xlsx?${downloadParams.toString()}`}
              className="icon-button btn-primary"
            >
              <Download className="h-4 w-4" />
              Descargar Excel
            </a>
          </div>
        </div>

        <div className="mt-5 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <span className="inline-flex items-center gap-2 text-sm font-semibold text-clinic-muted">
            <FileSpreadsheet className="h-4 w-4 text-clinic-violet" />
            {monthIncumplidos.length} registros incumplidos
          </span>
          <span className="text-sm font-semibold text-clinic-muted">Pagina {safePage} de {totalPages}</span>
        </div>

        <div className="mt-5 overflow-hidden rounded-xl border border-clinic-border bg-white/70">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-clinic-border text-sm">
              <thead className="bg-slate-100">
                <tr className="text-left text-clinic-ink">
                  <th className="px-4 py-3 font-bold">DNI</th>
                  <th className="px-4 py-3 font-bold">Paciente</th>
                  <th className="px-4 py-3 font-bold">Establecimiento</th>
                  <th className="px-4 py-3 font-bold">Motivo</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-clinic-border bg-white">
                {paginatedIncumplidos.map((item) => (
                  <tr key={`${item.Mes_eva}-${item.afi_DNI}-${item.NumCNV}`} className="text-clinic-muted transition hover:bg-clinic-rose/10">
                    <td className="px-4 py-3 font-semibold text-clinic-ink">{item.afi_DNI || item.NumCNV || '-'}</td>
                    <td className="px-4 py-3">
                      {[item.afi_nombres, item.afi_appaterno, item.afi_apmaterno].filter(Boolean).join(' ') || '-'}
                    </td>
                    <td className="px-4 py-3">
                      <p className="inline-flex items-center gap-2 font-bold text-clinic-ink">
                        <Hospital className="h-4 w-4 text-clinic-violet" />
                        {item.Des_EESS || 'Sin establecimiento'}
                      </p>
                      <p className="mt-1 text-xs text-clinic-muted">
                        {item.Des_MicroRed || '-'} / RENAES {item.pre_CodigoRENAES || '-'}
                      </p>
                    </td>
                    <td className="px-4 py-3">{item.reason}</td>
                  </tr>
                ))}
                {summary && monthIncumplidos.length === 0 && (
                  <tr>
                    <td className="px-4 py-4 text-clinic-muted" colSpan="4">
                      <span className="inline-flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                        No hay incumplidos en el mes seleccionado.
                      </span>
                    </td>
                  </tr>
                )}
                {!summary && (
                  <tr>
                    <td className="px-4 py-4 text-clinic-muted" colSpan="4">
                      <span className="inline-flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin text-clinic-violet" />
                        Cargando incumplidos...
                      </span>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <button
            type="button"
            onClick={() => setPage((current) => Math.max(1, current - 1))}
            disabled={safePage <= 1}
            className="icon-button btn-secondary disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ArrowLeft className="h-4 w-4" />
            Anterior
          </button>
          <div className="text-center text-sm font-semibold text-clinic-muted">
            Registros {displayStart}-{displayEnd} de {monthIncumplidos.length}
          </div>
          <button
            type="button"
            onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
            disabled={safePage >= totalPages}
            className="icon-button btn-secondary disabled:cursor-not-allowed disabled:opacity-40"
          >
            Siguiente
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </section>

      {summary?.committed === false && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700">
          <span className="inline-flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            El compromiso aun no alcanza la regla de cumplimiento configurada para el periodo de verificacion.
          </span>
        </div>
      )}
    </section>
  );
}

export default Dashboard;
