import { useEffect, useState } from 'react';
import api from './api/client';
import { CheckCircle2, Filter, Goal, Info, Layers3, MapPin, ShieldCheck, SlidersHorizontal, XCircle } from 'lucide-react';

const ALL_PROVINCES = '__ALL__';
const DEFAULT_TARGET_COVERAGE = 70.7;

function ConfigCard({ icon: Icon, title, children }) {
  return (
    <div className="inner-panel p-5 transition hover:-translate-y-0.5 hover:shadow-soft">
      <div className="flex items-center gap-3">
        <span className="grid h-10 w-10 place-items-center rounded-xl bg-clinic-mint text-clinic-teal ring-1 ring-teal-100">
          <Icon className="h-5 w-5" />
        </span>
        <h3 className="font-bold text-clinic-ink">{title}</h3>
      </div>
      <div className="mt-4">{children}</div>
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

  const handleTargetChange = (event) => {
    const value = Number(event.target.value);
    if (Number.isNaN(value)) return;
    onTargetCoverageChange(Math.max(0, Math.min(100, value)));
  };

  return (
    <section className="space-y-6">
      <article className="panel p-5 lg:p-6">
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-3">
            <span className="grid h-11 w-11 place-items-center rounded-xl bg-clinic-teal text-white">
              <SlidersHorizontal className="h-5 w-5" />
            </span>
            <div>
              <h2 className="text-2xl font-bold text-clinic-ink">Poblacion objetivo</h2>
              <p className="text-sm text-clinic-muted">
                El filtro se aplica al dashboard, busqueda por DNI y descarga de incumplidos.
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="mt-5 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
            No se pudieron cargar las opciones: {error}
          </div>
        )}

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <label className="block">
            <span className="inline-flex items-center gap-2 text-sm font-bold uppercase tracking-[0.18em] text-clinic-muted">
              <MapPin className="h-4 w-4 text-clinic-violet" />
              Provincia
            </span>
            <select value={selectedProvince} onChange={(event) => onProvinceChange(event.target.value)} className="field">
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
          </label>

          <label className="block">
            <span className="inline-flex items-center gap-2 text-sm font-bold uppercase tracking-[0.18em] text-clinic-muted">
              <Goal className="h-4 w-4 text-clinic-violet" />
              Meta del indicador (%)
            </span>
            <input
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={targetCoverage}
              onChange={handleTargetChange}
              className="field"
            />
          </label>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <ConfigCard icon={Filter} title="Filtro activo">
            <p className="text-2xl font-bold text-clinic-ink">{isAllData ? 'Todos los datos' : selectedProvince}</p>
            <p className="mt-2 text-sm leading-6 text-clinic-muted">
              {isAllData
                ? 'Se calculara el indicador usando todas las provincias disponibles en el archivo.'
                : `Se calculara el indicador solo con registros cuya columna territorial coincida con ${selectedProvince}.`}
            </p>
          </ConfigCard>

          <ConfigCard icon={ShieldCheck} title="Semaforo">
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

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <ConfigCard icon={Layers3} title="Tipos de seguro incluidos">
            <div className="flex flex-wrap gap-2">
              {options.included_insurance_types.map((item) => (
                <span key={item} className="rounded-full bg-clinic-mint px-3 py-1 text-sm font-bold text-clinic-teal ring-1 ring-teal-100">
                  {item}
                </span>
              ))}
            </div>
            <p className="mt-3 text-sm leading-6 text-clinic-muted">
              Las celdas vacias de seguro se consideran como sin seguro para el calculo del denominador.
            </p>
          </ConfigCard>

          <ConfigCard icon={Info} title="Criterios de evaluacion">
            <div className="space-y-2 text-sm leading-6 text-clinic-muted">
              <p>Incluye: <span className="font-bold text-clinic-ink">{options.exclusion_criteria.included_obs_eval ?? options.exclusion_criteria.included_population ?? 'Evaluado'}</span>.</p>
              <p>Excluye: <span className="font-bold text-clinic-ink">{options.exclusion_criteria.excluded_obs_eval ?? options.exclusion_criteria.excluded_population ?? 'No_Evaluado'}</span>.</p>
              <p>
                El peso al nacer y la edad gestacional ya vienen evaluados en esa columna del archivo.
              </p>
            </div>
          </ConfigCard>
        </div>
      </article>
    </section>
  );
}

export { ALL_PROVINCES, DEFAULT_TARGET_COVERAGE };
export default ConfigView;
