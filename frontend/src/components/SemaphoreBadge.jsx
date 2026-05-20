import { CheckCircle2, XCircle } from 'lucide-react';

const semaphoreStyles = {
  green: {
    badge: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
    border: 'border-emerald-300',
    dot: 'bg-emerald-500',
    icon: CheckCircle2,
    label: 'Cumple',
  },
  red: {
    badge: 'bg-red-50 text-red-700 ring-red-200',
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
    <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-bold ring-1 ${style.badge}`}>
      <Icon className="h-4 w-4" />
      {style.label}
    </span>
  );
}
