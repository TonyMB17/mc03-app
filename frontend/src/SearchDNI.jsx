import {
  AlertTriangle,
  Baby,
  ChevronDown,
  ClipboardList,
  Hospital,
  IdCard,
  Loader2,
  PackageCheck,
  Search,
  ShieldAlert,
  ShieldCheck,
  Syringe,
  TestTube2,
  Timer,
} from 'lucide-react';
import { useDniSearch } from './hooks/useDniSearch';
import StatusPill from './components/StatusPill';
import DoseDetails from './components/DoseDetails';
import HemoglobinDetails from './components/HemoglobinDetails';
import IronDetails from './components/IronDetails';
import SectionPanel from './components/SectionPanel';
import { UsiBadge, UsiCard } from './components/usi';
import indicators from './indicators/registry';
import { formatShortDate } from './utils/dates';

const componentLabels = {
  BCG: 'BCG',
  HVB: 'HVB',
  cred_rn: 'CRED recien nacido',
  cred_1_mas: 'CRED 1 mes a mas',
  neumococo: 'Vacuna neumococo',
  rotavirus: 'Vacuna rotavirus',
  antipolio: 'Vacuna antipolio',
  pentavalente: 'Vacuna pentavalente',
  hierro_menor_6m: 'Hierro 4 meses',
  hierro_mayor_6m: 'Hierro mayor de 6 meses',
  hemoglobina: 'Dosaje de hemoglobina',
};

function formatDate(value) {
  return formatShortDate(value);
}

function getFullName(personal = {}) {
  return [
    personal.afi_nombres,
    personal.afi_appaterno,
    personal.afi_apmaterno,
  ]
    .filter(Boolean)
    .join(' ');
}

function getInitials(name) {
  const initials = String(name || 'USI')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join('');
  return initials || 'US';
}

function formatIdentifier(value) {
  const text = value == null ? '' : String(value).trim();
  return text.replace(/\.0$/, '');
}

function registeredDoseCount(data = {}) {
  const explicitCount = Number(data.dosis_registradas ?? 0);
  const doseCount = Array.isArray(data.dosis) ? data.dosis.filter((dose) => dose.registrada || dose.fecha).length : 0;
  const hasAttentionDate = Boolean(data.fecha);
  return Math.max(Number.isFinite(explicitCount) ? explicitCount : 0, doseCount, hasAttentionDate ? 1 : 0);
}

function DetailMessage({ item }) {
  if (item.cumple) return null;
  const showWindow = !item.cumple && (item.fecha_inicio || item.fecha_limite);
  return (
    <div className="mt-3 rounded-xl border border-base-300 bg-base-200 p-3">
      <p className="text-sm leading-6 text-clinic-muted">{item.mensaje}</p>
      {showWindow && (
        <p className="mt-2 inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.14em] text-clinic-muted">
          <Timer className="h-3.5 w-3.5 text-secondary" />
          Servicio segun edad actual: {formatDate(item.fecha_inicio)} - {formatDate(item.fecha_limite)}
        </p>
      )}
    </div>
  );
}

function InfoItem({ label, value, icon: Icon }) {
  return (
    <div className="rounded-lg border border-base-300 bg-base-200 px-3 py-2">
      <p className="inline-flex items-center gap-1.5 text-[0.68rem] font-bold uppercase tracking-[0.12em] text-clinic-muted">
        <Icon className="h-3.5 w-3.5 text-secondary" />
        {label}
      </p>
      <p className="mt-1 break-words text-sm font-bold text-clinic-ink">{value || '-'}</p>
    </div>
  );
}

function SectionTitle({ icon: Icon, title }) {
  return (
    <div className="flex items-center gap-3">
      <span className="grid h-10 w-10 place-items-center rounded-xl bg-secondary/10 text-secondary ring-1 ring-secondary/20">
        <Icon className="h-5 w-5" />
      </span>
      <h3 className="text-lg font-bold text-clinic-ink">{title}</h3>
    </div>
  );
}

function PackageStatusBanner({ complete, completeText, incompleteText }) {
  return (
    <article className={`overflow-hidden rounded-2xl border ${complete ? 'border-success/30 bg-success/10' : 'border-error/30 bg-error/10'}`}>
      <div className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className={`inline-flex items-center gap-2 text-xs font-bold uppercase ${complete ? 'text-success' : 'text-error'}`}>
            {complete ? <ShieldCheck className="h-4 w-4" /> : <ShieldAlert className="h-4 w-4" />}
            Estado del paquete
          </p>
          <p className="mt-1 text-lg font-black text-primary">
            {complete ? completeText : incompleteText}
          </p>
        </div>
        <StatusPill estado={complete ? 'cumple' : 'no_cumple'} />
      </div>
    </article>
  );
}

function PatientSummaryCard({ result, metrics }) {
  const fullName = getFullName(result.personal);
  const identifier = result.personal.afi_DNI || result.personal.NumCNV || '-';

  return (
    <UsiCard className="overflow-hidden">
      <div className="grid gap-4 p-4 xl:grid-cols-[minmax(14rem,1.1fr)_minmax(0,2fr)_minmax(18rem,1.15fr)] xl:items-center">
        <div className="flex min-w-0 items-center gap-4">
          <div className="avatar placeholder">
            <div className="w-12 rounded-full bg-accent text-primary ring ring-primary/70 ring-offset-2 ring-offset-base-100">
              <span className="text-lg font-black">{getInitials(fullName)}</span>
            </div>
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <p className="inline-flex items-center gap-1.5 text-[0.68rem] font-bold uppercase tracking-[0.14em] text-clinic-muted">
                <Baby className="h-3.5 w-3.5 text-secondary" />
                Paciente activo
              </p>
              <UsiBadge tone={result.paquete_completo ? 'success' : 'error'} className="px-2 py-1 text-[0.65rem]">
                {result.paquete_completo ? 'Cumple' : 'Seguimiento'}
              </UsiBadge>
            </div>
            <h4 className="mt-1 break-words text-base font-black leading-tight text-primary">{fullName || 'Sin nombre registrado'}</h4>
            <p className="mt-1 text-xs font-semibold text-base-content/65">
              {identifier} · Nac. {formatDate(result.personal.fec_Nac)}
            </p>
          </div>
        </div>

        <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
          <InfoItem icon={Hospital} label="Establecimiento" value={result.personal.Des_EESS || 'Sin establecimiento'} />
          <InfoItem icon={ClipboardList} label="Provincia / Microred" value={`${result.personal.Desc_prov || '-'} / ${result.personal.Des_MicroRed || '-'}`} />
          <InfoItem icon={IdCard} label="CNV" value={result.personal.NumCNV} />
          <InfoItem icon={Hospital} label="RENAES" value={formatIdentifier(result.personal.pre_CodigoRENAES)} />
          <InfoItem
            icon={Timer}
            label="Peso / EG"
            value={`${result.personal.peso || '-'} g / ${result.personal.edadGEst || '-'} sem.`}
          />
        </div>

        <div className="grid gap-2 sm:grid-cols-2">
          {metrics.map((item) => (
            <div key={item.value} className="rounded-xl border border-base-300 bg-base-100 px-3 py-2 text-left">
              <p className="text-[0.65rem] font-bold uppercase tracking-[0.14em] text-base-content/55">{item.kicker}</p>
              <p className={`mt-0.5 text-lg font-black ${item.toneClass ?? 'text-primary'}`}>{item.metric}</p>
              <p className="mt-1 text-[0.68rem] font-bold text-base-content/55">{item.label}</p>
            </div>
          ))}
        </div>
      </div>
    </UsiCard>
  );
}

function SI02ComponentCard({ data }) {
  const deliveries = data.entregas ?? [];
  return (
    <div className="rounded-xl border border-clinic-violet/10 bg-white/70 p-4 transition hover:-translate-y-0.5 hover:shadow-soft">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-bold text-clinic-ink">{data.label || 'Componente'}</p>
          <p className="text-sm text-clinic-muted">Codigo: {data.codigo || '-'}</p>
          <p className="text-sm text-clinic-muted">Fecha: {formatDate(data.fecha)}</p>
          <p className="text-sm text-clinic-muted">
            Intervalo/edad: {data.intervalo_dias != null ? `${data.intervalo_dias} dias` : '-'}
          </p>
          <p className="text-sm text-clinic-muted">LAB: {data.lab || '-'}</p>
          <p className="text-sm text-clinic-muted">Ventana: {data.ventana_normativa || '-'}</p>
        </div>
        <StatusPill estado={data.estado} />
      </div>
      {deliveries.length > 0 && (
        <details className="mt-3 rounded-xl border border-clinic-border bg-white/80 p-3">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-3 text-sm font-bold text-clinic-ink">
            <span>
              {deliveries.length} entrega{deliveries.length === 1 ? '' : 's'} registrada
              {deliveries.length === 1 ? '' : 's'}
            </span>
            <ChevronDown className="h-4 w-4 text-clinic-violet" />
          </summary>
          <div className="mt-3 space-y-2">
            {deliveries.map((delivery) => (
              <div
                key={`${delivery.number}-${delivery.date}-${delivery.code}`}
                className="rounded-lg bg-clinic-mint/30 p-3 text-xs text-clinic-muted"
              >
                <div className="grid gap-2 sm:grid-cols-4">
                  <p>
                    <span className="block font-bold text-clinic-ink">Entrega {delivery.number}</span>
                    {formatDate(delivery.date)}
                  </p>
                  <p>
                    <span className="block font-bold text-clinic-ink">Codigo</span>
                    {delivery.code || '-'}
                  </p>
                  <p>
                    <span className="block font-bold text-clinic-ink">LAB</span>
                    {delivery.lab || '-'}
                  </p>
                  <p>
                    <span className="block font-bold text-clinic-ink">Intervalo</span>
                    {delivery.interval != null ? `${delivery.interval} dias` : '-'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </details>
      )}
      <DetailMessage item={data} />
    </div>
  );
}

function SearchDNI({
  selectedProvince,
  selectedIndicator,
  selectedSi02Subindicator = 'all',
}) {
  const { dni, setDni, result, error, loading, search } = useDniSearch(
    selectedProvince,
    selectedIndicator,
    selectedSi02Subindicator,
  );

  const isMc02 = selectedIndicator === 'mc02';
  const isSi02 = selectedIndicator === 'si02';
  const selectedSubindicatorInfo = (indicators.si02.subindicators ?? []).find((item) => item.code === selectedSi02Subindicator);
  const searchLabel = isMc02 || isSi02 ? 'DNI o CNV del niño' : 'DNI del recien nacido';
  const packageTitle = isMc02
    ? 'Paquete integrado MC-02'
    : isSi02 && selectedSubindicatorInfo
    ? `${selectedSubindicatorInfo.officialCode} ${selectedSubindicatorInfo.title}`
    : isSi02
    ? 'Subindicadores SI-02'
    : 'Componentes del paquete';
  const packageIcon = isMc02 ? PackageCheck : Syringe;
  const finalCompleteText = isMc02
    ? 'Paquete integrado completo'
    : isSi02
    ? selectedSubindicatorInfo
      ? 'El subindicador consultado cumple'
      : 'Todos los subindicadores encontrados cumplen'
    : 'Paquete completo';
  const finalIncompleteText = isMc02
    ? 'Paquete integrado incompleto, requiere seguimiento'
    : isSi02
    ? selectedSubindicatorInfo
      ? 'El subindicador consultado requiere seguimiento'
      : 'Tiene subindicadores con observaciones'
    : 'Paquete incompleto, requiere intervencion';
  const clinicalMetrics = result
    ? [
        {
          value: isSi02 ? 'subindicators' : 'components',
          label: isSi02 ? 'Subindicadores' : 'Componentes',
          kicker: isSi02 ? 'SI-02' : 'Paquete',
          metric: isSi02 ? result.subindicators?.length ?? 0 : Object.keys(result.vacunas ?? {}).length,
          toneClass: 'text-secondary',
        },
        ...(!isMc02 && !isSi02
          ? [
              {
                value: 'cred',
                label: 'Controles CRED',
                kicker: 'CRED',
                metric: result.cred_controls?.length ?? 0,
                toneClass: 'text-primary',
              },
              {
                value: 'tamizaje',
                label: 'Tamizaje',
                kicker: 'Neonatal',
                metric: result.tamizaje?.estado === 'cumple' ? 'OK' : 'Obs.',
                toneClass: result.tamizaje?.estado === 'cumple' ? 'text-success' : 'text-warning',
              },
            ]
          : []),
        ...(result.clinical_alerts?.length
          ? [
              {
                value: 'alerts',
                label: 'Alertas',
                kicker: 'Clinica',
                metric: result.clinical_alerts.length,
                toneClass: 'text-error',
              },
            ]
          : []),
      ]
    : [];

  const handleSearchSubmit = (event) => {
    event.preventDefault();
    search();
  };

  return (
    <section className="space-y-5">
      <SectionPanel className="p-5 lg:p-6">
        <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_18rem] lg:items-end">
          <div className="space-y-4">
            <form onSubmit={handleSearchSubmit} className="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-end">
              <div>
                <label htmlFor="dni" className="text-sm font-bold uppercase tracking-[0.16em] text-clinic-muted">
                  {searchLabel}
                </label>
                <div className="relative mt-2">
                  <IdCard className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-clinic-teal" />
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
                className="icon-button btn-primary w-full px-6 py-3 disabled:opacity-50 lg:w-auto"
              >
                {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Search className="h-5 w-5" />}
                {loading ? 'Buscando...' : 'Buscar'}
              </button>
            </form>
          </div>

          <div className="rounded-lg border border-clinic-line bg-clinic-sky/70 p-4">
            {/* <p className="text-xs font-bold uppercase text-clinic-muted">Consulta nominal</p> */}
            <p className="text-sm leading-6 text-clinic-muted">
              {isSi02 && selectedSubindicatorInfo
                ? `Consulta solo ${selectedSubindicatorInfo.officialCode} para revisar sus atenciones y observaciones.`
                : 'Busqueda para revisar paquete, ventanas normativas, atenciones registradas y alertas.'}
            </p>
          </div>
        </div>
      </SectionPanel>

      {error && (
        <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 font-semibold text-red-700">
          <span className="inline-flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            {error}
          </span>
        </div>
      )}

      {result && (
        <div className="animate-slide-up space-y-5">
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_22rem]">
            <PatientSummaryCard
              result={result}
              metrics={clinicalMetrics}
            />
            <PackageStatusBanner
              complete={result.paquete_completo}
              completeText={finalCompleteText}
              incompleteText={finalIncompleteText}
            />
          </div>

          <section>
            <SectionPanel className="p-5">
              <SectionTitle icon={packageIcon} title={packageTitle} />

              <div className="mt-5 space-y-5">
                {result.clinical_alerts?.length > 0 && (
                  <article className="rounded-xl border border-warning/30 bg-warning/10 p-5 text-warning">
                    <h3 className="inline-flex items-center gap-2 text-lg font-bold text-primary">
                      <AlertTriangle className="h-5 w-5 text-warning" />
                      Alertas clinicas
                    </h3>
                    <div className="mt-3 space-y-2 text-sm font-semibold leading-6 text-base-content/70">
                      {result.clinical_alerts.map((alert) => (
                        <p key={alert}>{alert}</p>
                      ))}
                    </div>
                  </article>
                )}

                {isSi02 && (
                  <div className="space-y-4">
                    {(result.subindicators ?? []).map((section) => (
                      <section key={section.subindicator_code} className="rounded-xl border border-base-300 bg-base-100 p-4">
                        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                          <div>
                            <p className="text-xs font-bold uppercase tracking-[0.14em] text-clinic-muted">
                              {section.subindicator_code}
                            </p>
                            <h3 className="mt-1 text-lg font-bold text-primary">{section.subindicator_name}</h3>
                          </div>
                          <StatusPill estado={section.complete ? 'cumple' : 'no_cumple'} />
                        </div>
                        <div className="mt-4 grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
                          {Object.entries(section.details ?? {}).map(([componentKey, data]) => (
                            <SI02ComponentCard key={`${section.subindicator_code}-${componentKey}`} data={data} />
                          ))}
                        </div>
                      </section>
                    ))}
                  </div>
                )}

                {!isSi02 && result.vacunas && (
                  <div className="grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
                    {Object.entries(result.vacunas).map(([vacuna, data]) => {
                      const label = componentLabels[vacuna] ?? vacuna;
                      const isHemoglobin = isMc02 && vacuna === 'hemoglobina';
                      const isIron = isMc02 && vacuna.startsWith('hierro_');
                      const vaccineDoseCount = registeredDoseCount(data);
                      const hasIronDelivery = isIron && Boolean(data.fecha);
                      const deliveryCount = data.entregas?.length || (hasIronDelivery ? 1 : 0);
                      const hasAnemiaAlert = Boolean(result.clinical_alerts?.length);
                      const fallbackIronType =
                        vacuna === 'hierro_menor_6m'
                          ? 'Preventiva 4 meses'
                          : hasAnemiaAlert
                          ? 'Tratamiento de anemia'
                          : 'Preventiva 6 a 11 meses';
                      const ironType =
                        data.entregas?.[0]?.tipo || data.tipo_atencion || (hasIronDelivery ? fallbackIronType : null);
                      const displayCode = data.codigo && data.codigo !== label ? data.codigo : '-';
                      return (
                        <div key={vacuna} className="rounded-xl border border-base-300 bg-base-100 p-4 transition hover:-translate-y-0.5 hover:border-secondary hover:shadow-soft">
                          <div className="flex items-start justify-between gap-4">
                            <div>
                              <p className="font-bold text-primary">{label}</p>
                              <p className="text-sm text-clinic-muted">Codigo: {displayCode}</p>
                              {!isHemoglobin && !isIron && (
                                <p className="text-sm text-clinic-muted">Dosis registradas: {vaccineDoseCount}</p>
                              )}
                              {isIron && <p className="text-sm text-clinic-muted">Entregas registradas: {deliveryCount}</p>}
                              <p className="text-sm text-clinic-muted">
                                {isHemoglobin ? 'Fecha dosaje' : isIron ? 'Fecha entrega' : 'Ultima fecha'}:{' '}
                                {formatDate(data.fecha)}
                              </p>
                              {isHemoglobin && (
                                <p className="text-sm text-clinic-muted">
                                  Edad al dosaje: {data.edad_atencion_dias != null ? `${data.edad_atencion_dias} dias` : '-'}
                                </p>
                              )}
                              {isIron && (
                                <p className="text-sm text-clinic-muted">
                                  Edad a la entrega: {data.edad_atencion_dias != null ? `${data.edad_atencion_dias} dias` : '-'}
                                </p>
                              )}
                              {isIron && <p className="text-sm text-clinic-muted">Tipo: {ironType || '-'}</p>}
                              {isIron && <p className="text-sm text-clinic-muted">Resultado Excel: {data.resultado || '-'}</p>}
                              <p className="text-sm text-clinic-muted">EESS atencion: {data.establecimiento_atencion || '-'}</p>
                              <p className="text-sm text-clinic-muted">Profesional: {data.profesional || '-'}</p>
                            </div>
                            <StatusPill estado={data.estado} />
                          </div>
                          {isHemoglobin ? (
                            <HemoglobinDetails data={data} />
                          ) : isIron ? (
                            <IronDetails data={data} />
                          ) : (
                            <DoseDetails doses={data.dosis} />
                          )}
                          <DetailMessage item={data} />
                        </div>
                      );
                    })}
                  </div>
                )}

                {!isMc02 && !isSi02 && result.cred_controls?.length > 0 && (
                  <section className="space-y-3">
                    <SectionTitle icon={ClipboardList} title="Controles CRED" />
                    <div className="grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
                      {result.cred_controls.map((cred) => (
                        <div key={cred.numero} className="rounded-xl border border-base-300 bg-base-100 p-4 transition hover:-translate-y-0.5 hover:border-secondary hover:shadow-soft">
                          <div className="flex items-start justify-between gap-3">
                            <div>
                              <p className="font-bold text-primary">CRED {cred.numero}</p>
                              <p className="mt-2 text-sm text-clinic-muted">Fecha: {formatDate(cred.fecha)}</p>
                              <p className="text-sm text-clinic-muted">Edad: {cred.edad_atencion_dias ?? '-'} dias</p>
                            </div>
                            <StatusPill estado={cred.estado} />
                          </div>
                          <DetailMessage item={cred} />
                        </div>
                      ))}
                    </div>
                  </section>
                )}

                {!isMc02 && !isSi02 && result.tamizaje && (
                  <section className="space-y-3">
                    <SectionTitle icon={TestTube2} title="Tamizaje neonatal" />
                    <div className="rounded-xl border border-base-300 bg-base-100 p-4">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="text-sm text-clinic-muted">Fecha: {formatDate(result.tamizaje.fecha)}</p>
                          <p className="text-sm text-clinic-muted">Edad: {result.tamizaje.edad_atencion_dias ?? '-'} dias</p>
                        </div>
                        <StatusPill estado={result.tamizaje.estado} />
                      </div>
                      <DetailMessage item={result.tamizaje} />
                    </div>
                  </section>
                )}
              </div>
            </SectionPanel>
          </section>
        </div>
      )}
    </section>
  );
}

export default SearchDNI;
