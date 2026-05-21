import { ChevronDown } from 'lucide-react';
import { formatShortDate } from '../utils/dates';

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

function formatDate(value) {
  return formatShortDate(value);
}

export default function DoseDetails({ doses = [] }) {
  if (!doses.length) return null;
  const registeredCount = doses.filter((dose) => dose.registrada).length;
  const issueCount = doses.filter((dose) => !dose.cumple).length;
  const summaryText =
    registeredCount > 0
      ? `${registeredCount} dosis registrada${registeredCount === 1 ? '' : 's'}${
          issueCount ? ` / ${issueCount} con observacion` : ''
        }`
      : `${issueCount || doses.length} dosis requerida${(issueCount || doses.length) === 1 ? '' : 's'} sin registro`;

  return (
    <details className="mt-3 rounded-xl border border-clinic-border bg-white/80 p-3">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 text-sm font-bold text-clinic-ink">
        <span>{summaryText}</span>
        <ChevronDown className="h-4 w-4 text-clinic-violet" />
      </summary>
      <div className="mt-3 space-y-2">
        {doses.map((dose) => (
          <div
            key={`${dose.label}-${dose.fecha}-${dose.codigo}`}
            className="rounded-lg bg-clinic-mint/30 p-3 text-xs text-clinic-muted"
          >
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
              <span
                className={`inline-flex w-fit items-center rounded-full px-2.5 py-1 font-bold ring-1 ${
                  doseStatusStyles[dose.estado] ?? doseStatusStyles.no_requerida
                }`}
              >
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
