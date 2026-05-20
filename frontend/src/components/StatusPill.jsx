import { AlertTriangle, CalendarClock, CheckCircle2, Timer, XCircle } from 'lucide-react';

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

export default function StatusPill({ estado = 'pendiente' }) {
  const Icon = statusIcons[estado] ?? statusIcons.pendiente;
  return (
    <span
      className={`inline-flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1 text-sm font-bold ring-1 ${
        statusStyles[estado] ?? statusStyles.pendiente
      }`}
    >
      <Icon className="h-4 w-4" />
      {statusLabels[estado] ?? statusLabels.pendiente}
    </span>
  );
}
