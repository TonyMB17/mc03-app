import { useEffect, useState } from 'react';
import api from './api/client';
import { CheckCircle2, Filter, Goal, Info, Layers3, MapPin, ShieldCheck, SlidersHorizontal, XCircle } from 'lucide-react';
import SectionPanel from './components/SectionPanel';

const ALL_PROVINCES = '__ALL__';
const DEFAULT_TARGET_COVERAGE = 70.7;

const cardToneStyles = {
  teal: 'border-base-300 bg-base-100 text-secondary',
  blue: 'border-base-300 bg-base-100 text-info',
  violet: 'border-base-300 bg-base-100 text-accent',
  amber: 'border-base-300 bg-base-100 text-warning',
};

function ConfigCard({ icon: Icon, title, children, tone = 'teal' }) {
  return (
    <div className={`card rounded-xl border p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-soft ${cardToneStyles[tone] ?? cardToneStyles.teal}`}>
      <div className="flex items-center gap-3">
        <span className="grid h-10 w-10 place-items-center rounded-xl bg-base-200 ring-1 ring-current/20">
          <Icon className="h-5 w-5" />
        </span>
        <h3 className="font-black text-primary">{title}</h3>
      </div>
      <div className="mt-4 text-clinic-ink">{children}</div>
    </div>
  );
}

function ParameterCard({ icon: Icon, label, value, helper, tone = 'teal' }) {
  return (
    <div className={`stat rounded-xl border p-4 shadow-sm ${cardToneStyles[tone] ?? cardToneStyles.teal}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.16em] opacity-70">{label}</p>
          <p className="mt-2 break-words text-2xl font-bold text-clinic-ink">{value}</p>
        </div>
        <Icon className="h-5 w-5 shrink-0" />
      </div>
      <p className="mt-2 text-sm font-semibold leading-5 text-clinic-muted">{helper}</p>
    </div>
  );
}

function ConfigView({ selectedIndicator, selectedProvince, onProvinceChange, targetCoverage, onTargetCoverageChange }) {
  const [options, setOptions] = useState({
    provinces: [],
    default_province: 'ABANCAY',
    default_target_coverage: DEFAULT_TARGET_COVERAGE,
    included_insurance_types: [],
    exclusion_criteria: {},
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .get(`/api/config/options?indicator=${selectedIndicator}`)
      .then((response) => {
        setOptions(response.data);
        onProvinceChange(response.data.default_province ?? 'ABANCAY');
        onTargetCoverageChange(response.data.default_target_coverage ?? DEFAULT_TARGET_COVERAGE);
      })
      .catch((err) => {
        setError(err.message);
      });
  }, [selectedIndicator]);

  const isAllData = selectedProvince === ALL_PROVINCES;
  const boundedTarget = Math.max(0, Math.min(100, Number(targetCoverage) || 0));

  const handleTargetChange = (event) => {
    const value = Number(event.target.value);
    if (Number.isNaN(value)) return;
    onTargetCoverageChange(Math.max(0, Math.min(100, value)));
  };

  return (
    <section className="space-y-5">
      <SectionPanel className="overflow-hidden">
        <div className="grid lg:grid-cols-[0.95fr_1.05fr]">
          <div className="bg-primary p-5 text-primary-content lg:p-6">
            <div className="flex items-start gap-3">
              <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-white/15 ring-1 ring-white/20">
                <SlidersHorizontal className="h-5 w-5" />
              </span>
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-primary-content/70">Parametros operativos</p>
                <h2 className="mt-1 text-2xl font-black">Poblacion objetivo</h2>
                <p className="mt-2 max-w-xl text-sm font-semibold leading-6 text-primary-content/80">
                  Provincia, meta, seguros y reglas que gobiernan dashboard, busqueda nominal y descargas.
                </p>
              </div>
            </div>
          </div>

          <div className="grid gap-3 bg-base-200 p-4 md:grid-cols-3">
            <ParameterCard
              icon={MapPin}
              label="Provincia"
              value={isAllData ? 'Todos' : selectedProvince}
              helper={isAllData ? 'Corte regional completo' : 'Filtro territorial activo'}
              tone="blue"
            />
            <ParameterCard
              icon={Goal}
              label="Meta"
              value={`${targetCoverage}%`}
              helper="Umbral del semaforo"
              tone="teal"
            />
            <ParameterCard
              icon={Layers3}
              label="Seguros"
              value={options.included_insurance_types.length}
              helper="Tipos incluidos"
              tone="violet"
            />
          </div>
        </div>

        <div className="p-5 lg:p-6">
          {error && (
            <div className="alert alert-error rounded-xl text-sm font-semibold">
              No se pudieron cargar las opciones: {error}
            </div>
          )}

          <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
            <div className="rounded-xl border border-base-300 bg-base-100 p-4 shadow-sm">
              <span className="inline-flex items-center gap-2 text-sm font-bold uppercase tracking-[0.18em] text-clinic-muted">
                <MapPin className="h-4 w-4 text-secondary" />
                Provincia
              </span>
              <select value={selectedProvince} onChange={(event) => onProvinceChange(event.target.value)} className="select select-bordered mt-3 w-full">
                <option value={options.default_province}>{options.default_province}</option>
                <option value={ALL_PROVINCES}>Todos los datos</option>
                {options.provinces
                  .filter((province) => province !== options.default_province)
                  .map((province) => (
                    <option key={province} value={province}>
                      {province}
                    </option>
                  ))}
              </select>
            </div>

            <div className="rounded-xl border border-base-300 bg-base-100 p-4 shadow-sm">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <span className="inline-flex items-center gap-2 text-sm font-bold uppercase tracking-[0.18em] text-clinic-muted">
                  <Goal className="h-4 w-4 text-secondary" />
                  Meta del indicador
                </span>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  value={targetCoverage}
                  onChange={handleTargetChange}
                  className="input input-bordered input-sm max-w-40"
                />
              </div>
              <progress className="progress progress-secondary mt-4 h-3 w-full" value={boundedTarget} max="100" />
            </div>
          </div>
        </div>
      </SectionPanel>

      <div className="grid gap-4 md:grid-cols-2">
        <ConfigCard icon={Filter} title="Filtro activo" tone="blue">
          <p className="text-2xl font-bold text-clinic-ink">{isAllData ? 'Todos los datos' : selectedProvince}</p>
          <p className="mt-2 text-sm leading-6 text-clinic-muted">
            {isAllData
              ? 'Se calculara el indicador usando todas las provincias disponibles en el archivo.'
              : `Se calculara el indicador solo con registros cuya columna territorial coincida con ${selectedProvince}.`}
          </p>
        </ConfigCard>

        <ConfigCard icon={ShieldCheck} title="Semaforo" tone="teal">
          <div className="space-y-3 text-sm font-semibold">
            <p className="inline-flex items-center gap-2 text-emerald-700">
              <CheckCircle2 className="h-5 w-5" />
              Cumple: cobertura mayor o igual a {targetCoverage}%.
            </p>
            <p className="inline-flex items-center gap-2 text-red-700">
              <XCircle className="h-5 w-5" />
              No cumple: cobertura menor a {targetCoverage}%.
            </p>
          </div>
        </ConfigCard>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <ConfigCard icon={Layers3} title="Tipos de seguro incluidos" tone="violet">
          <div className="flex flex-wrap gap-2">
            {options.included_insurance_types.map((item) => (
              <span key={item} className="badge badge-accent h-auto px-3 py-1 text-sm font-bold">
                {item}
              </span>
            ))}
          </div>
          <p className="mt-3 text-sm leading-6 text-clinic-muted">
            Las celdas vacias de seguro se consideran como sin seguro para el calculo del denominador.
          </p>
        </ConfigCard>

        <ConfigCard icon={Info} title="Criterios de evaluacion" tone="amber">
          <div className="space-y-2 text-sm leading-6 text-clinic-muted">
            <p>Incluye: <span className="font-bold text-clinic-ink">{options.exclusion_criteria.included_obs_eval ?? options.exclusion_criteria.included_population ?? 'Evaluado'}</span>.</p>
            <p>Excluye: <span className="font-bold text-clinic-ink">{options.exclusion_criteria.excluded_obs_eval ?? options.exclusion_criteria.excluded_population ?? 'No_Evaluado'}</span>.</p>
            <p>El peso al nacer y la edad gestacional ya vienen evaluados en esa columna del archivo.</p>
          </div>
        </ConfigCard>
      </div>
    </section>
  );
}

export { ALL_PROVINCES, DEFAULT_TARGET_COVERAGE };
export default ConfigView;
