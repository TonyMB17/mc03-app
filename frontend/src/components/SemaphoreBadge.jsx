import { CheckCircle2, XCircle } from 'lucide-react';

const semaphoreStyles = {
  green: {
    badge: 'badge-success',
    border: 'border-emerald-300',
    dot: 'bg-emerald-500',
    icon: CheckCircle2,
    label: 'Cumple',
  },
  red: {
    badge: 'badge-error',
    border: 'border-red-300',
    dot: 'bg-red-500',
    icon: XCircle,
    label: 'No cumple',
  },
};

export default function SemaphoreBadge({ value }) {
  const style = semaphoreStyles[value] ?? semaphoreStyles.red;
  const Icon = style.icon;
  return (
    <span className={`badge badge-lg inline-flex h-auto items-center gap-1.5 px-3 py-1.5 text-sm font-bold ${style.badge}`}>
      <Icon className="h-4 w-4" />
      {style.label}
    </span>
  );
}
