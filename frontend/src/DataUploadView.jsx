import { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import {
  AlertCircle,
  CalendarDays,
  CheckCircle2,
  DatabaseZap,
  FileCheck2,
  FileSpreadsheet,
  Loader2,
  RefreshCcw,
  UploadCloud,
  XCircle,
} from 'lucide-react';
import indicators from './indicators/registry';
import { formatPeruDate } from './utils/dates';

function formatDate(value) {
  return formatPeruDate(value);
}

function formatDateTime(value) {
  if (!value) return '-';
  const date = new Date(String(value).replace(' ', 'T'));
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('es-PE', { year: 'numeric', month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function formatFileSize(value) {
  if (!value) return '-';
  if (value < 1024 * 1024) return `${Math.round(value / 1024)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

function titleCaseKey(value) {
  return String(value || '')
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatCountItems(counts) {
  return Object.entries(counts ?? {}).map(([key, value]) => `${titleCaseKey(key)}: ${value}`);
}

function formatComponentItems(counts) {
  return Object.entries(counts ?? {}).map(([component, values]) => {
    const detail = Object.entries(values ?? {})
      .map(([key, value]) => `${titleCaseKey(key)} ${value}`)
      .join(' / ');
    return detail ? `${component}: ${detail}` : component;
  });
}

function InfoCell({ label, value, icon: Icon }) {
  return (
    <div className="flex min-h-[4.75rem] items-center gap-3 rounded-lg border border-clinic-border bg-white p-3 shadow-sm">
      <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-clinic-mint text-clinic-teal ring-1 ring-teal-100">
        <Icon className="h-4 w-4" />
      </span>
      <div className="min-w-0">
        <p className="text-[0.68rem] font-bold uppercase tracking-[0.14em] text-clinic-muted">{label}</p>
        <p className="mt-1 break-words text-sm font-bold text-clinic-ink">{value}</p>
      </div>
    </div>
  );
}

function SectionTitleCard({ eyebrow, title, description, icon: Icon, action }) {
  return (
    <div className="flex h-full items-start gap-3 rounded-xl border border-clinic-border bg-white p-4 shadow-sm">
      <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-clinic-teal text-white">
        <Icon className="h-5 w-5" />
      </span>
      <div className="min-w-0 flex-1">
        {eyebrow && <p className="text-xs font-bold uppercase tracking-[0.16em] text-clinic-teal">{eyebrow}</p>}
        <h2 className="mt-1 break-words text-lg font-bold text-clinic-ink">{title}</h2>
        {description && <p className="mt-1 text-sm leading-5 text-clinic-muted">{description}</p>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}

function StatusRow({ number, title, description, state = 'pending' }) {
  const styles = {
    done: 'border-emerald-200 bg-emerald-50 text-emerald-700',
    active: 'border-clinic-teal/30 bg-clinic-mint/70 text-clinic-teal',
    pending: 'border-clinic-border bg-white text-clinic-muted',
  };

  return (
    <div className={`flex h-full items-start gap-3 rounded-xl border p-3 shadow-sm ${styles[state]}`}>
      <span className={`grid h-7 w-7 shrink-0 place-items-center rounded-full text-xs font-bold ${
        state === 'done' ? 'bg-emerald-600 text-white' : state === 'active' ? 'bg-white text-clinic-teal ring-1 ring-teal-100' : 'bg-slate-100 text-clinic-muted'
      }`}>
        {state === 'done' ? <CheckCircle2 className="h-4 w-4" /> : number}
      </span>
      <div>
        <p className="text-sm font-bold">{title}</p>
        <p className="text-xs font-semibold opacity-80">{description}</p>
      </div>
    </div>
  );
}

function MessageList({ title, items, tone = 'warning' }) {
  if (!items?.length) return null;
  const isError = tone === 'error';
  const Icon = isError ? XCircle : AlertCircle;
  return (
    <div className={`rounded-lg border p-3 ${isError ? 'border-red-200 bg-red-50 text-red-700' : 'border-amber-200 bg-amber-50 text-amber-800'}`}>
      <p className="inline-flex items-center gap-2 text-sm font-bold">
        <Icon className="h-4 w-4" />
        {title}
      </p>
      <ul className="mt-2 space-y-1 text-sm font-semibold leading-5">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function ChipGroup({ title, items, emptyText = 'Sin datos detectados' }) {
  return (
    <div className="rounded-lg border border-clinic-border bg-white p-3">
      <p className="text-[0.68rem] font-bold uppercase tracking-[0.14em] text-clinic-muted">{title}</p>
      {items?.length ? (
        <div className="mt-2 flex max-h-20 flex-wrap gap-1.5 overflow-y-auto pr-1">
          {items.slice(0, 18).map((item) => (
            <span key={item} className="rounded-full bg-clinic-mint px-2.5 py-1 text-xs font-bold text-clinic-teal ring-1 ring-teal-100">
              {item}
            </span>
          ))}
          {items.length > 18 && (
            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-bold text-clinic-muted ring-1 ring-slate-200">
              +{items.length - 18} mas
            </span>
          )}
        </div>
      ) : (
        <p className="mt-2 text-sm font-semibold text-clinic-muted">{emptyText}</p>
      )}
    </div>
  );
}

function DataUploadView({ selectedIndicator }) {
  const [currentData, setCurrentData] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);
  const activeIndicator = indicators[selectedIndicator] ?? indicators.mc03;

  const loadCurrentData = () => {
    axios
      .get(`/api/data/current?indicator=${selectedIndicator}`)
      .then((response) => setCurrentData(response.data))
      .catch((err) => setError(err.response?.data?.detail || err.message));
  };

  useEffect(() => {
    setSelectedFile(null);
    setPreview(null);
    setError(null);
    setStatus('idle');
    loadCurrentData();
  }, [selectedIndicator]);

  const previewSummary = preview?.summary;
  const canActivate = preview?.valid && preview?.upload_id && status !== 'activating';
  const currentSummary = currentData?.summary;
  const selectedFileLabel = selectedFile ? `${selectedFile.name} (${formatFileSize(selectedFile.size)})` : 'Ningun archivo seleccionado';

  const statusPreview = useMemo(
    () => formatCountItems(previewSummary?.status_counts ?? previewSummary?.obs_eval_counts),
    [previewSummary],
  );
  const denominatorPreview = useMemo(
    () => formatCountItems(previewSummary?.denominator_counts),
    [previewSummary],
  );
  const componentPreview = useMemo(
    () => formatComponentItems(previewSummary?.component_counts),
    [previewSummary],
  );
  const insurancePreview = useMemo(
    () => formatCountItems(previewSummary?.insurance_counts),
    [previewSummary],
  );
  const missingColumnsPreview = useMemo(
    () => previewSummary?.missing_columns ?? [],
    [previewSummary],
  );
  const omittedColumnsPreview = useMemo(
    () => previewSummary?.omitted_columns ?? [],
    [previewSummary],
  );

  const stepState = {
    upload: preview ? 'done' : selectedFile ? 'active' : 'pending',
    validate: preview?.valid ? 'done' : status === 'uploading' ? 'active' : 'pending',
    activate: status === 'activated' ? 'done' : status === 'activating' ? 'active' : 'pending',
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files?.[0] ?? null);
    setPreview(null);
    setError(null);
    setStatus('idle');
  };

  const handlePreview = async () => {
    if (!selectedFile) return;
    setStatus('uploading');
    setError(null);
    setPreview(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`/api/data/upload-preview?indicator=${selectedIndicator}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setPreview(response.data);
      setStatus('previewed');
    } catch (err) {
      setStatus('idle');
      setError(err.response?.data?.detail || err.message);
    }
  };

  const handleActivate = async () => {
    if (!canActivate) return;
    setStatus('activating');
    setError(null);

    try {
      const response = await axios.post(`/api/data/activate?indicator=${selectedIndicator}`, { upload_id: preview.upload_id });
      setCurrentData(response.data);
      setStatus('activated');
      setSelectedFile(null);
    } catch (err) {
      setStatus('previewed');
      setError(err.response?.data?.detail || err.message);
    }
  };

  return (
    <section className="space-y-4">
      <article className="panel p-4 lg:p-5">
        <div className="grid gap-3 lg:grid-cols-[1.2fr_0.8fr_0.8fr_0.9fr]">
          <SectionTitleCard
            eyebrow="Fuente de datos activa"
            title={currentSummary?.original_name || currentSummary?.filename || 'Sin archivo cargado'}
            description="Archivo usado por busqueda, dashboard y exportaciones."
            icon={DatabaseZap}
            action={(
              <button type="button" onClick={loadCurrentData} className="icon-button btn-secondary">
                <RefreshCcw className="h-4 w-4" />
                Actualizar
              </button>
            )}
          />
          <InfoCell label="Fecha de corte" value={formatDate(currentSummary?.cutoff_date)} icon={CalendarDays} />
          <InfoCell label="Registros" value={currentSummary?.total_rows ?? '-'} icon={DatabaseZap} />
          <InfoCell label="Ultima activacion" value={formatDateTime(currentSummary?.activated_at)} icon={FileCheck2} />
        </div>
      </article>

      <article className="panel p-4 lg:p-5">
        <div className="grid gap-3 lg:grid-cols-4">
          <SectionTitleCard
            eyebrow="Carga del archivo"
            title={`Nuevo Excel ${activeIndicator.shortName}`}
            description={`Selecciona, valida y activa un .xlsx para ${activeIndicator.title}.`}
            icon={UploadCloud}
          />
          <StatusRow number="1" title="Seleccionar archivo" description="Carga el Excel mensual." state={stepState.upload} />
          <StatusRow number="2" title="Validar estructura" description="Revisa hoja, columnas y corte." state={stepState.validate} />
          <StatusRow number="3" title="Activar datos" description="Reprocesa busqueda y dashboard." state={stepState.activate} />
        </div>

        {error && (
          <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm font-semibold text-red-700">
            {error}
          </div>
        )}

        <div className="mt-4 grid gap-4 lg:grid-cols-[0.82fr_1.18fr]">
          <section className="rounded-xl border border-clinic-border bg-slate-50/70 p-4">
            <div className="flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-clinic-teal text-white">
              <FileSpreadsheet className="h-5 w-5" />
            </span>
            <div>
              <h3 className="font-bold text-clinic-ink">Archivo a procesar</h3>
              <p className="text-sm text-clinic-muted">El archivo no se activa hasta validar.</p>
            </div>
          </div>

          <label className="mt-4 block cursor-pointer rounded-xl border border-clinic-border bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-clinic-teal hover:bg-clinic-mint/30">
            <span className="flex items-center gap-3">
              <span className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-clinic-mint text-clinic-teal ring-1 ring-teal-100">
                <FileSpreadsheet className="h-5 w-5" />
              </span>
              <span className="min-w-0">
                <span className="block text-xs font-bold uppercase tracking-[0.14em] text-clinic-muted">Archivo Excel</span>
                <span className="mt-1 block break-words text-sm font-bold text-clinic-ink">{selectedFileLabel}</span>
              </span>
            </span>
            <input type="file" accept=".xlsx" onChange={handleFileChange} className="sr-only" />
          </label>

          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
            <button
              type="button"
              onClick={handlePreview}
              disabled={!selectedFile || status === 'uploading' || status === 'activating'}
              className="icon-button btn-primary disabled:cursor-not-allowed disabled:opacity-50"
            >
              {status === 'uploading' ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileCheck2 className="h-4 w-4" />}
              Validar
            </button>
            <button
              type="button"
              onClick={handleActivate}
              disabled={!canActivate}
              className="icon-button btn-secondary disabled:cursor-not-allowed disabled:opacity-50"
            >
              {status === 'activating' ? <Loader2 className="h-4 w-4 animate-spin" /> : <DatabaseZap className="h-4 w-4" />}
              Activar
            </button>
          </div>

          {status === 'activated' && (
            <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm font-bold text-emerald-700">
              Archivo activado correctamente. El sistema ya usa la nueva informacion.
            </div>
          )}
          </section>

          <section className="overflow-hidden rounded-xl border border-clinic-border bg-white">
          <div className="border-b border-clinic-border bg-slate-50 px-4 py-3">
            <h2 className="text-xl font-bold text-clinic-ink">Resultado de validacion</h2>
            <p className="text-sm text-clinic-muted">Resumen antes de activar el archivo como fuente oficial.</p>
          </div>

          {!preview ? (
            <div className="grid min-h-64 place-items-center p-5">
              <div className="max-w-md text-center">
                <UploadCloud className="mx-auto h-11 w-11 text-clinic-teal" />
                <h3 className="mt-3 text-lg font-bold text-clinic-ink">Sin archivo validado</h3>
                <p className="mt-2 text-sm leading-5 text-clinic-muted">
                  Selecciona un Excel y presiona validar para ver corte, registros, meses, provincias y observaciones.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-3 p-4">
              <div className={`rounded-lg border p-3 ${preview.valid ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : 'border-red-200 bg-red-50 text-red-700'}`}>
                <p className="inline-flex items-center gap-2 text-sm font-bold">
                  {preview.valid ? <CheckCircle2 className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
                  {preview.valid ? 'Archivo valido para procesamiento' : 'El archivo necesita correcciones antes de activarse'}
                </p>
              </div>

              <MessageList title="Errores encontrados" items={preview.errors} tone="error" />
              <MessageList title="Advertencias" items={preview.warnings} />

              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                  <InfoCell label="Corte detectado" value={formatDate(previewSummary?.cutoff_date)} icon={CalendarDays} />
                  <InfoCell label="Registros" value={previewSummary?.total_rows ?? '-'} icon={DatabaseZap} />
                  <InfoCell label="Columnas" value={previewSummary?.total_columns ?? '-'} icon={FileSpreadsheet} />
                  <InfoCell label="Tamanio" value={formatFileSize(previewSummary?.file_size_bytes)} icon={FileCheck2} />
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                <InfoCell label="Hoja esperada" value={previewSummary?.sheet_name ?? 'Detalle_Ate'} icon={FileSpreadsheet} />
                <InfoCell label="Celda de corte" value={previewSummary?.cutoff_cell ?? '-'} icon={CalendarDays} />
                <InfoCell label="Fila de encabezados" value={previewSummary?.header_row ?? '-'} icon={FileCheck2} />
              </div>

              <div className="grid gap-3 xl:grid-cols-3">
                <ChipGroup title="Meses encontrados" items={previewSummary?.months ?? []} />
                <ChipGroup title="Provincias encontradas" items={previewSummary?.provinces ?? []} />
                <ChipGroup title={previewSummary?.validation_label ?? 'Estado'} items={statusPreview} />
              </div>

              <div className="grid gap-3 xl:grid-cols-3">
                <ChipGroup title="Tipo de seguro" items={insurancePreview} />
                <ChipGroup title="Denominador y exclusiones" items={denominatorPreview} />
                <ChipGroup title="Componentes evaluados" items={componentPreview} />
              </div>

              <div className="grid gap-3 xl:grid-cols-2">
                <ChipGroup title="Columnas faltantes" items={missingColumnsPreview} emptyText="No faltan columnas obligatorias" />
                <ChipGroup title="Columnas presentes no evaluadas ahora" items={omittedColumnsPreview} emptyText="Sin columnas omitidas detectadas" />
              </div>
            </div>
          )}
          </section>
        </div>
      </article>
    </section>
  );
}

export default DataUploadView;
