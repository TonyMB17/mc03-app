import { AlertTriangle, CalendarClock, CheckCircle2, Timer, XCircle } from 'lucide-react';

const statusStyles = {
  cumple: 'badge-success',
  advertencia: 'badge-warning',
  programado: 'badge-info',
  incumplimiento: 'badge-error',
  incumplimiento_fuera_plazo: 'badge-error',
  no_cumple: 'badge-error',
  pendiente: 'badge-ghost border-base-300 text-clinic-muted',
  pendiente_en_plazo: 'badge-warning',
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

export default function StatusPill({ estado = 'pendiente' }) {
  const Icon = statusIcons[estado] ?? statusIcons.pendiente;
  return (
    <span
      className={`badge badge-lg inline-flex h-auto shrink-0 items-center gap-1.5 px-3 py-1.5 text-sm font-bold ${
        statusStyles[estado] ?? statusStyles.pendiente
      }`}
    >
      <Icon className="h-4 w-4" />
      {statusLabels[estado] ?? statusLabels.pendiente}
    </span>
  );
}
