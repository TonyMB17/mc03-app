import { useEffect, useMemo, useState } from 'react';
import api from '../api/client';

const PAGE_SIZE = 10;

function buildMonthKey(item) {
  const monthNumber = {
    enero: 1,
    febrero: 2,
    marzo: 3,
    abril: 4,
    mayo: 5,
    junio: 6,
    julio: 7,
    agosto: 8,
    setiembre: 9,
    octubre: 10,
    noviembre: 11,
    diciembre: 12,
  }[item.month];
  return `${item.year}_${monthNumber}`;
}

function buildMonthOrder(item) {
  const [year, month] = buildMonthKey(item).split('_').map(Number);
  return year * 12 + month;
}

export function useDashboardData(selectedProvince, targetCoverage, selectedIndicator, externalSelectedSubindicator = 'all') {
  const [status, setStatus] = useState('cargando...');
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  const [downloadError, setDownloadError] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState('');
  const [selectedSubindicator, setSelectedSubindicator] = useState('all');
  const [page, setPage] = useState(1);

  const isMc02 = selectedIndicator === 'mc02';
  const isSi02 = selectedIndicator === 'si02';

  // Fetch summary data on dependency change
  useEffect(() => {
    setError(null);
    setStatus('cargando...');
    const params = new URLSearchParams({
      province: selectedProvince,
      target: targetCoverage,
      indicator: selectedIndicator,
    });
    api
      .get(`/api/report/summary?${params.toString()}`)
      .then((response) => {
        setSummary(response.data);
        setStatus('Conectado');
      })
      .catch((err) => {
        setStatus('Error');
        setError(err.message);
      });
  }, [selectedProvince, targetCoverage, selectedIndicator]);

  // Reset selected subindicator when base indicator changes
  useEffect(() => {
    setSelectedSubindicator(selectedIndicator === 'si02' ? externalSelectedSubindicator : 'all');
  }, [externalSelectedSubindicator, selectedIndicator]);

  // Validate selected subindicator against options
  const configuredSubindicators = summary?.subindicators ? Object.keys(summary.subindicators) : [];
  useEffect(() => {
    if (!isSi02 || selectedSubindicator === 'all') return;
    if (!configuredSubindicators.includes(selectedSubindicator)) {
      setSelectedSubindicator('all');
    }
  }, [isSi02, selectedSubindicator, configuredSubindicators]);

  // Set default month when data finishes loading
  const selectedSubindicatorSummary = useMemo(() => {
    return isSi02 && selectedSubindicator !== 'all' ? summary?.subindicators?.[selectedSubindicator] : null;
  }, [isSi02, selectedSubindicator, summary]);

  const viewSummary = selectedSubindicatorSummary ?? summary;

  useEffect(() => {
    if (!viewSummary?.monthly?.length) return;

    const monthsWithData = viewSummary.monthly.filter((item) => item.denominator > 0);
    const cutoffMonthKey = summary?.cut_off_date
      ? `${new Date(summary.cut_off_date).getUTCFullYear()}_${new Date(summary.cut_off_date).getUTCMonth() + 1}`
      : '';
    const availableCutoffMonth = monthsWithData.find((item) => buildMonthKey(item) === cutoffMonthKey);
    const fallbackMonth = [...monthsWithData].reverse()[0] ?? viewSummary.monthly[0];
    setSelectedMonth(buildMonthKey(availableCutoffMonth ?? fallbackMonth));
    setPage(1);
  }, [summary?.cut_off_date, viewSummary]);

  // Memoized metrics and stats
  const viewTarget = viewSummary?.target_coverage ?? targetCoverage;
  const incumplidosCount = viewSummary?.omisos?.length ?? 0;
  const monthsWithData = useMemo(() => {
    return viewSummary?.monthly?.filter((item) => item.denominator > 0) ?? [];
  }, [viewSummary]);

  const currentEvaluationKey = summary?.cut_off_date
    ? `${new Date(summary.cut_off_date).getUTCFullYear()}_${new Date(summary.cut_off_date).getUTCMonth() + 1}`
    : '';
  const currentEvaluationOrder = useMemo(() => {
    return currentEvaluationKey
      ? Number(currentEvaluationKey.split('_')[0]) * 12 + Number(currentEvaluationKey.split('_')[1])
      : 0;
  }, [currentEvaluationKey]);

  const { monthsThroughCurrent, monthsMetThroughCurrent } = useMemo(() => {
    const throughCurrent = currentEvaluationOrder
      ? monthsWithData.filter((item) => buildMonthOrder(item) <= currentEvaluationOrder)
      : monthsWithData;
    const met = throughCurrent.filter((item) => item.semaphore === 'green').length;
    return { monthsThroughCurrent: throughCurrent, monthsMetThroughCurrent: met };
  }, [monthsWithData, currentEvaluationOrder]);

  const currentEvaluationMonth = useMemo(() => {
    return monthsWithData.find((item) => buildMonthKey(item) === currentEvaluationKey);
  }, [monthsWithData, currentEvaluationKey]);

  const currentTargetCount = useMemo(() => {
    return currentEvaluationMonth ? Math.ceil((currentEvaluationMonth.denominator * viewTarget) / 100) : 0;
  }, [currentEvaluationMonth, viewTarget]);

  const currentMissingCount = useMemo(() => {
    return currentEvaluationMonth ? Math.max(0, currentTargetCount - currentEvaluationMonth.numerator) : 0;
  }, [currentEvaluationMonth, currentTargetCount]);

  const selectedMonthItem = useMemo(() => {
    return viewSummary?.monthly?.find((item) => buildMonthKey(item) === selectedMonth);
  }, [viewSummary, selectedMonth]);

  const selectedMonthLabel = selectedMonthItem ? `${selectedMonthItem.month} ${selectedMonthItem.year}` : 'mes seleccionado';

  const monthIncumplidos = useMemo(() => {
    return viewSummary?.omisos?.filter((item) => item.Mes_eva === selectedMonth) ?? [];
  }, [selectedMonth, viewSummary]);

  const totalPages = Math.max(1, Math.ceil(monthIncumplidos.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const paginatedIncumplidos = useMemo(() => {
    return monthIncumplidos.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);
  }, [monthIncumplidos, safePage]);

  const displayStart = monthIncumplidos.length === 0 ? 0 : (safePage - 1) * PAGE_SIZE + 1;
  const displayEnd = Math.min(safePage * PAGE_SIZE, monthIncumplidos.length);

  const handleMonthChange = (event) => {
    setSelectedMonth(event.target.value);
    setPage(1);
  };

  const handleDownload = async () => {
    setDownloadError(null);
    try {
      const downloadParams = new URLSearchParams({
        province: selectedProvince,
        month: selectedMonth,
        indicator: selectedIndicator,
      });
      if (isSi02 && selectedSubindicator !== 'all') {
        downloadParams.set('subindicator', selectedSubindicator);
      }

      const response = await api.get(`/api/report/incumplidos.xlsx?${downloadParams.toString()}`, {
        responseType: 'blob',
      });
      const blobUrl = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = blobUrl;
      const subindicatorSuffix = isSi02 && selectedSubindicator !== 'all' ? `_${selectedSubindicator}` : '';
      link.download = `incumplidos_${selectedIndicator}${subindicatorSuffix}${selectedMonth ? `_${selectedMonth}` : ''}.xlsx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (err) {
      setDownloadError(err.response?.data?.detail || err.message || 'No se pudo descargar el Excel');
    }
  };

  return {
    status,
    summary,
    error,
    downloadError,
    selectedMonth,
    setSelectedMonth,
    selectedSubindicator,
    setSelectedSubindicator,
    page,
    setPage,
    isMc02,
    isSi02,
    selectedSubindicatorSummary,
    viewSummary,
    viewTarget,
    incumplidosCount,
    monthsWithData,
    currentEvaluationKey,
    monthsThroughCurrent,
    monthsMetThroughCurrent,
    currentEvaluationMonth,
    currentTargetCount,
    currentMissingCount,
    selectedMonthItem,
    selectedMonthLabel,
    monthIncumplidos,
    totalPages,
    safePage,
    paginatedIncumplidos,
    displayStart,
    displayEnd,
    handleMonthChange,
    handleDownload,
    buildMonthKey,
  };
}
