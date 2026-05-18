import { useEffect, useMemo, useState } from 'react';
import api from './api/client';
import {
  AlertCircle,
  AlertTriangle,
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
import MetricCard from './components/MetricCard';
import { formatShortDate } from './utils/dates';

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

function PeriodBadge({ inVerificationPeriod, isCurrentEvaluationMonth = false, isMc02 = false }) {
  if (isCurrentEvaluationMonth) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-3 py-1 text-xs font-bold uppercase tracking-[0.12em] text-amber-800 ring-1 ring-amber-200">
        <CalendarDays className="h-3.5 w-3.5" />
        {isMc02 ? 'Cohorte en evaluacion' : 'Mes en evaluacion'}
      </span>
    );
  }

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
    diciembre: 12,
  }[item.month];
  return `${item.year}_${monthNumber}`;
}

function buildMonthOrder(item) {
  const [year, month] = buildMonthKey(item).split('_').map(Number);
  return year * 12 + month;
}

function formatDate(value) {
  return formatShortDate(value);
}

function splitSemicolonList(value) {
  return String(value || '')
    .split(';')
    .map((item) => item.trim())
    .filter(Boolean);
}

function ObservedComponentsCell({ item }) {
  const components = splitSemicolonList(item.components_observed || item.component);

  return (
    <div className="flex w-56 flex-col items-start gap-1.5">
      {components.length > 0 ? (
        <>
          {components.map((component, index) => (
            <span
              key={`${component}-${index}`}
              className="max-w-full rounded-full bg-clinic-mint px-2.5 py-1 text-xs font-bold leading-4 text-clinic-teal ring-1 ring-teal-100"
            >
              {component}
            </span>
          ))}
        </>
      ) : (
        <p className="font-bold text-clinic-ink">-</p>
      )}
    </div>
  );
}

function Dashboard({ selectedProvince, targetCoverage, selectedIndicator }) {
  const [status, setStatus] = useState('cargando...');
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  const [downloadError, setDownloadError] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState('');
  const [page, setPage] = useState(1);
  const isMc02 = selectedIndicator === 'mc02';
  const periodLabel = isMc02 ? 'cohorte' : 'mes de evaluacion';
  const periodLabelTitle = isMc02 ? 'Cohorte' : 'Mes';
  const currentPeriodTitle = isMc02 ? 'Cohorte en evaluacion' : 'Mes en evaluacion';
  const incumplidosTitle = isMc02 ? 'Incumplidos por cohorte de nacimiento' : 'Incumplidos por mes de evaluacion';

  useEffect(() => {
    setError(null);
    setStatus('cargando...');
    const params = new URLSearchParams({ province: selectedProvince, target: targetCoverage, indicator: selectedIndicator });
    api
      .get(`/api/report/summary?${params.toString()}`)
      .then((response) => {
        setSummary(response.data);
        setStatus('Conectado');
      })
      .catch((err) => {
        setStatus('Error');
        setError(err.message);
      });
  }, [selectedProvince, targetCoverage, selectedIndicator]);

  useEffect(() => {
    if (!summary?.monthly?.length) return;

    const monthsWithData = summary.monthly.filter((item) => item.denominator > 0);
    const cutoffMonthKey = summary.cut_off_date
      ? `${new Date(summary.cut_off_date).getUTCFullYear()}_${new Date(summary.cut_off_date).getUTCMonth() + 1}`
      : '';
    const availableCutoffMonth = monthsWithData.find((item) => buildMonthKey(item) === cutoffMonthKey);
    const fallbackMonth = [...monthsWithData].reverse()[0] ?? summary.monthly[0];
    setSelectedMonth(buildMonthKey(availableCutoffMonth ?? fallbackMonth));
    setPage(1);
  }, [summary]);

  const incumplidosCount = summary?.omisos?.length ?? 0;
  const monthsWithData = summary?.monthly?.filter((item) => item.denominator > 0) ?? [];
  const activeTarget = summary?.target_coverage ?? targetCoverage;
  const currentEvaluationKey = summary?.cut_off_date
    ? `${new Date(summary.cut_off_date).getUTCFullYear()}_${new Date(summary.cut_off_date).getUTCMonth() + 1}`
    : '';
  const currentEvaluationOrder = currentEvaluationKey
    ? Number(currentEvaluationKey.split('_')[0]) * 12 + Number(currentEvaluationKey.split('_')[1])
    : 0;
  const monthsThroughCurrent = currentEvaluationOrder
    ? monthsWithData.filter((item) => buildMonthOrder(item) <= currentEvaluationOrder)
    : monthsWithData;
  const monthsMetThroughCurrent = monthsThroughCurrent.filter((item) => item.semaphore === 'green').length;
  const currentEvaluationMonth = monthsWithData.find((item) => buildMonthKey(item) === currentEvaluationKey);
  const currentTargetCount = currentEvaluationMonth
    ? Math.ceil((currentEvaluationMonth.denominator * activeTarget) / 100)
    : 0;
  const currentMissingCount = currentEvaluationMonth
    ? Math.max(0, currentTargetCount - currentEvaluationMonth.numerator)
    : 0;

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
  const downloadParams = new URLSearchParams({ province: selectedProvince, month: selectedMonth, indicator: selectedIndicator });

  const handleMonthChange = (event) => {
    setSelectedMonth(event.target.value);
    setPage(1);
  };

  const handleDownload = async () => {
    setDownloadError(null);
    try {
      const response = await api.get(`/api/report/incumplidos.xlsx?${downloadParams.toString()}`, {
        responseType: 'blob',
      });
      const blobUrl = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = `incumplidos_${selectedIndicator}${selectedMonth ? `_${selectedMonth}` : ''}.xlsx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (err) {
      setDownloadError(err.response?.data?.detail || err.message || 'No se pudo descargar el Excel');
    }
  };

  return (
    <section className="space-y-6">
      <section className="grid gap-4 md:grid-cols-4">
        <MetricCard title="Estado API" value={summary ? 'Conectado' : status} icon={summary ? CheckCircle2 : Loader2} tone="blue" />
        <MetricCard title="Meta" value={`${activeTarget}%`} icon={Target} tone="lilac" />
        <MetricCard title="Meses cumplidos" value={summary ? `${monthsMetThroughCurrent}/${monthsThroughCurrent.length}` : '-'} icon={TrendingUp} tone="pink" />
        <MetricCard title={isMc02 ? 'Registros observados' : 'Incumplidos total'} value={summary ? incumplidosCount : '-'} icon={UsersRound} tone="rose" />
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
              {isMc02
                ? `Avance acumulado por cohorte de nacimiento segun meta de ${activeTarget}%.`
                : `${summary?.committed ? 'Compromiso cumplido' : 'Compromiso pendiente'} segun meta de ${activeTarget}% y regla 5 de 6 meses.`}
            </p>
          </div>
          <span className="inline-flex items-center gap-2 rounded-full border border-clinic-violet/15 bg-white/70 px-4 py-2 text-sm font-semibold text-clinic-muted">
            <CalendarDays className="h-4 w-4 text-clinic-violet" />
            {summary?.cut_off_date
              ? `Corte: ${formatDate(summary.cut_off_date)}`
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

        {currentEvaluationMonth && (
          <div className="mt-5 rounded-xl border border-amber-200 bg-amber-50 p-4">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="inline-flex items-center gap-2 text-sm font-bold uppercase tracking-[0.14em] text-amber-800">
                  <CalendarDays className="h-4 w-4" />
                  {currentPeriodTitle}: {currentEvaluationMonth.month} {currentEvaluationMonth.year}
                </p>
                <p className="mt-2 text-sm leading-6 text-amber-900">
                  Avance hasta el corte: {currentEvaluationMonth.numerator} de {currentEvaluationMonth.denominator} registros completos.
                  {currentMissingCount > 0
                    ? ` Faltan ${currentMissingCount} registros para alcanzar la meta de ${activeTarget}%.`
                    : ` La meta de ${activeTarget}% ya se alcanza con los registros actuales.`}
                </p>
              </div>
              <div className="min-w-48 rounded-lg bg-white/80 p-3 ring-1 ring-amber-200">
                <p className="text-xs font-bold uppercase tracking-[0.14em] text-amber-800">Cobertura actual</p>
                <p className="mt-1 text-3xl font-bold text-clinic-ink">{currentEvaluationMonth.coverage}%</p>
                <div className="mt-3 h-2 overflow-hidden rounded-full bg-amber-100">
                  <div
                    className="h-full rounded-full bg-clinic-teal"
                    style={{ width: `${Math.min(100, currentEvaluationMonth.coverage)}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="mt-6 overflow-hidden rounded-xl border border-clinic-border bg-white/70">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-clinic-border text-sm">
              <thead className="bg-slate-100">
                <tr className="text-left text-clinic-ink">
                  <th className="px-4 py-3 font-bold">{periodLabelTitle}</th>
                  <th className="px-4 py-3 font-bold">Estado del periodo</th>
                  <th className="px-4 py-3 font-bold">Cobertura</th>
                  <th className="px-4 py-3 font-bold">Numerador</th>
                  <th className="px-4 py-3 font-bold">Denominador</th>
                  <th className="px-4 py-3 font-bold">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-clinic-border bg-white">
                {monthsWithData.map((item) => {
                  const isCurrentEvaluationMonth = buildMonthKey(item) === currentEvaluationKey;
                  return (
                  <tr
                    key={`${item.month}-${item.year}`}
                    className={`border-l-4 ${
                      isCurrentEvaluationMonth
                        ? 'border-amber-400 bg-amber-50/70'
                        : semaphoreStyles[item.semaphore]?.border ?? semaphoreStyles.red.border
                    } text-clinic-muted transition hover:bg-clinic-lilac/10`}
                  >
                    <td className="px-4 py-3 font-bold capitalize text-clinic-ink">{item.month} {item.year}</td>
                    <td className="px-4 py-3">
                      <PeriodBadge
                        inVerificationPeriod={item.in_verification_period}
                        isCurrentEvaluationMonth={isCurrentEvaluationMonth}
                        isMc02={isMc02}
                      />
                    </td>
                    <td className="px-4 py-3 font-semibold text-clinic-ink">{item.coverage}%</td>
                    <td className="px-4 py-3">{item.numerator}</td>
                    <td className="px-4 py-3">{item.denominator}</td>
                    <td className="px-4 py-3"><SemaphoreBadge value={item.semaphore} /></td>
                  </tr>
                  );
                })}
                {summary && monthsWithData.length === 0 && (
                  <tr>
                    <td className="px-4 py-4 text-clinic-muted" colSpan="6">
                      No hay meses con registros evaluables para mostrar.
                    </td>
                  </tr>
                )}
                {!summary && (
                  <tr>
                    <td className="px-4 py-4 text-clinic-muted" colSpan="6">Cargando historial mensual...</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="panel p-5 lg:p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h2 className="text-2xl font-bold text-clinic-ink">{incumplidosTitle}</h2>
            <p className="mt-1 text-sm text-clinic-muted">
              Mostrando registros observados de la {periodLabel} {selectedMonthLabel}.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <label className="block">
              <span className="text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">{periodLabelTitle}</span>
              <select value={selectedMonth} onChange={handleMonthChange} className="field min-w-48">
                {monthsWithData.map((item) => (
                  <option key={buildMonthKey(item)} value={buildMonthKey(item)}>
                    {item.month} {item.year}
                  </option>
                ))}
              </select>
            </label>
            <button type="button" onClick={handleDownload} className="icon-button btn-primary">
              <Download className="h-4 w-4" />
              Descargar Excel
            </button>
          </div>
        </div>

        {downloadError && (
          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm font-semibold text-red-700">
            {downloadError}
          </div>
        )}

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
                  <th className="px-4 py-3 font-bold">Nacimiento</th>
                  <th className="px-4 py-3 font-bold">Establecimiento</th>
                  <th className="w-60 px-4 py-3 font-bold">{isMc02 ? 'Componentes observados' : 'Atencion observada'}</th>
                  <th className="min-w-[36rem] px-4 py-3 font-bold">Motivo</th>
                  <th className="px-4 py-3 font-bold">Alertas</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-clinic-border bg-white">
                {paginatedIncumplidos.map((item) => (
                  <tr key={`${item.Mes_eva}-${item.afi_DNI}-${item.NumCNV}`} className="text-clinic-muted transition hover:bg-clinic-rose/10">
                    <td className="px-4 py-3 font-semibold text-clinic-ink">{item.afi_DNI || item.NumCNV || '-'}</td>
                    <td className="px-4 py-3">
                      {[item.afi_nombres, item.afi_appaterno, item.afi_apmaterno].filter(Boolean).join(' ') || '-'}
                    </td>
                    <td className="px-4 py-3 font-semibold text-clinic-ink">{formatDate(item.fec_Nac)}</td>
                    <td className="px-4 py-3">
                      <p className="inline-flex items-center gap-2 font-bold text-clinic-ink">
                        <Hospital className="h-4 w-4 text-clinic-violet" />
                        {item.Des_EESS || 'Sin establecimiento'}
                      </p>
                      {item.Des_MicroRed && <p className="mt-1 text-xs text-clinic-muted">{item.Des_MicroRed}</p>}
                    </td>
                    <td className="w-60 px-4 py-3 align-top">
                      <ObservedComponentsCell item={item} />
                    </td>
                    <td className="min-w-[36rem] px-4 py-3 align-top whitespace-pre-line leading-6">{item.reason}</td>
                    <td className="px-4 py-3">
                      {item.clinical_alerts?.length > 0 ? (
                        <span className="inline-flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-semibold leading-5 text-amber-800">
                          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                          {item.clinical_alerts.join('; ')}
                        </span>
                      ) : '-'}
                    </td>
                  </tr>
                ))}
                {summary && monthIncumplidos.length === 0 && (
                  <tr>
                    <td className="px-4 py-4 text-clinic-muted" colSpan="7">
                      <span className="inline-flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                        No hay incumplidos en el mes seleccionado.
                      </span>
                    </td>
                  </tr>
                )}
                {!summary && (
                  <tr>
                    <td className="px-4 py-4 text-clinic-muted" colSpan="7">
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
