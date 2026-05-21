import { CalendarDays } from 'lucide-react';

export default function PeriodBadge({ inVerificationPeriod, isCurrentEvaluationMonth = false, isMc02 = false }) {
  if (isCurrentEvaluationMonth) {
    return (
      <span className="badge badge-warning h-auto gap-1.5 px-3 py-1.5 text-xs font-bold uppercase tracking-[0.12em]">
        <CalendarDays className="h-3.5 w-3.5" />
        {isMc02 ? 'Cohorte en evaluacion' : 'Mes en evaluacion'}
      </span>
    );
  }

  return (
    <span
      className={`badge h-auto gap-1.5 px-3 py-1.5 text-xs font-bold uppercase tracking-[0.12em] ${
        inVerificationPeriod
          ? 'badge-primary'
          : 'badge-ghost border-base-300 text-clinic-muted'
      }`}
    >
      <CalendarDays className="h-3.5 w-3.5" />
      {inVerificationPeriod ? 'Verificacion' : 'Historico'}
    </span>
  );
}
