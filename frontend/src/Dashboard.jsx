import { useMemo } from 'react';
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
  Layers3,
  Loader2,
  Target,
  TrendingUp,
  UsersRound,
} from 'lucide-react';
import MetricCard from './components/MetricCard';
import PeriodBadge from './components/PeriodBadge';
import SemaphoreBadge from './components/SemaphoreBadge';
import { useDashboardData } from './hooks/useDashboardData';
import indicators from './indicators/registry';
import { formatShortDate } from './utils/dates';

const PAGE_SIZE = 10;

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

function formatSubindicatorCode(value) {
  const code = String(value || '').toUpperCase();
  return code.replace(/^SI02_(\d+)$/, 'SI-02.$1');
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

function latestPeriodWithData(monthly = []) {
  const withData = monthly.filter((item) => item.denominator > 0);
  return (
    [...withData].sort((left, right) => buildMonthOrder(left) - buildMonthOrder(right)).at(-1) ??
    monthly.at(-1)
  );
}

function SubindicatorSelector({ options, value, onChange }) {
  return (
    <section className="panel p-4 lg:p-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="max-w-2xl">
          <p className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">
            <Layers3 className="h-4 w-4 text-clinic-violet" />
            Vista SI-02
          </p>
          <h3 className="mt-2 text-xl font-bold text-clinic-ink">Seguimiento por subindicador</h3>
          <p className="mt-1 text-sm leading-6 text-clinic-muted">
            Cambia entre el compromiso global y cada subindicador para revisar avance mensual, omisos y descarga enfocada.
          </p>
        </div>
        <div className="grid w-full gap-2 md:grid-cols-2 xl:grid-cols-5">
          {options.map((option) => {
            const active = option.code === value;
            const latest = latestPeriodWithData(option.summary?.monthly ?? []);
            return (
              <button
                key={option.code}
                type="button"
                onClick={() => onChange(option.code)}
                className={`min-h-24 rounded-xl border p-3 text-left transition ${
                  active
                    ? 'border-clinic-teal bg-clinic-mint text-clinic-ink shadow-soft'
                    : 'border-clinic-border bg-white/70 text-clinic-muted hover:-translate-y-0.5 hover:border-clinic-teal/40 hover:bg-white'
                }`}
              >
                <span className="text-xs font-bold uppercase tracking-[0.14em]">{option.shortName}</span>
                <span className="mt-1 block text-sm font-bold leading-5 text-clinic-ink">{option.title}</span>
                <span className="mt-2 block text-xs font-semibold">
                  {option.summary
                    ? `${option.summary.months_met}/${option.summary.months_evaluated} meses, ${option.omisosCount} omisos`
                    : 'Sin datos cargados'}
                </span>
                {latest && (
                  <span className="mt-1 block text-xs font-semibold">
                    Ultimo mes: {latest.coverage}% ({latest.numerator}/{latest.denominator})
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function CommitmentPanel({ summary }) {
  const commitment = summary?.commitment_summary;
  if (!commitment?.verifications?.length) return null;

  return (
    <section className="panel p-4 lg:p-5">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">
            <Target className="h-4 w-4 text-clinic-violet" />
            Compromiso SI-02
          </p>
          <h3 className="mt-2 text-xl font-bold text-clinic-ink">{commitment.current_label}</h3>
          <p className="mt-1 text-sm leading-6 text-clinic-muted">
            Estado segun meses cumplidos por subindicador y la regla oficial de verificacion.
          </p>
        </div>
        <SemaphoreBadge value={commitment.global_committed ? 'green' : 'red'} />
      </div>

      <div className="mt-4 grid gap-3 xl:grid-cols-2">
        {commitment.verifications.map((verification) => (
          <article
            key={verification.code}
            className={`rounded-xl border p-4 ${
              verification.is_current ? 'border-clinic-teal bg-clinic-mint/45' : 'border-clinic-border bg-white/70'
            }`}
          >
            <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm font-bold text-clinic-ink">{verification.label}</p>
                <p className="mt-1 text-xs font-semibold text-clinic-muted">{verification.period}</p>
                <p className="mt-1 text-xs font-semibold text-clinic-muted">{verification.required_rule}</p>
              </div>
              <SemaphoreBadge value={verification.committed ? 'green' : 'red'} />
            </div>
            <div className="mt-3 grid gap-2 sm:grid-cols-2">
              {verification.subindicators.map((item) => (
                <div key={item.subindicator_code} className="rounded-lg border border-clinic-border bg-white/80 p-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-xs font-bold uppercase tracking-[0.12em] text-clinic-teal">
                        {formatSubindicatorCode(item.subindicator_code)}
                      </p>
                      <p className="mt-1 text-xs font-semibold leading-5 text-clinic-muted">
                        {item.months_met}/{item.required_months} meses requeridos
                      </p>
                    </div>
                    <span
                      className={`rounded-full px-2 py-1 text-xs font-bold ring-1 ${
                        item.committed
                          ? 'bg-emerald-50 text-emerald-700 ring-emerald-200'
                          : 'bg-red-50 text-red-700 ring-red-200'
                      }`}
                    >
                      {item.committed ? 'Cumple' : 'No cumple'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function Dashboard({ selectedProvince, targetCoverage, selectedIndicator }) {
  const {
    status,
    summary,
    error,
    downloadError,
    selectedMonth,
    selectedSubindicator,
    setSelectedSubindicator,
    page,
    setPage,
    isMc02,
    isSi02,
    selectedSubindicatorSummary,
    viewSummary,
    viewTarget,
    incumplidosCount,
    monthsWithData,
    currentEvaluationKey,
    monthsThroughCurrent,
    monthsMetThroughCurrent,
    currentEvaluationMonth,
    currentTargetCount,
    currentMissingCount,
    selectedMonthLabel,
    monthIncumplidos,
    totalPages,
    safePage,
    paginatedIncumplidos,
    displayStart,
    displayEnd,
    handleMonthChange,
    handleDownload,
  } = useDashboardData(selectedProvince, targetCoverage, selectedIndicator);

  const activeIndicator = indicators[selectedIndicator] ?? indicators.mc03;
  const periodLabel = isMc02 ? 'cohorte' : 'mes de evaluacion';
  const periodLabelTitle = isMc02 ? 'Cohorte' : 'Mes';
  const currentPeriodTitle = isMc02 ? 'Cohorte en evaluacion' : 'Mes en evaluacion';
  const isGlobalSi02View = isSi02 && selectedSubindicator === 'all';

  const viewTitle = selectedSubindicatorSummary
    ? selectedSubindicatorSummary.subindicator_name
    : isSi02
    ? 'Compromiso global SI-02'
    : 'Avance del indicador';

  const incumplidosTitle = isMc02
    ? 'Incumplidos por cohorte de nacimiento'
    : isSi02
    ? selectedSubindicatorSummary
      ? `Incumplidos - ${formatSubindicatorCode(selectedSubindicatorSummary.subindicator_code)}`
      : 'Incumplidos por subindicador y mes'
    : 'Incumplidos por mes de evaluacion';

  const si02SubindicatorOptions = useMemo(() => {
    if (!isSi02) return [];
    const configured = activeIndicator.subindicators ?? [];
    const summaryByCode = summary?.subindicators ?? {};
    const globalSummary = summary
      ? {
          months_met: summary.months_met,
          months_evaluated: summary.months_evaluated,
          monthly: summary.monthly ?? [],
          omisos: summary.omisos ?? [],
        }
      : null;
    return [
      {
        code: 'all',
        shortName: 'Global',
        title: 'Todo SI-02',
        summary: globalSummary,
        omisosCount: globalSummary?.omisos?.length ?? 0,
      },
      ...configured.map((item) => {
        const itemSummary = summaryByCode[item.code];
        return {
          code: item.code,
          shortName: item.shortName,
          title: itemSummary?.subindicator_name ?? item.title,
          summary: itemSummary,
          omisosCount: itemSummary?.omisos?.length ?? 0,
        };
      }),
    ];
  }, [activeIndicator.subindicators, isSi02, summary]);

  return (
    <section className="space-y-6">
      {isSi02 && (
        <SubindicatorSelector
          options={si02SubindicatorOptions}
          value={selectedSubindicator}
          onChange={setSelectedSubindicator}
        />
      )}

      <section className="grid gap-4 md:grid-cols-4">
        <MetricCard
          title="Estado API"
          value={summary ? 'Conectado' : status}
          icon={summary ? CheckCircle2 : Loader2}
          tone="blue"
        />
        <MetricCard
          title={isSi02 ? 'Meta de vista' : 'Meta'}
          value={`${viewTarget}%`}
          icon={Target}
          tone="lilac"
        />
        <MetricCard
          title="Meses cumplidos"
          value={viewSummary ? `${monthsMetThroughCurrent}/${monthsThroughCurrent.length}` : '-'}
          icon={TrendingUp}
          tone="pink"
        />
        <MetricCard
          title={isMc02 ? 'Registros observados' : 'Incumplidos total'}
          value={viewSummary ? incumplidosCount : '-'}
          icon={UsersRound}
          tone="rose"
        />
      </section>

      {isSi02 && <CommitmentPanel summary={summary} />}

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
          No se pudo conectar con el backend: {error}
        </div>
      )}

      <section className="panel p-5 lg:p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-2xl font-bold text-clinic-ink">{viewTitle}</h2>
            <p className="mt-1 text-sm text-clinic-muted">
              {isMc02
                ? `Avance acumulado por cohorte de nacimiento segun meta de ${viewTarget}%.`
                : isSi02
                ? selectedSubindicatorSummary
                  ? `Vista especifica del subindicador ${formatSubindicatorCode(
                      selectedSubindicatorSummary.subindicator_code,
                    )} segun meta oficial de ${viewTarget}%.`
                  : `Avance agregado del paquete SI-02 segun meta de referencia de ${viewTarget}%.`
                : `${summary?.committed ? 'Compromiso cumplido' : 'Compromiso pendiente'} segun meta de ${viewTarget}% y regla 5 de 6 meses.`}
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
            Cumple: cobertura mayor o igual a {viewTarget}%.
          </div>
          <div className="rounded-xl border border-red-200 bg-red-50 p-3 font-semibold text-red-700">
            No cumple: cobertura menor a {viewTarget}%.
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
                  Avance hasta el corte: {currentEvaluationMonth.numerator} de {currentEvaluationMonth.denominator}{' '}
                  registros completos.
                  {currentMissingCount > 0
                    ? ` Faltan ${currentMissingCount} registros para alcanzar la meta de ${viewTarget}%.`
                    : ` La meta de ${viewTarget}% ya se alcanza con los registros actuales.`}
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
                          : item.semaphore === 'green'
                          ? 'border-emerald-300'
                          : 'border-red-300'
                      } text-clinic-muted transition hover:bg-clinic-lilac/10`}
                    >
                      <td className="px-4 py-3 font-bold capitalize text-clinic-ink">
                        {item.month} {item.year}
                      </td>
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
                      <td className="px-4 py-3">
                        <SemaphoreBadge value={item.semaphore} />
                      </td>
                    </tr>
                  );
                })}
                {viewSummary && monthsWithData.length === 0 && (
                  <tr>
                    <td className="px-4 py-4 text-clinic-muted" colSpan="6">
                      No hay meses con registros evaluables para mostrar.
                    </td>
                  </tr>
                )}
                {!summary && (
                  <tr>
                    <td className="px-4 py-4 text-clinic-muted" colSpan="6">
                      Cargando historial mensual...
                    </td>
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
              <span className="text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">
                {periodLabelTitle}
              </span>
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
          <span className="text-sm font-semibold text-clinic-muted">
            Pagina {safePage} de {totalPages}
          </span>
        </div>

        <div className="mt-5 overflow-hidden rounded-xl border border-clinic-border bg-white/70">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-clinic-border text-sm">
              <thead className="bg-slate-100">
                <tr className="text-left text-clinic-ink">
                  <th className="px-4 py-3 font-bold">DNI</th>
                  <th className="px-4 py-3 font-bold">Paciente</th>
                  {isGlobalSi02View && <th className="px-4 py-3 font-bold">Subindicador</th>}
                  <th className="px-4 py-3 font-bold">Nacimiento</th>
                  <th className="px-4 py-3 font-bold">Establecimiento</th>
                  <th className="w-60 px-4 py-3 font-bold">
                    {isMc02 || isSi02 ? 'Componentes observados' : 'Atencion observada'}
                  </th>
                  <th className="min-w-[36rem] px-4 py-3 font-bold">Motivo</th>
                  <th className="px-4 py-3 font-bold">Alertas</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-clinic-border bg-white">
                {paginatedIncumplidos.map((item) => (
                  <tr
                    key={`${item.subindicator_code || selectedIndicator}-${item.Mes_eva}-${
                      item.afi_DNI || item.NumCNV
                    }`}
                    className="text-clinic-muted transition hover:bg-clinic-rose/10"
                  >
                    <td className="px-4 py-3 font-semibold text-clinic-ink">
                      {item.afi_DNI || item.NumCNV || '-'}
                    </td>
                    <td className="px-4 py-3">
                      {[item.afi_nombres, item.afi_appaterno, item.afi_apmaterno].filter(Boolean).join(' ') || '-'}
                    </td>
                    {isGlobalSi02View && (
                      <td className="px-4 py-3">
                        <span className="inline-flex rounded-full bg-clinic-mint px-2.5 py-1 text-xs font-bold uppercase tracking-[0.12em] text-clinic-teal ring-1 ring-teal-100">
                          {formatSubindicatorCode(item.subindicator_code) || '-'}
                        </span>
                        {item.subindicator_name && (
                          <p className="mt-1 w-44 text-xs leading-5 text-clinic-muted">
                            {item.subindicator_name}
                          </p>
                        )}
                      </td>
                    )}
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
                    <td className="min-w-[36rem] px-4 py-3 align-top whitespace-pre-line leading-6">
                      {item.reason}
                    </td>
                    <td className="px-4 py-3">
                      {item.clinical_alerts?.length > 0 ? (
                        <span className="inline-flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-semibold leading-5 text-amber-800">
                          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                          {item.clinical_alerts.join('; ')}
                        </span>
                      ) : (
                        '-'
                      )}
                    </td>
                  </tr>
                ))}
                {viewSummary && monthIncumplidos.length === 0 && (
                  <tr>
                    <td className="px-4 py-4 text-clinic-muted" colSpan={isGlobalSi02View ? 8 : 7}>
                      <span className="inline-flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                        No hay incumplidos en el mes seleccionado.
                      </span>
                    </td>
                  </tr>
                )}
                {!summary && (
                  <tr>
                    <td className="px-4 py-4 text-clinic-muted" colSpan={isGlobalSi02View ? 8 : 7}>
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

      {summary?.committed === false && selectedSubindicator === 'all' && (
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
