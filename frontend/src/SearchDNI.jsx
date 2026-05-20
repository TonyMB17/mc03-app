import {
  AlertTriangle,
  Baby,
  CalendarClock,
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
  UserRound,
} from 'lucide-react';
import { useDniSearch } from './hooks/useDniSearch';
import StatusPill from './components/StatusPill';
import DoseDetails from './components/DoseDetails';
import HemoglobinDetails from './components/HemoglobinDetails';
import IronDetails from './components/IronDetails';
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
  hierro_menor_6m: 'Hierro menor de 6 meses',
  hierro_mayor_6m: 'Hierro mayor de 6 meses',
  hemoglobina: 'Dosaje de hemoglobina',
};

function formatDate(value) {
  return formatShortDate(value);
}

function DetailMessage({ item }) {
  if (item.cumple) return null;
  const showWindow = !item.cumple && (item.fecha_inicio || item.fecha_limite);
  return (
    <div className="mt-3 rounded-xl border border-clinic-violet/10 bg-clinic-mint/35 p-3">
      <p className="text-sm leading-6 text-clinic-muted">{item.mensaje}</p>
      {showWindow && (
        <p className="mt-2 inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.14em] text-clinic-muted">
          <Timer className="h-3.5 w-3.5 text-clinic-violet" />
          Servicio segun edad actual: {formatDate(item.fecha_inicio)} - {formatDate(item.fecha_limite)}
        </p>
      )}
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

function SearchDNI({ selectedProvince, selectedIndicator }) {
  const { dni, setDni, result, error, loading, search } = useDniSearch(
    selectedProvince,
    selectedIndicator,
  );

  const isMc02 = selectedIndicator === 'mc02';
  const isSi02 = selectedIndicator === 'si02';
  const searchLabel = isMc02 || isSi02 ? 'DNI o CNV del niño' : 'DNI del recien nacido';
  const packageTitle = isMc02 ? 'Paquete integrado MC-02' : isSi02 ? 'Subindicadores SI-02' : 'Componentes del paquete';
  const packageIcon = isMc02 ? PackageCheck : Syringe;
  const finalCompleteText = isMc02
    ? 'Paquete integrado completo'
    : isSi02
    ? 'Todos los subindicadores encontrados cumplen'
    : 'Paquete completo';
  const finalIncompleteText = isMc02
    ? 'Paquete integrado incompleto, requiere seguimiento'
    : isSi02
    ? 'Tiene subindicadores con observaciones'
    : 'Paquete incompleto, requiere intervencion';

  const handleSearchSubmit = (event) => {
    event.preventDefault();
    search();
  };

  return (
    <section className="panel p-5 lg:p-6">
      <form onSubmit={handleSearchSubmit} className="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-end">
        <div>
          <label htmlFor="dni" className="text-sm font-bold uppercase tracking-[0.18em] text-clinic-muted">
            {searchLabel}
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
            <AlertTriangle className="h-5 w-5" />
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
                value={[
                  result.personal.afi_nombres,
                  result.personal.afi_appaterno,
                  result.personal.afi_apmaterno,
                ]
                  .filter(Boolean)
                  .join(' ')}
              />
              <InfoItem icon={CalendarClock} label="Fecha de nacimiento" value={formatDate(result.personal.fec_Nac)} />
              <InfoItem
                icon={Timer}
                label="Peso / EG"
                value={`${result.personal.peso || '-'} g / ${result.personal.edadGEst || '-'} sem.`}
              />
              <div className="rounded-xl border border-clinic-violet/10 bg-white/62 p-4">
                <p className="inline-flex items-center gap-2 text-sm font-semibold text-clinic-muted">
                  <Hospital className="h-4 w-4 text-clinic-violet" />
                  Establecimiento
                </p>
                <p className="mt-2 font-bold text-clinic-ink">{result.personal.Des_EESS || 'Sin establecimiento'}</p>
                <p className="mt-1 text-xs text-clinic-muted">
                  {result.personal.Desc_prov || '-'} / {result.personal.Des_MicroRed || '-'} / RENAES{' '}
                  {result.personal.pre_CodigoRENAES || '-'}
                </p>
              </div>
            </div>
          </article>

          {result.clinical_alerts?.length > 0 && (
            <article className="rounded-xl border border-amber-200 bg-amber-50 p-5 text-amber-900">
              <h3 className="inline-flex items-center gap-2 text-lg font-bold">
                <AlertTriangle className="h-5 w-5" />
                Alertas clinicas
              </h3>
              <div className="mt-3 space-y-2 text-sm font-semibold leading-6">
                {result.clinical_alerts.map((alert) => (
                  <p key={alert}>{alert}</p>
                ))}
              </div>
            </article>
          )}

          {isSi02 && result.subindicators?.length > 0 ? (
            <article className="inner-panel p-5">
              <SectionTitle icon={packageIcon} title={packageTitle} />
              <div className="mt-4 space-y-4">
                {result.subindicators.map((section) => (
                  <section
                    key={section.subindicator_code}
                    className="rounded-xl border border-clinic-border bg-white/70 p-4"
                  >
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <p className="text-xs font-bold uppercase tracking-[0.14em] text-clinic-muted">
                          {section.subindicator_code}
                        </p>
                        <h3 className="mt-1 text-lg font-bold text-clinic-ink">{section.subindicator_name}</h3>
                      </div>
                      <StatusPill estado={section.complete ? 'cumple' : 'no_cumple'} />
                    </div>
                    <div className="mt-4 grid gap-4 md:grid-cols-2">
                      {Object.entries(section.details ?? {}).map(([componentKey, data]) => (
                        <SI02ComponentCard key={`${section.subindicator_code}-${componentKey}`} data={data} />
                      ))}
                    </div>
                  </section>
                ))}
              </div>
            </article>
          ) : (
            <article className="inner-panel p-5">
              <SectionTitle icon={packageIcon} title={packageTitle} />
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                {Object.entries(result.vacunas).map(([vacuna, data]) => {
                  const label = componentLabels[vacuna] ?? vacuna;
                  const isHemoglobin = isMc02 && vacuna === 'hemoglobina';
                  const isIron = isMc02 && vacuna.startsWith('hierro_');
                  const registeredDoseCount =
                    data.dosis_registradas ?? data.dosis?.filter((dose) => dose.registrada).length ?? 0;
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
                    <div
                      key={vacuna}
                      className="rounded-xl border border-clinic-violet/10 bg-white/70 p-4 transition hover:-translate-y-0.5 hover:shadow-soft"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="font-bold text-clinic-ink">{label}</p>
                          <p className="text-sm text-clinic-muted">Codigo: {displayCode}</p>
                          {!isHemoglobin && !isIron && (
                            <p className="text-sm text-clinic-muted">Dosis registradas: {registeredDoseCount}</p>
                          )}
                          {isIron && <p className="text-sm text-clinic-muted">Entregas registradas: {deliveryCount}</p>}
                          <p className="text-sm text-clinic-muted">
                            {isHemoglobin ? 'Fecha dosaje' : isIron ? 'Fecha entrega' : 'Ultima fecha'}:{' '}
                            {formatDate(data.fecha)}
                          </p>
                          {isHemoglobin && (
                            <p className="text-sm text-clinic-muted">
                              Edad al dosaje:{' '}
                              {data.edad_atencion_dias != null ? `${data.edad_atencion_dias} dias` : '-'}
                            </p>
                          )}
                          {isIron && (
                            <p className="text-sm text-clinic-muted">
                              Edad a la entrega:{' '}
                              {data.edad_atencion_dias != null ? `${data.edad_atencion_dias} dias` : '-'}
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
            </article>
          )}

          {!isMc02 && !isSi02 && (
            <article className="inner-panel p-5">
              <SectionTitle icon={ClipboardList} title="Controles CRED" />
              <div className="mt-4 grid gap-4 xl:grid-cols-3">
                {result.cred_controls.map((cred) => (
                  <div
                    key={cred.numero}
                    className="rounded-xl border border-clinic-violet/10 bg-white/70 p-4 transition hover:-translate-y-0.5 hover:shadow-soft"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-bold text-clinic-ink">CRED {cred.numero}</p>
                        <p className="mt-2 text-sm text-clinic-muted">Fecha: {formatDate(cred.fecha)}</p>
                        <p className="text-sm text-clinic-muted">Edad: {cred.edad_atencion_dias ?? '-'} dias</p>
                      </div>
                      <StatusPill estado={cred.estado} />
                    </div>
                    <DetailMessage item={cred} />
                  </div>
                ))}
              </div>
            </article>
          )}

          {!isMc02 && !isSi02 && (
            <article className="inner-panel p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <SectionTitle icon={TestTube2} title="Tamizaje neonatal" />
                  <p className="mt-4 text-sm text-clinic-muted">Fecha: {formatDate(result.tamizaje.fecha)}</p>
                  <p className="text-sm text-clinic-muted">Edad: {result.tamizaje.edad_atencion_dias ?? '-'} dias</p>
                </div>
                <StatusPill estado={result.tamizaje.estado} />
              </div>
              <DetailMessage item={result.tamizaje} />
            </article>
          )}

          <article
            className={`rounded-xl border p-5 ${
              result.paquete_completo ? 'border-emerald-200 bg-emerald-50' : 'border-red-200 bg-red-50'
            }`}
          >
            <h3
              className={`inline-flex items-center gap-2 text-lg font-bold ${
                result.paquete_completo ? 'text-emerald-700' : 'text-red-700'
              }`}
            >
              {result.paquete_completo ? <ShieldCheck className="h-5 w-5" /> : <AlertTriangle className="h-5 w-5" />}
              Estado del paquete
            </h3>
            <p className={`mt-2 text-sm font-semibold ${result.paquete_completo ? 'text-emerald-700' : 'text-red-700'}`}>
              {result.paquete_completo ? finalCompleteText : finalIncompleteText}
            </p>
          </article>
        </div>
      )}
    </section>
  );
}

export default SearchDNI;
