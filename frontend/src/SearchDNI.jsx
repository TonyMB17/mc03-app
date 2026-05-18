import { useState } from 'react';
import api from './api/client';
import {
  AlertTriangle,
  Baby,
  CalendarClock,
  ChevronDown,
  CheckCircle2,
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
  XCircle,
} from 'lucide-react';
import { formatShortDate } from './utils/dates';

const statusStyles = {
  cumple: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  advertencia: 'bg-amber-50 text-amber-700 ring-amber-200',
  programado: 'bg-blue-50 text-blue-700 ring-blue-200',
  incumplimiento: 'bg-red-50 text-red-700 ring-red-200',
  incumplimiento_fuera_plazo: 'bg-red-50 text-red-700 ring-red-200',
  no_cumple: 'bg-red-50 text-red-700 ring-red-200',
  pendiente: 'bg-slate-100 text-clinic-muted ring-slate-200',
  pendiente_en_plazo: 'bg-amber-50 text-amber-700 ring-amber-200',
};

const statusLabels = {
  cumple: 'Cumple',
  advertencia: 'En ventana',
  programado: 'Programado',
  incumplimiento: 'Incumple',
  incumplimiento_fuera_plazo: 'Fuera de plazo',
  no_cumple: 'No cumple',
  pendiente: 'Pendiente',
  pendiente_en_plazo: 'Pendiente en plazo',
};

const statusIcons = {
  cumple: CheckCircle2,
  advertencia: AlertTriangle,
  programado: CalendarClock,
  incumplimiento: XCircle,
  incumplimiento_fuera_plazo: XCircle,
  no_cumple: XCircle,
  pendiente: Timer,
  pendiente_en_plazo: AlertTriangle,
};

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

const doseStatusStyles = {
  registrada: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  registrada_no_exigible: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  no_registrada: 'bg-red-50 text-red-700 ring-red-200',
  fuera_plazo: 'bg-red-50 text-red-700 ring-red-200',
  no_requerida: 'bg-slate-100 text-clinic-muted ring-slate-200',
};

const doseStatusLabels = {
  registrada: 'Valida',
  registrada_no_exigible: 'Valida',
  no_registrada: 'No registrada',
  fuera_plazo: 'Fuera de plazo',
  no_requerida: 'No requerida',
};

function DoseDetails({ doses = [] }) {
  if (!doses.length) return null;
  const registeredCount = doses.filter((dose) => dose.registrada).length;
  const issueCount = doses.filter((dose) => !dose.cumple).length;
  const summaryText = registeredCount > 0
    ? `${registeredCount} dosis registrada${registeredCount === 1 ? '' : 's'}${issueCount ? ` / ${issueCount} con observacion` : ''}`
    : `${issueCount || doses.length} dosis requerida${(issueCount || doses.length) === 1 ? '' : 's'} sin registro`;

  return (
    <details className="mt-3 rounded-xl border border-clinic-border bg-white/80 p-3">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 text-sm font-bold text-clinic-ink">
        <span>{summaryText}</span>
        <ChevronDown className="h-4 w-4 text-clinic-violet" />
      </summary>
      <div className="mt-3 space-y-2">
        {doses.map((dose) => (
          <div key={`${dose.label}-${dose.fecha}-${dose.codigo}`} className="rounded-lg bg-clinic-mint/30 p-3 text-xs text-clinic-muted">
            <div className="grid gap-2 sm:grid-cols-[0.7fr_1fr_0.8fr_auto] sm:items-start">
              <p>
                <span className="block font-bold text-clinic-ink">{dose.label}</span>
                {formatDate(dose.fecha)}
              </p>
              <p>
                <span className="block font-bold text-clinic-ink">Codigo</span>
                {dose.codigo || '-'}{dose.lab ? ` - LAB ${dose.lab}` : ''}
              </p>
              <p>
                <span className="block font-bold text-clinic-ink">Edad</span>
                {dose.edad_atencion_dias ?? '-'} dias
              </p>
              <span className={`inline-flex w-fit items-center rounded-full px-2.5 py-1 font-bold ring-1 ${doseStatusStyles[dose.estado] ?? doseStatusStyles.no_requerida}`}>
                {doseStatusLabels[dose.estado] ?? dose.estado}
              </span>
            </div>
            {!dose.cumple && (dose.ventana_inicio || dose.ventana_fin) && (
              <p className="mt-2 rounded-md bg-white/70 px-2 py-1 font-semibold text-clinic-muted">
                Ventana de esta dosis: {formatDate(dose.ventana_inicio)} - {formatDate(dose.ventana_fin)}
              </p>
            )}
            {dose.motivo && !dose.cumple && (
              <p className="mt-2 rounded-md bg-white/70 px-2 py-1 font-semibold text-clinic-muted">{dose.motivo}</p>
            )}
          </div>
        ))}
      </div>
    </details>
  );
}

function HemoglobinDetails({ data }) {
  const isProgrammed = data.estado === 'programado';
  const hasWindow = data.fecha_inicio || data.fecha_limite;
  if (data.cumple && !isProgrammed) return null;
  if (!hasWindow && !data.fecha && data.edad_atencion_dias == null) return null;

  if (isProgrammed) {
    return (
      <div className="mt-3 rounded-xl border border-clinic-border bg-clinic-mint/25 p-3 text-sm text-clinic-muted">
        <span className="block text-xs font-bold uppercase tracking-[0.12em] text-clinic-muted">Ventana programada del dosaje</span>
        <span className="font-bold text-clinic-ink">{formatDate(data.fecha_inicio)} - {formatDate(data.fecha_limite)}</span>
        <span className="ml-2 text-clinic-muted">(170 a 209 dias)</span>
      </div>
    );
  }

  return (
    <div className="mt-3 grid gap-2 rounded-xl border border-clinic-border bg-clinic-mint/25 p-3 text-sm text-clinic-muted sm:grid-cols-2">
      <p>
        <span className="block text-xs font-bold uppercase tracking-[0.12em] text-clinic-muted">Fecha de dosaje</span>
        <span className="font-bold text-clinic-ink">{formatDate(data.fecha)}</span>
      </p>
      <p>
        <span className="block text-xs font-bold uppercase tracking-[0.12em] text-clinic-muted">Edad al dosaje</span>
        <span className="font-bold text-clinic-ink">
          {data.edad_atencion_dias ?? '-'}{data.edad_atencion_dias != null ? ' dias' : ''}
        </span>
      </p>
      {hasWindow && (
        <p className="sm:col-span-2">
          <span className="block text-xs font-bold uppercase tracking-[0.12em] text-clinic-muted">Ventana valida del dosaje</span>
          <span className="font-bold text-clinic-ink">{formatDate(data.fecha_inicio)} - {formatDate(data.fecha_limite)}</span>
          <span className="ml-2 text-clinic-muted">(170 a 209 dias)</span>
        </p>
      )}
    </div>
  );
}

function IronDetails({ data }) {
  const deliveries = data.entregas ?? [];
  if (!deliveries.length || (data.cumple && deliveries.length <= 1)) return null;

  return (
    <details className="mt-3 rounded-xl border border-clinic-border bg-white/80 p-3">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 text-sm font-bold text-clinic-ink">
        <span>{deliveries.length} entrega{deliveries.length === 1 ? '' : 's'} registrada{deliveries.length === 1 ? '' : 's'}</span>
        <ChevronDown className="h-4 w-4 text-clinic-violet" />
      </summary>
      <div className="mt-3 space-y-2">
        {deliveries.map((delivery) => (
          <div key={`${delivery.label}-${delivery.fecha}-${delivery.codigo}`} className="rounded-lg bg-clinic-mint/30 p-3 text-xs text-clinic-muted">
            <div className="grid gap-2 sm:grid-cols-[0.8fr_1fr_0.8fr_0.8fr]">
              <p>
                <span className="block font-bold text-clinic-ink">{delivery.label}</span>
                {formatDate(delivery.fecha)}
              </p>
              <p>
                <span className="block font-bold text-clinic-ink">Tipo</span>
                {delivery.tipo || '-'}
              </p>
              <p>
                <span className="block font-bold text-clinic-ink">Codigo</span>
                {delivery.codigo || '-'}{delivery.lab ? ` - LAB ${delivery.lab}` : ''}
              </p>
              <p>
                <span className="block font-bold text-clinic-ink">Edad</span>
                {delivery.edad_atencion_dias ?? '-'} dias
              </p>
            </div>
            {(delivery.codigo_anemia || delivery.intervalo_dias || delivery.establecimiento_atencion) && (
              <p className="mt-2 rounded-md bg-white/70 px-2 py-1 font-semibold text-clinic-muted">
                {delivery.codigo_anemia ? `Dx anemia: ${delivery.codigo_anemia}. ` : ''}
                {delivery.intervalo_dias != null ? `Intervalo: ${delivery.intervalo_dias} dias. ` : ''}
                {delivery.establecimiento_atencion ? `EESS: ${delivery.establecimiento_atencion}.` : ''}
              </p>
            )}
          </div>
        ))}
      </div>
    </details>
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
          <p className="text-sm text-clinic-muted">Intervalo/edad: {data.intervalo_dias != null ? `${data.intervalo_dias} dias` : '-'}</p>
          <p className="text-sm text-clinic-muted">LAB: {data.lab || '-'}</p>
          <p className="text-sm text-clinic-muted">Ventana: {data.ventana_normativa || '-'}</p>
        </div>
        <StatusPill estado={data.estado} />
      </div>
      {deliveries.length > 0 && (
        <details className="mt-3 rounded-xl border border-clinic-border bg-white/80 p-3">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-3 text-sm font-bold text-clinic-ink">
            <span>{deliveries.length} entrega{deliveries.length === 1 ? '' : 's'} registrada{deliveries.length === 1 ? '' : 's'}</span>
            <ChevronDown className="h-4 w-4 text-clinic-violet" />
          </summary>
          <div className="mt-3 space-y-2">
            {deliveries.map((delivery) => (
              <div key={`${delivery.number}-${delivery.date}-${delivery.code}`} className="rounded-lg bg-clinic-mint/30 p-3 text-xs text-clinic-muted">
                <div className="grid gap-2 sm:grid-cols-4">
                  <p><span className="block font-bold text-clinic-ink">Entrega {delivery.number}</span>{formatDate(delivery.date)}</p>
                  <p><span className="block font-bold text-clinic-ink">Codigo</span>{delivery.code || '-'}</p>
                  <p><span className="block font-bold text-clinic-ink">LAB</span>{delivery.lab || '-'}</p>
                  <p><span className="block font-bold text-clinic-ink">Intervalo</span>{delivery.interval != null ? `${delivery.interval} dias` : '-'}</p>
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
  const [dni, setDni] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const isMc02 = selectedIndicator === 'mc02';
  const isSi02 = selectedIndicator === 'si02';
  const searchLabel = isMc02 || isSi02 ? 'DNI o CNV del niño' : 'DNI del recien nacido';
  const packageTitle = isMc02 ? 'Paquete integrado MC-02' : isSi02 ? 'Subindicadores SI-02' : 'Componentes del paquete';
  const packageIcon = isMc02 ? PackageCheck : Syringe;
  const finalCompleteText = isMc02 ? 'Paquete integrado completo' : isSi02 ? 'Todos los subindicadores encontrados cumplen' : 'Paquete completo';
  const finalIncompleteText = isMc02 ? 'Paquete integrado incompleto, requiere seguimiento' : isSi02 ? 'Tiene subindicadores con observaciones' : 'Paquete incompleto, requiere intervencion';

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
      const params = new URLSearchParams({ province: selectedProvince, indicator: selectedIndicator });
      const response = await api.get(`/api/search/dni/${dni.trim()}?${params.toString()}`);
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
              <InfoItem icon={CalendarClock} label="Fecha de nacimiento" value={formatDate(result.personal.fec_Nac)} />
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
                  <section key={section.subindicator_code} className="rounded-xl border border-clinic-border bg-white/70 p-4">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <p className="text-xs font-bold uppercase tracking-[0.14em] text-clinic-muted">{section.subindicator_code}</p>
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
                  const registeredDoseCount = data.dosis_registradas ?? data.dosis?.filter((dose) => dose.registrada).length ?? 0;
                  const hasIronDelivery = isIron && Boolean(data.fecha);
                  const deliveryCount = data.entregas?.length || (hasIronDelivery ? 1 : 0);
                  const hasAnemiaAlert = Boolean(result.clinical_alerts?.length);
                  const fallbackIronType = vacuna === 'hierro_menor_6m'
                    ? 'Preventiva 4 meses'
                    : hasAnemiaAlert ? 'Tratamiento de anemia' : 'Preventiva 6 a 11 meses';
                  const ironType = data.entregas?.[0]?.tipo || data.tipo_atencion || (hasIronDelivery ? fallbackIronType : null);
                  const displayCode = data.codigo && data.codigo !== label ? data.codigo : '-';
                  return (
                    <div key={vacuna} className="rounded-xl border border-clinic-violet/10 bg-white/70 p-4 transition hover:-translate-y-0.5 hover:shadow-soft">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="font-bold text-clinic-ink">{label}</p>
                          <p className="text-sm text-clinic-muted">Codigo: {displayCode}</p>
                          {!isHemoglobin && !isIron && <p className="text-sm text-clinic-muted">Dosis registradas: {registeredDoseCount}</p>}
                          {isIron && <p className="text-sm text-clinic-muted">Entregas registradas: {deliveryCount}</p>}
                          <p className="text-sm text-clinic-muted">
                            {isHemoglobin ? 'Fecha dosaje' : isIron ? 'Fecha entrega' : 'Ultima fecha'}: {formatDate(data.fecha)}
                          </p>
                          {isHemoglobin && <p className="text-sm text-clinic-muted">Edad al dosaje: {data.edad_atencion_dias != null ? `${data.edad_atencion_dias} dias` : '-'}</p>}
                          {isIron && <p className="text-sm text-clinic-muted">Edad a la entrega: {data.edad_atencion_dias != null ? `${data.edad_atencion_dias} dias` : '-'}</p>}
                          {isIron && <p className="text-sm text-clinic-muted">Tipo: {ironType || '-'}</p>}
                          {isIron && <p className="text-sm text-clinic-muted">Resultado Excel: {data.resultado || '-'}</p>}
                          <p className="text-sm text-clinic-muted">EESS atencion: {data.establecimiento_atencion || '-'}</p>
                          <p className="text-sm text-clinic-muted">Profesional: {data.profesional || '-'}</p>
                        </div>
                        <StatusPill estado={data.estado} />
                      </div>
                      {isHemoglobin ? <HemoglobinDetails data={data} /> : isIron ? <IronDetails data={data} /> : <DoseDetails doses={data.dosis} />}
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
                  <div key={cred.numero} className="rounded-xl border border-clinic-violet/10 bg-white/70 p-4 transition hover:-translate-y-0.5 hover:shadow-soft">
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

          <article className={`rounded-xl border p-5 ${result.paquete_completo ? 'border-emerald-200 bg-emerald-50' : 'border-red-200 bg-red-50'}`}>
            <h3 className={`inline-flex items-center gap-2 text-lg font-bold ${result.paquete_completo ? 'text-emerald-700' : 'text-red-700'}`}>
              {result.paquete_completo ? <ShieldCheck className="h-5 w-5" /> : <ShieldAlert className="h-5 w-5" />}
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
