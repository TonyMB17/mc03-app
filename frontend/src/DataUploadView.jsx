import { useEffect, useMemo, useState } from 'react';
import api from './api/client';
import {
  AlertCircle,
  CalendarDays,
  CheckCircle2,
  DatabaseZap,
  FileCheck2,
  FileSpreadsheet,
  Layers3,
  Loader2,
  RefreshCcw,
  UploadCloud,
  XCircle,
} from 'lucide-react';
import SectionPanel from './components/SectionPanel';
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

function formatSubindicatorCode(value) {
  const code = String(value || '').toUpperCase();
  return code.replace(/^SI02_(\d+)$/, 'SI-02.$1');
}

function PackageFileGrid({ files }) {
  if (!files?.length) return null;

  const styles = {
    ok: 'border-success/25 bg-success/10 text-success',
    missing: 'border-error/25 bg-error/10 text-error',
    duplicate: 'border-warning/25 bg-warning/10 text-warning',
  };

  return (
    <div className="rounded-xl border border-base-300 bg-base-100 p-3">
      <p className="inline-flex items-center gap-2 text-[0.68rem] font-bold uppercase tracking-[0.14em] text-clinic-muted">
        <Layers3 className="h-4 w-4 text-secondary" />
        Archivos del paquete
      </p>
      <div className="mt-3 grid gap-2 md:grid-cols-2">
        {files.map((item) => (
          <div key={item.subindicator_code} className={`rounded-lg border p-3 ${styles[item.status] ?? styles.ok}`}>
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="text-sm font-bold text-clinic-ink">{formatSubindicatorCode(item.subindicator_code)}</p>
                <p className="mt-1 truncate text-xs font-semibold">{item.filename || 'Archivo no encontrado'}</p>
              </div>
              <span className="badge badge-ghost h-auto shrink-0 px-2.5 py-1 text-xs font-bold">
                {item.status === 'ok' ? 'OK' : item.status === 'duplicate' ? 'Duplicado' : 'Falta'}
              </span>
            </div>
            <p className="mt-2 text-xs font-semibold">
              Corte {formatDate(item.cutoff_date)} - {item.rows ?? 0} registros - {item.columns ?? 0} columnas
            </p>
            {item.missing_columns?.length > 0 && (
              <p className="mt-1 text-xs font-bold">Faltan {item.missing_columns.length} columnas obligatorias</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function InfoCell({ label, value, icon: Icon }) {
  return (
    <div className="flex min-h-[4.25rem] items-center gap-3 rounded-xl border border-base-300 bg-base-100 p-3 shadow-sm">
      <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-secondary/10 text-secondary ring-1 ring-secondary/20">
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
    <div className="flex h-full items-start gap-3 rounded-xl border border-base-300 bg-base-100 p-4 shadow-sm">
      <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-secondary text-secondary-content">
        <Icon className="h-5 w-5" />
      </span>
      <div className="min-w-0 flex-1">
        {eyebrow && <p className="text-xs font-bold uppercase tracking-[0.16em] text-secondary">{eyebrow}</p>}
        <h2 className="mt-1 break-words text-lg font-black text-primary">{title}</h2>
        {description && <p className="mt-1 text-sm leading-5 text-clinic-muted">{description}</p>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}

function OperationalStatus({ status, preview, currentData }) {
  const states = {
    idle: {
      label: 'Listo para cargar',
      description: 'Selecciona un archivo para iniciar la validacion.',
      className: 'border-info/25 bg-info/10 text-primary',
      icon: UploadCloud,
    },
    uploading: {
      label: 'Validando archivo',
      description: 'Revisando estructura, columnas y corte del Excel.',
      className: 'border-warning/25 bg-warning/10 text-warning',
      icon: Loader2,
    },
    previewed: {
      label: preview?.valid ? 'Validacion correcta' : 'Validacion con observaciones',
      description: preview?.valid ? 'El archivo esta listo para activarse.' : 'Corrige los errores antes de activar.',
      className: preview?.valid ? 'border-success/25 bg-success/10 text-success' : 'border-error/25 bg-error/10 text-error',
      icon: preview?.valid ? CheckCircle2 : XCircle,
    },
    activating: {
      label: 'Activando datos',
      description: currentData?.message || 'Procesando en segundo plano. La version anterior sigue disponible.',
      className: 'border-warning/25 bg-warning/10 text-warning',
      icon: Loader2,
    },
    activated: {
      label: 'Fuente actualizada',
      description: 'El sistema ya usa la informacion activada.',
      className: 'border-success/25 bg-success/10 text-success',
      icon: CheckCircle2,
    },
  };
  const current = states[status] ?? states.idle;
  const Icon = current.icon;

  return (
    <div className={`rounded-lg border p-4 ${current.className}`}>
      <p className="inline-flex items-center gap-2 text-sm font-bold">
        <Icon className={`h-4 w-4 ${status === 'uploading' || status === 'activating' ? 'animate-spin' : ''}`} />
        {current.label}
      </p>
      <p className="mt-2 text-sm font-semibold leading-5">{current.description}</p>
    </div>
  );
}

function StatusRow({ number, title, description, state = 'pending' }) {
  const styles = {
    done: 'border-success/25 bg-success/10 text-success',
    active: 'border-secondary/30 bg-secondary/10 text-secondary',
    pending: 'border-base-300 bg-base-100 text-clinic-muted',
  };

  return (
    <div className={`flex h-full items-start gap-3 rounded-xl border p-3 shadow-sm ${styles[state]}`}>
      <span className={`grid h-7 w-7 shrink-0 place-items-center rounded-full text-xs font-bold ${
        state === 'done' ? 'bg-success text-success-content' : state === 'active' ? 'bg-base-100 text-secondary ring-1 ring-secondary/20' : 'bg-base-200 text-clinic-muted'
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
    <div className={`rounded-lg border p-3 ${isError ? 'border-error/25 bg-error/10 text-error' : 'border-warning/25 bg-warning/10 text-warning'}`}>
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
    <div className="rounded-xl border border-base-300 bg-base-100 p-3">
      <p className="text-[0.68rem] font-bold uppercase tracking-[0.14em] text-clinic-muted">{title}</p>
      {items?.length ? (
        <div className="mt-2 flex max-h-20 flex-wrap gap-1.5 overflow-y-auto pr-1">
          {items.slice(0, 18).map((item) => (
            <span key={item} className="badge badge-info badge-outline h-auto px-2.5 py-1 text-xs font-bold">
              {item}
            </span>
          ))}
          {items.length > 18 && (
            <span className="badge badge-ghost h-auto border-base-300 px-2.5 py-1 text-xs font-bold text-clinic-muted">
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

function UploadStatusBadge({ item }) {
  const status = item.is_active ? 'active' : item.status;
  const styles = {
    active: 'badge-success',
    failed: 'badge-error',
    processing: 'badge-warning',
    pending: 'badge-info',
    superseded: 'badge-ghost border-base-300 text-clinic-muted',
  };
  const labels = {
    active: 'Activa',
    failed: 'Fallida',
    processing: 'Procesando',
    pending: 'Pendiente',
    superseded: 'Reemplazada',
  };
  return (
    <span className={`badge h-auto px-2.5 py-1 text-xs font-bold ${styles[status] ?? styles.superseded}`}>
      {labels[status] ?? titleCaseKey(status)}
    </span>
  );
}

function DataUploadView({ selectedIndicator }) {
  const [currentData, setCurrentData] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [preview, setPreview] = useState(null);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);
  const [activationJobId, setActivationJobId] = useState(null);
  const [uploadHistory, setUploadHistory] = useState([]);
  const activeIndicator = indicators[selectedIndicator] ?? indicators.mc03;
  const isPackageUpload = Boolean(activeIndicator.packageUpload);

  const loadCurrentData = () => {
    api
      .get(`/api/data/current?indicator=${selectedIndicator}`)
      .then((response) => setCurrentData(response.data))
      .catch((err) => setError(err.response?.data?.detail || err.message));
  };

  const loadUploadHistory = () => {
    api
      .get(`/api/data/uploads?indicator=${selectedIndicator}`)
      .then((response) => setUploadHistory(response.data.uploads ?? []))
      .catch((err) => setError(err.response?.data?.detail || err.message));
  };

  useEffect(() => {
    setSelectedFiles([]);
    setPreview(null);
    setError(null);
    setStatus('idle');
    setActivationJobId(null);
    loadCurrentData();
    loadUploadHistory();
  }, [selectedIndicator]);

  useEffect(() => {
    if (!activationJobId || status !== 'activating') return undefined;

    let cancelled = false;
    const loadActivationStatus = async () => {
      try {
        const response = await api.get(`/api/data/activation/${activationJobId}?indicator=${selectedIndicator}`);
        if (cancelled) return;
        setCurrentData(response.data);
        if (!response.data.processing) {
          if (response.data.job_status === 'activated') {
            setStatus('activated');
            setSelectedFiles([]);
            setActivationJobId(null);
            loadUploadHistory();
          } else if (response.data.job_status === 'failed') {
            setStatus('previewed');
            setActivationJobId(null);
            setError(response.data.error || 'No se pudo activar la carga');
          }
        }
      } catch (err) {
        if (cancelled) return;
        setStatus('previewed');
        setActivationJobId(null);
        setError(err.response?.data?.detail || err.message);
      }
    };

    loadActivationStatus();
    const interval = window.setInterval(loadActivationStatus, 2000);
    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [activationJobId, selectedIndicator, status]);

  const previewSummary = preview?.summary;
  const canActivate = preview?.valid && preview?.upload_id && status !== 'activating';
  const currentSummary = currentData?.summary;
  const totalSelectedSize = selectedFiles.reduce((sum, file) => sum + file.size, 0);
  const selectedFileLabel = selectedFiles.length
    ? selectedFiles.length === 1
      ? `${selectedFiles[0].name} (${formatFileSize(selectedFiles[0].size)})`
      : `${selectedFiles.length} archivos seleccionados (${formatFileSize(totalSelectedSize)})`
    : isPackageUpload
      ? 'Ningun paquete seleccionado'
      : 'Ningun archivo seleccionado';
  const expectedFileCount = activeIndicator.requiredFiles ?? 1;
  const hasRequiredFiles = !isPackageUpload || selectedFiles.length === expectedFileCount;
  const canPreview = selectedFiles.length > 0 && hasRequiredFiles;

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
  const packageFilesPreview = useMemo(
    () => previewSummary?.package_files ?? [],
    [previewSummary],
  );

  const stepState = {
    upload: preview ? 'done' : selectedFiles.length ? 'active' : 'pending',
    validate: preview?.valid ? 'done' : status === 'uploading' ? 'active' : 'pending',
    activate: status === 'activated' ? 'done' : status === 'activating' ? 'active' : 'pending',
  };

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files ?? []);
    setSelectedFiles(isPackageUpload ? files : files.slice(0, 1));
    setPreview(null);
    setError(null);
    setStatus('idle');
    setActivationJobId(null);
  };

  const handlePreview = async () => {
    if (!canPreview) return;
    setStatus('uploading');
    setError(null);
    setPreview(null);

    const formData = new FormData();
    if (isPackageUpload) {
      selectedFiles.forEach((file) => formData.append('files', file));
    } else {
      formData.append('file', selectedFiles[0]);
    }

    try {
      const response = await api.post(`/api/data/upload-preview?indicator=${selectedIndicator}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setPreview(response.data);
      setActivationJobId(null);
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
      const response = await api.post(`/api/data/activate?indicator=${selectedIndicator}`, { upload_id: preview.upload_id });
      setCurrentData(response.data);
      if (response.data.processing && response.data.job_id) {
        setActivationJobId(response.data.job_id);
        setStatus('activating');
        return;
      }
      setStatus('activated');
      setSelectedFiles([]);
      loadUploadHistory();
    } catch (err) {
      setStatus('previewed');
      setError(err.response?.data?.detail || err.message);
    }
  };

  const shortHash = (value) => (value ? `${value.slice(0, 12)}...` : '-');

  return (
    <section className="space-y-4">
      <SectionPanel className="p-4 lg:p-5">
        <div className="grid gap-3 lg:grid-cols-[1.2fr_0.8fr_0.8fr_0.9fr]">
          <SectionTitleCard
            eyebrow="Fuente de datos activa"
            title={currentSummary?.original_name || currentSummary?.filename || 'Sin archivo cargado'}
            description="Archivo usado por busqueda, dashboard y exportaciones."
            icon={DatabaseZap}
            action={(
              <button type="button" onClick={loadCurrentData} className="btn btn-outline btn-secondary btn-sm">
                <RefreshCcw className="h-4 w-4" />
                Actualizar
              </button>
            )}
          />
          <InfoCell label="Fecha de corte" value={formatDate(currentSummary?.cutoff_date)} icon={CalendarDays} />
          <InfoCell label="Registros" value={currentSummary?.total_rows ?? '-'} icon={DatabaseZap} />
          <InfoCell label="Ultima activacion" value={formatDateTime(currentSummary?.activated_at)} icon={FileCheck2} />
        </div>
      </SectionPanel>

      <SectionPanel className="p-4 lg:p-5">
        <div className="grid gap-3 xl:grid-cols-[1.15fr_0.85fr]">
          <SectionTitleCard
            eyebrow="Carga del archivo"
            title={isPackageUpload ? `Nuevo paquete ${activeIndicator.shortName}` : `Nuevo Excel ${activeIndicator.shortName}`}
            description={isPackageUpload ? `Selecciona los ${activeIndicator.requiredFiles} Excel del paquete semanal, valida y activa solo si el paquete esta completo.` : `Selecciona, valida y activa un .xlsx para ${activeIndicator.title}.`}
            icon={UploadCloud}
          />
          <OperationalStatus status={status} preview={preview} currentData={currentData} />
        </div>

        <div className="mt-4 grid gap-3 md:grid-cols-3">
          <StatusRow number="1" title={isPackageUpload ? 'Seleccionar paquete' : 'Seleccionar archivo'} description={isPackageUpload ? 'Carga los 4 Excel SI-02.' : 'Carga el Excel mensual.'} state={stepState.upload} />
          <StatusRow number="2" title="Validar estructura" description="Revisa hoja, columnas y corte." state={stepState.validate} />
          <StatusRow number="3" title="Activar datos" description="Reprocesa busqueda y dashboard." state={stepState.activate} />
        </div>

        {error && (
          <div className="alert alert-error mt-4 rounded-lg py-3 text-sm font-semibold">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        )}

        <div className="mt-4 grid gap-4 lg:grid-cols-[0.82fr_1.18fr]">
          <section className="rounded-xl border border-base-300 bg-base-200 p-4">
            <div className="flex items-center gap-3">
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-secondary text-secondary-content">
                <FileSpreadsheet className="h-5 w-5" />
              </span>
              <div>
                <h3 className="font-bold text-clinic-ink">Archivo a procesar</h3>
                <p className="text-sm text-clinic-muted">{isPackageUpload ? 'El paquete no se activa hasta validar los 4 archivos.' : 'El archivo no se activa hasta validar.'}</p>
              </div>
            </div>

            <label className="mt-4 block cursor-pointer rounded-xl border border-dashed border-base-300 bg-base-100 p-4 shadow-sm transition hover:border-secondary hover:bg-info/10">
              <span className="flex items-center gap-3">
                <span className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-secondary/10 text-secondary ring-1 ring-secondary/20">
                  <FileSpreadsheet className="h-5 w-5" />
                </span>
                <span className="min-w-0">
                  <span className="block text-xs font-bold uppercase tracking-[0.14em] text-clinic-muted">{isPackageUpload ? 'Paquete Excel' : 'Archivo Excel'}</span>
                  <span className="mt-1 block break-words text-sm font-bold text-clinic-ink">{selectedFileLabel}</span>
                  {isPackageUpload && selectedFiles.length > 0 && (
                    <span className="mt-2 block text-xs font-semibold leading-5 text-clinic-muted">
                      {selectedFiles.map((file) => file.name).join(' / ')}
                    </span>
                  )}
                  {isPackageUpload && selectedFiles.length > 0 && !hasRequiredFiles && (
                    <span className="mt-2 block text-xs font-bold text-amber-700">
                      Selecciona exactamente {expectedFileCount} archivos para validar el paquete.
                    </span>
                  )}
                </span>
              </span>
              <input type="file" accept=".xlsx" multiple={isPackageUpload} onChange={handleFileChange} className="sr-only" />
            </label>

            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
              <button
                type="button"
                onClick={handlePreview}
                disabled={!canPreview || status === 'uploading' || status === 'activating'}
                className="btn btn-primary disabled:cursor-not-allowed disabled:opacity-50"
              >
                {status === 'uploading' ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileCheck2 className="h-4 w-4" />}
                Validar
              </button>
              <button
                type="button"
                onClick={handleActivate}
                disabled={!canActivate}
                className="btn btn-outline btn-secondary disabled:cursor-not-allowed disabled:opacity-50"
              >
                {status === 'activating' ? <Loader2 className="h-4 w-4 animate-spin" /> : <DatabaseZap className="h-4 w-4" />}
                {status === 'activating' ? 'Procesando...' : 'Activar'}
              </button>
            </div>

            {status === 'activated' && (
              <div className="mt-4 rounded-lg border border-success/25 bg-success/10 p-3 text-sm font-bold text-success">
                Archivo activado correctamente. El sistema ya usa la nueva informacion.
              </div>
            )}
            {status === 'activating' && (
              <div className="mt-4 rounded-lg border border-warning/25 bg-warning/10 p-3 text-sm font-bold text-warning">
                {currentData?.message || 'Procesando la activacion en segundo plano. La version anterior sigue disponible mientras termina.'}
              </div>
            )}
          </section>

          <section className="overflow-hidden rounded-xl border border-base-300 bg-base-100">
            <div className="border-b border-base-300 bg-base-200 px-4 py-3">
              <h2 className="text-xl font-black text-primary">Resultado de validacion</h2>
              <p className="text-sm text-clinic-muted">Resumen antes de activar el archivo como fuente oficial.</p>
            </div>

            {!preview ? (
              <div className="grid min-h-64 place-items-center p-5">
                <div className="max-w-md text-center">
                  <UploadCloud className="mx-auto h-11 w-11 text-secondary" />
                  <h3 className="mt-3 text-lg font-bold text-clinic-ink">Sin archivo validado</h3>
                  <p className="mt-2 text-sm leading-5 text-clinic-muted">
                    Selecciona un Excel y presiona validar para ver corte, registros, meses, provincias y observaciones.
                  </p>
                </div>
              </div>
            ) : (
            <div className="space-y-3 p-4">
              <div className={`rounded-lg border p-3 ${preview.valid ? 'border-success/25 bg-success/10 text-success' : 'border-error/25 bg-error/10 text-error'}`}>
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

              {isPackageUpload && <PackageFileGrid files={packageFilesPreview} />}

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
      </SectionPanel>

      <SectionPanel className="p-4 lg:p-5">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <SectionTitleCard
            eyebrow="Auditoria"
            title="Historial de cargas"
            description="Versiones procesadas, archivo, actor, estado y hash SHA-256."
            icon={FileCheck2}
            action={(
              <button type="button" onClick={loadUploadHistory} className="btn btn-outline btn-secondary btn-sm">
                <RefreshCcw className="h-4 w-4" />
                Actualizar
              </button>
            )}
          />
        </div>
        <div className="mt-4 overflow-hidden rounded-xl border border-base-300 bg-base-100">
          <div className="overflow-x-auto">
            <table className="table table-zebra table-sm min-w-full text-sm">
              <thead className="bg-base-200 text-left text-primary">
                <tr>
                  <th className="px-4 py-3 font-bold">Estado</th>
                  <th className="px-4 py-3 font-bold">Archivo</th>
                  <th className="px-4 py-3 font-bold">Subido por</th>
                  <th className="px-4 py-3 font-bold">Activado por</th>
                  <th className="px-4 py-3 font-bold">Corte</th>
                  <th className="px-4 py-3 font-bold">Registros</th>
                  <th className="px-4 py-3 font-bold">SHA-256</th>
                </tr>
              </thead>
              <tbody>
                {uploadHistory.map((item) => (
                  <tr key={item.id} className={`text-clinic-muted ${item.is_active ? 'bg-success/10' : ''}`}>
                    <td className="px-4 py-3">
                      <UploadStatusBadge item={item} />
                    </td>
                    <td className="max-w-xs px-4 py-3 font-semibold text-clinic-ink">
                      <span className="block truncate">{item.original_filename || '-'}</span>
                      <span className="mt-1 block text-xs font-normal text-clinic-muted">{formatDateTime(item.created_at)}</span>
                    </td>
                    <td className="px-4 py-3">{item.uploaded_by || '-'}</td>
                    <td className="px-4 py-3">{item.activated_by || '-'}</td>
                    <td className="px-4 py-3">{formatDate(item.cutoff_date)}</td>
                    <td className="px-4 py-3">
                      <span className="font-semibold text-clinic-ink">{item.rows_total ?? '-'}</span>
                      {item.validation_summary?.subindicators && (
                        <span className="mt-1 block text-xs leading-5 text-clinic-muted">
                          {Object.entries(item.validation_summary.subindicators)
                            .map(([code, summary]) => `${formatSubindicatorCode(code)} ${summary.total_rows ?? 0}`)
                            .join(' / ')}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 font-mono text-xs">{shortHash(item.file_hash)}</td>
                  </tr>
                ))}
                {!uploadHistory.length && (
                  <tr>
                    <td className="px-4 py-4 text-clinic-muted" colSpan="7">
                      Aun no hay historial de cargas registrado en PostgreSQL.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </SectionPanel>
    </section>
  );
}

export default DataUploadView;
