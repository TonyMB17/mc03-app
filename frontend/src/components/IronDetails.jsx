import { ChevronDown } from 'lucide-react';
import { formatShortDate } from '../utils/dates';

function formatDate(value) {
  return formatShortDate(value);
}

export default function IronDetails({ data }) {
  const deliveries = data.entregas ?? [];
  if (!deliveries.length || (data.cumple && deliveries.length <= 1)) return null;

  return (
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
            key={`${delivery.label}-${delivery.fecha}-${delivery.codigo}`}
            className="rounded-lg bg-clinic-mint/30 p-3 text-xs text-clinic-muted"
          >
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
