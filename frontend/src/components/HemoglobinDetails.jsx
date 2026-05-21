import { formatShortDate } from '../utils/dates';

function formatDate(value) {
  return formatShortDate(value);
}

export default function HemoglobinDetails({ data }) {
  const isProgrammed = data.estado === 'programado';
  const hasWindow = data.fecha_inicio || data.fecha_limite;
  if (data.cumple && !isProgrammed) return null;
  if (!hasWindow && !data.fecha && data.edad_atencion_dias == null) return null;

  if (isProgrammed) {
    return (
      <div className="mt-3 rounded-xl border border-clinic-border bg-clinic-mint/25 p-3 text-sm text-clinic-muted">
        <span className="block text-xs font-bold uppercase tracking-[0.12em] text-clinic-muted">
          Ventana programada del dosaje
        </span>
        <span className="font-bold text-clinic-ink">
          {formatDate(data.fecha_inicio)} - {formatDate(data.fecha_limite)}
        </span>
        <span className="ml-2 text-clinic-muted">(170 a 209 dias)</span>
      </div>
    );
  }

  return (
    <div className="mt-3 grid gap-2 rounded-xl border border-clinic-border bg-clinic-mint/25 p-3 text-sm text-clinic-muted sm:grid-cols-2">
      <p>
        <span className="block text-xs font-bold uppercase tracking-[0.12em] text-clinic-muted">
          Fecha de dosaje
        </span>
        <span className="font-bold text-clinic-ink">{formatDate(data.fecha)}</span>
      </p>
      <p>
        <span className="block text-xs font-bold uppercase tracking-[0.12em] text-clinic-muted">
          Edad al dosaje
        </span>
        <span className="font-bold text-clinic-ink">
          {data.edad_atencion_dias ?? '-'}{data.edad_atencion_dias != null ? ' dias' : ''}
        </span>
      </p>
      {hasWindow && (
        <p className="sm:col-span-2">
          <span className="block text-xs font-bold uppercase tracking-[0.12em] text-clinic-muted">
            Ventana valida del dosaje
          </span>
          <span className="font-bold text-clinic-ink">
            {formatDate(data.fecha_inicio)} - {formatDate(data.fecha_limite)}
          </span>
          <span className="ml-2 text-clinic-muted">(170 a 209 dias)</span>
        </p>
      )}
    </div>
  );
}
