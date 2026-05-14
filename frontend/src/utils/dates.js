function parseLocalDate(value) {
  if (!value) return null;
  const text = String(value);
  const dateOnlyMatch = text.match(/^(\d{4})-(\d{2})-(\d{2})/);
  const date = dateOnlyMatch
    ? new Date(Number(dateOnlyMatch[1]), Number(dateOnlyMatch[2]) - 1, Number(dateOnlyMatch[3]))
    : new Date(text.replace(' ', 'T'));
  return Number.isNaN(date.getTime()) ? null : date;
}

export function formatShortDate(value) {
  const date = parseLocalDate(value);
  if (!date) return value || '-';

  const months = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'set', 'oct', 'nov', 'dic'];
  const day = String(date.getDate()).padStart(2, '0');
  return `${day} ${months[date.getMonth()]} ${date.getFullYear()}`;
}

export function formatPeruDate(value) {
  const date = parseLocalDate(value);
  if (!date) return value || '-';
  return date.toLocaleDateString('es-PE', { year: 'numeric', month: 'short', day: '2-digit' });
}
