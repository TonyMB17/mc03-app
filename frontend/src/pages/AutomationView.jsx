import { useRef, useState } from 'react';
import { CheckCircle2, Loader2, Play, Terminal, Trash2 } from 'lucide-react';
import { AUTH_TOKEN_KEY } from '../api/client';
import SectionPanel from '../components/SectionPanel';

function consoleLineTone(line) {
  if (line.includes('ERROR')) return 'text-error';
  if (line.includes('VALIDO') || line.includes('activado') || line.includes('terminado')) return 'text-success';
  if (line.includes('Advertencia')) return 'text-warning';
  return 'text-primary-content/85';
}

function AutomationView() {
  const [running, setRunning] = useState(false);
  const [finished, setFinished] = useState(false);
  const [lines, setLines] = useState([
    '[listo] Presiona ejecutar para descargar, validar y activar los archivos semanales.',
  ]);
  const consoleRef = useRef(null);

  const appendText = (text) => {
    const nextLines = text.split(/\r?\n/).filter(Boolean);
    if (!nextLines.length) return;
    setLines((current) => [...current, ...nextLines]);
    window.requestAnimationFrame(() => {
      if (consoleRef.current) {
        consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
      }
    });
  };

  const runAutomation = async () => {
    setRunning(true);
    setFinished(false);
    setLines(['[inicio] Ejecutando automatizacion de carga semanal...']);

    try {
      const token = localStorage.getItem(AUTH_TOKEN_KEY);
      const response = await fetch('/api/automation/cloud-import/stream?activate=true&cleanup=true', {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (!response.ok) {
        throw new Error(`No se pudo iniciar la automatizacion. HTTP ${response.status}`);
      }
      if (!response.body) {
        throw new Error('El navegador no pudo abrir el stream de ejecucion.');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        appendText(decoder.decode(value, { stream: true }));
      }
      appendText(decoder.decode());
      setFinished(true);
    } catch (error) {
      appendText(`[ERROR] ${error.message || 'Error inesperado durante la automatizacion.'}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <section className="space-y-5">
      <SectionPanel className="overflow-hidden">
        <div className="grid gap-5 border-b border-base-300 bg-base-200 p-5 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center lg:p-6">
          <div className="flex items-start gap-3">
            <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-base-100 text-secondary ring-1 ring-secondary/20">
              <Terminal className="h-5 w-5" />
            </span>
            <div>
              <h3 className="text-xl font-bold text-clinic-ink">Automatizacion de carga</h3>
              <p className="mt-1 max-w-3xl text-sm leading-6 text-clinic-muted">
                Descarga los Excel mas recientes desde DIRESA Cloud, valida MC-02, MC-03 y SI-02, activa los datos y elimina los archivos temporales si todo termina correctamente.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={runAutomation}
            disabled={running}
            className="btn btn-primary min-w-52 text-primary-content shadow-sm disabled:opacity-60"
          >
            {running ? <Loader2 className="h-4 w-4 animate-spin" /> : finished ? <CheckCircle2 className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            {running ? 'Ejecutando...' : finished ? 'Ejecutar nuevamente' : 'Ejecutar automatizacion'}
          </button>
        </div>

        <div className="p-5 lg:p-6">
          <div className="mb-3 flex items-center justify-between gap-3">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-clinic-muted">Consola de ejecucion</p>
            <span className="inline-flex items-center gap-2 rounded-full border border-base-300 bg-base-200 px-3 py-1 text-xs font-bold text-clinic-muted">
              <Trash2 className="h-3.5 w-3.5 text-secondary" />
              Limpieza automatica al finalizar
            </span>
          </div>

          <div
            ref={consoleRef}
            className="h-[28rem] overflow-y-auto rounded-xl border border-primary/20 bg-[#071527] p-4 font-mono text-xs leading-6 shadow-inner"
          >
            {lines.map((line, index) => (
              <div key={`${index}-${line}`} className={`whitespace-pre-wrap break-words ${consoleLineTone(line)}`}>
                {line}
              </div>
            ))}
            {running && <div className="mt-2 h-4 w-2 animate-pulse bg-secondary" />}
          </div>
        </div>
      </SectionPanel>
    </section>
  );
}

export default AutomationView;
