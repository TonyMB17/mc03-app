function IndicatorSelector({ indicators, value, onChange }) {
  return (
    <label className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-white/75">
      Indicador:
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="rounded-md border border-white/20 bg-white px-2 py-1 text-sm font-bold text-clinic-ink outline-none"
      >
        {indicators.map((indicator) => (
          <option key={indicator.code} value={indicator.code}>
            {indicator.shortName}
          </option>
        ))}
      </select>
    </label>
  );
}

export default IndicatorSelector;
