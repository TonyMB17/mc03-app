import { CalendarDays } from 'lucide-react';

export default function PeriodBadge({ inVerificationPeriod, isCurrentEvaluationMonth = false, isMc02 = false }) {
  if (isCurrentEvaluationMonth) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-3 py-1 text-xs font-bold uppercase tracking-[0.12em] text-amber-800 ring-1 ring-amber-200">
        <CalendarDays className="h-3.5 w-3.5" />
        {isMc02 ? 'Cohorte en evaluacion' : 'Mes en evaluacion'}
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold uppercase tracking-[0.12em] ${
        inVerificationPeriod
          ? 'bg-clinic-mint text-clinic-teal ring-1 ring-teal-100'
          : 'bg-slate-100 text-clinic-muted ring-1 ring-slate-200'
      }`}
    >
      <CalendarDays className="h-3.5 w-3.5" />
      {inVerificationPeriod ? 'Verificacion' : 'Historico'}
    </span>
  );
}
