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
} from 'lucide-react';
import MetricCard from './components/MetricCard';
import PeriodBadge from './components/PeriodBadge';
import SectionPanel from './components/SectionPanel';
import SemaphoreBadge from './components/SemaphoreBadge';
import { useDashboardData } from './hooks/useDashboardData';
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
              className="badge badge-info badge-outline h-auto max-w-full justify-start px-2.5 py-1 text-left text-xs font-bold leading-4"
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

function CommitmentPanel({ summary }) {
  const commitment = summary?.commitment_summary;
  if (!commitment?.verifications?.length) return null;
  const currentVerification = commitment.verifications.find((verification) => verification.is_current) ?? commitment.verifications[0];
  const otherVerifications = commitment.verifications.filter((verification) => verification.code !== currentVerification.code);
  const globalStatus = commitment.global_committed ? 'green' : 'red';

  return (
    <SectionPanel className="overflow-hidden">
      <div className="grid gap-0 xl:grid-cols-[24rem_minmax(0,1fr)]">
        <div className="bg-primary p-5 text-primary-content lg:p-6">
          <p className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.16em] text-primary-content/75">
            <Target className="h-4 w-4 text-secondary" />
            Compromiso SI-02
          </p>
          <h3 className="mt-3 text-2xl font-black text-primary-content">{commitment.current_label}</h3>
          <p className="mt-2 text-sm font-medium leading-6 text-primary-content/75">
            Lectura oficial del compromiso segun la verificacion vigente y los meses cumplidos por subindicador.
          </p>
          <div className="mt-5">
            <SemaphoreBadge value={globalStatus} />
          </div>
          <div className="mt-5 rounded-xl border border-white/15 bg-white/10 p-4 text-sm font-semibold text-primary-content/80">
            <span className="block text-xs font-bold uppercase tracking-[0.14em] text-primary-content/60">Regla vigente</span>
            <span className="mt-1 block text-primary-content">{currentVerification.required_rule}</span>
          </div>
        </div>

        <div className="p-5 lg:p-6">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.16em] text-clinic-muted">Verificacion vigente</p>
              <h4 className="mt-2 text-xl font-black text-primary">{currentVerification.label}</h4>
              <p className="mt-1 text-sm font-semibold text-clinic-muted">{currentVerification.period}</p>
            </div>
            <SemaphoreBadge value={currentVerification.committed ? 'green' : 'red'} />
          </div>

          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {currentVerification.subindicators.map((item) => {
              const progress = item.required_months ? Math.min(100, Math.round((item.months_met / item.required_months) * 100)) : 0;
              return (
                <article
                  key={item.subindicator_code}
                  className={`rounded-xl border bg-base-100 p-4 shadow-sm ${
                    item.committed ? 'border-success/25' : 'border-error/25'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="text-sm font-black text-primary">{formatSubindicatorCode(item.subindicator_code)}</p>
                      <p className="mt-1 text-xs font-semibold leading-5 text-clinic-muted">
                        {item.months_met}/{item.required_months} meses requeridos
                      </p>
                    </div>
                    <span className={`badge h-auto shrink-0 px-3 py-1.5 text-xs font-bold ${
                      item.committed ? 'badge-success' : 'badge-error'
                    }`}>
                      {item.committed ? 'Cumple' : 'No cumple'}
                    </span>
                  </div>
                  <progress
                    className={`progress mt-4 h-2 w-full ${item.committed ? 'progress-success' : 'progress-error'}`}
                    value={progress}
                    max="100"
                  />
                </article>
              );
            })}
          </div>

          {otherVerifications.length > 0 && (
            <div className="mt-5 grid gap-2">
              {otherVerifications.map((verification) => (
                <div key={verification.code} className="flex flex-col gap-2 rounded-xl border border-base-300 bg-base-200 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm font-bold text-primary">{verification.label}</p>
                    <p className="text-xs font-semibold text-clinic-muted">{verification.required_rule}</p>
                  </div>
                  <SemaphoreBadge value={verification.committed ? 'green' : 'red'} />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </SectionPanel>
  );
}

function CurrentPeriodPanel({
  currentEvaluationMonth,
  currentMissingCount,
  currentPeriodTitle,
  viewTarget,
}) {
  if (!currentEvaluationMonth) {
    return (
      <SectionPanel className="p-5 lg:p-6">
        <div className="flex items-center gap-3 text-clinic-muted">
          <Loader2 className="h-5 w-5 animate-spin text-clinic-teal" />
          <p className="text-sm font-semibold">Cargando periodo en evaluacion...</p>
        </div>
      </SectionPanel>
    );
  }

  const targetReached = currentMissingCount <= 0;
  const targetStatusClass = targetReached
    ? 'border-success/25 bg-success/10 text-success'
    : 'border-warning/25 bg-warning/10 text-warning';
  const coverageTone = currentEvaluationMonth.semaphore === 'green' ? 'progress-success' : 'progress-error';

  return (
    <SectionPanel className="p-4">
      <div className="grid gap-3 xl:grid-cols-[minmax(14rem,1.2fr)_repeat(4,minmax(8rem,0.8fr))] xl:items-center">
        <div className="rounded-xl bg-primary px-4 py-3 text-primary-content">
          <p className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.14em] text-primary-content/75">
            <CalendarDays className="h-4 w-4 text-secondary" />
            {currentPeriodTitle}
          </p>
          <h3 className="mt-1 text-xl font-black capitalize">
            {currentEvaluationMonth.month} {currentEvaluationMonth.year}
          </h3>
        </div>

        <div className="rounded-xl border border-base-300 bg-base-200 px-3 py-2">
          <p className="text-xs font-bold uppercase text-clinic-muted">Cobertura</p>
          <div className="mt-1 flex items-center justify-between gap-2">
            <p className="text-2xl font-black text-primary">{currentEvaluationMonth.coverage}%</p>
            <SemaphoreBadge value={currentEvaluationMonth.semaphore} />
          </div>
          <progress
            className={`progress mt-2 h-2 w-full ${coverageTone}`}
            value={Math.min(100, currentEvaluationMonth.coverage)}
            max="100"
          />
        </div>

        <div className="rounded-xl border border-base-300 bg-base-200 px-3 py-2">
          <p className="text-xs font-bold uppercase text-clinic-muted">Numerador</p>
          <p className="mt-1 text-2xl font-black text-primary">{currentEvaluationMonth.numerator}</p>
        </div>

        <div className="rounded-xl border border-base-300 bg-base-200 px-3 py-2">
          <p className="text-xs font-bold uppercase text-clinic-muted">Denominador</p>
          <p className="mt-1 text-2xl font-black text-primary">{currentEvaluationMonth.denominator}</p>
        </div>

        <div className={`rounded-xl border px-3 py-2 ${targetStatusClass}`}>
          <p className="text-xs font-bold uppercase">Brecha</p>
          <p className="mt-1 text-2xl font-black">{targetReached ? '0' : currentMissingCount}</p>
          <p className="mt-1 text-xs font-bold">
            Meta {viewTarget}%
          </p>
        </div>
      </div>
    </SectionPanel>
  );
}

function Dashboard({ selectedProvince, targetCoverage, selectedIndicator, selectedSi02Subindicator = 'all' }) {
  const {
    status,
    summary,
    error,
    downloadError,
    selectedMonth,
    selectedSubindicator,
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
  } = useDashboardData(selectedProvince, targetCoverage, selectedIndicator, selectedSi02Subindicator);

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

  const monthlyDescription = isMc02
    ? `Avance acumulado por cohorte de nacimiento segun meta de ${viewTarget}%.`
    : isSi02
    ? selectedSubindicatorSummary
      ? `Vista especifica del subindicador ${formatSubindicatorCode(
          selectedSubindicatorSummary.subindicator_code,
        )} segun meta oficial de ${viewTarget}%.`
      : `Avance agregado del paquete SI-02 segun meta de referencia de ${viewTarget}%.`
    : `${summary?.committed ? 'Compromiso cumplido' : 'Compromiso pendiente'} segun meta de ${viewTarget}% y regla 5 de 6 meses.`;

  const cutOffLabel = summary?.cut_off_date
    ? `Corte: ${formatDate(summary.cut_off_date)}`
    : 'Periodo oficial: Junio - Noviembre 2026';

  return (
    <section className="space-y-6">
      {error && (
        <div className="alert alert-error rounded-xl text-sm font-semibold">
          <AlertCircle className="h-5 w-5" />
          <span>No se pudo conectar con el backend: {error}</span>
        </div>
      )}

      {isGlobalSi02View ? (
        <CommitmentPanel summary={summary} />
      ) : (
        <div className="space-y-4">
          <div className="space-y-4">
            <CurrentPeriodPanel
              currentEvaluationMonth={currentEvaluationMonth}
              currentMissingCount={currentMissingCount}
              currentPeriodTitle={currentPeriodTitle}
              viewTarget={viewTarget}
            />

            <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
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
          </div>

          <section className="flex flex-col gap-4">
            <SectionPanel className="order-2 overflow-hidden">
              <div className="border-b border-base-300 p-4">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h2 className="text-xl font-black text-primary">{viewTitle}</h2>
                    <p className="mt-1 text-xs font-semibold leading-5 text-clinic-muted">{monthlyDescription}</p>
                  </div>
                  <span className="badge badge-ghost h-auto gap-2 border-base-300 px-3 py-1.5 text-xs font-bold text-clinic-muted">
                    <CalendarDays className="h-4 w-4 text-secondary" />
                    {cutOffLabel}
                  </span>
                </div>

                <div className="mt-3 grid gap-2 text-xs sm:grid-cols-2">
                  <div className="rounded-lg border border-success/25 bg-success/10 px-3 py-2 font-semibold text-success">
                    Cumple: cobertura mayor o igual a {viewTarget}%.
                  </div>
                  <div className="rounded-lg border border-error/25 bg-error/10 px-3 py-2 font-semibold text-error">
                    No cumple: cobertura menor a {viewTarget}%.
                  </div>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="table table-zebra table-sm min-w-full text-sm">
                  <thead className="bg-base-200 text-left text-primary">
                    <tr>
                      <th className="px-4 py-3 font-bold">{periodLabelTitle}</th>
                      <th className="px-4 py-3 font-bold">Estado del periodo</th>
                      <th className="px-4 py-3 font-bold">Cobertura</th>
                      <th className="px-4 py-3 font-bold">Numerador</th>
                      <th className="px-4 py-3 font-bold">Denominador</th>
                      <th className="px-4 py-3 font-bold">Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {monthsWithData.map((item) => {
                      const isCurrentEvaluationMonth = buildMonthKey(item) === currentEvaluationKey;
                      return (
                        <tr
                          key={`${item.month}-${item.year}`}
                          className={`border-l-4 ${
                            isCurrentEvaluationMonth
                              ? 'border-warning bg-warning/10'
                              : item.semaphore === 'green'
                              ? 'border-success/60'
                              : 'border-error/60'
                          } text-clinic-muted transition hover:bg-base-200`}
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
            </SectionPanel>

            <SectionPanel className="order-1 overflow-hidden">
              <div className="border-b border-base-300 p-4">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                  <div>
                    <h2 className="text-xl font-black text-primary">{incumplidosTitle}</h2>
                    <p className="mt-1 text-xs font-semibold leading-5 text-clinic-muted">
                      Mostrando registros observados de la {periodLabel} {selectedMonthLabel}.
                    </p>
                  </div>
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
                    <label className="block">
                      <span className="text-xs font-bold uppercase tracking-[0.18em] text-clinic-muted">
                        {periodLabelTitle}
                      </span>
                      <select value={selectedMonth} onChange={handleMonthChange} className="select select-bordered select-sm mt-1 min-w-48 font-semibold">
                        {monthsWithData.map((item) => (
                          <option key={buildMonthKey(item)} value={buildMonthKey(item)}>
                            {item.month} {item.year}
                          </option>
                        ))}
                      </select>
                    </label>
                    <button type="button" onClick={handleDownload} className="btn btn-primary btn-sm text-primary-content">
                      <Download className="h-4 w-4" />
                      Descargar Excel
                    </button>
                  </div>
                </div>

                {downloadError && (
                  <div className="alert alert-error mt-4 rounded-xl py-3 text-sm font-semibold">
                    <AlertCircle className="h-4 w-4" />
                    <span>{downloadError}</span>
                  </div>
                )}

                <div className="mt-5 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <span className="inline-flex items-center gap-2 text-sm font-semibold text-clinic-muted">
                    <FileSpreadsheet className="h-4 w-4 text-secondary" />
                    {monthIncumplidos.length} registros incumplidos
                  </span>
                  <span className="text-sm font-semibold text-clinic-muted">
                    Pagina {safePage} de {totalPages}
                  </span>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="table table-zebra table-sm min-w-full text-sm">
                  <thead className="bg-base-200 text-left text-primary">
                    <tr>
                      <th className="px-4 py-3 font-bold">DNI</th>
                      <th className="px-4 py-3 font-bold">Paciente</th>
                      <th className="px-4 py-3 font-bold">Nacimiento</th>
                      <th className="px-4 py-3 font-bold">Establecimiento</th>
                      <th className="w-60 px-4 py-3 font-bold">
                        {isMc02 || isSi02 ? 'Componentes observados' : 'Atencion observada'}
                      </th>
                      <th className="min-w-[36rem] px-4 py-3 font-bold">Motivo</th>
                      <th className="px-4 py-3 font-bold">Alertas</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedIncumplidos.map((item) => (
                      <tr
                        key={`${item.subindicator_code || selectedIndicator}-${item.Mes_eva}-${
                          item.afi_DNI || item.NumCNV
                        }`}
                        className="text-clinic-muted transition hover:bg-base-200"
                      >
                        <td className="px-4 py-3 font-semibold text-clinic-ink">
                          {item.afi_DNI || item.NumCNV || '-'}
                        </td>
                        <td className="px-4 py-3">
                          {[item.afi_nombres, item.afi_appaterno, item.afi_apmaterno].filter(Boolean).join(' ') || '-'}
                        </td>
                        <td className="px-4 py-3 font-semibold text-clinic-ink">{formatDate(item.fec_Nac)}</td>
                        <td className="px-4 py-3">
                          <p className="inline-flex items-center gap-2 font-bold text-clinic-ink">
                            <Hospital className="h-4 w-4 text-secondary" />
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
                            <span className="inline-flex items-start gap-2 rounded-lg border border-warning/30 bg-warning/10 px-3 py-2 text-xs font-semibold leading-5 text-warning">
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
                        <td className="px-4 py-4 text-clinic-muted" colSpan="7">
                          <span className="inline-flex items-center gap-2">
                            <CheckCircle2 className="h-4 w-4 text-success" />
                            No hay incumplidos en el mes seleccionado.
                          </span>
                        </td>
                      </tr>
                    )}
                    {!summary && (
                      <tr>
                        <td className="px-4 py-4 text-clinic-muted" colSpan="7">
                          <span className="inline-flex items-center gap-2">
                            <Loader2 className="h-4 w-4 animate-spin text-secondary" />
                            Cargando incumplidos...
                          </span>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              <div className="flex flex-col gap-3 border-t border-base-300 p-5 sm:flex-row sm:items-center sm:justify-between">
                <button
                  type="button"
                  onClick={() => setPage((current) => Math.max(1, current - 1))}
                  disabled={safePage <= 1}
                  className="btn btn-outline btn-secondary btn-sm disabled:cursor-not-allowed disabled:opacity-40"
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
                  className="btn btn-outline btn-secondary btn-sm disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Siguiente
                  <ArrowRight className="h-4 w-4" />
                </button>
              </div>
            </SectionPanel>
          </section>
        </div>
      )}

      {!isGlobalSi02View && summary?.committed === false && selectedSubindicator === 'all' && (
        <div className="alert alert-error rounded-xl text-sm font-semibold">
          <AlertCircle className="h-4 w-4" />
          <span>El compromiso aun no alcanza la regla de cumplimiento configurada para el periodo de verificacion.</span>
        </div>
      )}
    </section>
  );
}

export default Dashboard;
