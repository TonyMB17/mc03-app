import { useState, useCallback, useEffect } from 'react';
import api from '../api/client';

export function useDniSearch(selectedProvince, selectedIndicator, selectedSubindicator = 'all') {
  const [dni, setDni] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setResult(null);
    setError(null);
  }, [selectedProvince, selectedIndicator, selectedSubindicator]);

  const search = useCallback(
    async (searchDni) => {
      const targetDni = (searchDni || dni).trim();
      if (!targetDni) {
        setError('Ingrese un DNI valido');
        return;
      }

      setLoading(true);
      setError(null);
      setResult(null);

      try {
        const params = new URLSearchParams({ province: selectedProvince, indicator: selectedIndicator });
        if (selectedIndicator === 'si02' && selectedSubindicator && selectedSubindicator !== 'all') {
          params.set('subindicator', selectedSubindicator);
        }
        const response = await api.get(`/api/search/dni/${targetDni}?${params.toString()}`);
        setResult(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Error en la busqueda');
      } finally {
        setLoading(false);
      }
    },
    [dni, selectedProvince, selectedIndicator, selectedSubindicator],
  );

  const clear = useCallback(() => {
    setResult(null);
    setError(null);
    setDni('');
  }, []);

  return {
    dni,
    setDni,
    result,
    error,
    loading,
    search,
    clear,
  };
}
