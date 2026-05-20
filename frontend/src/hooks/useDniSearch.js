import { useState, useCallback } from 'react';
import api from '../api/client';

export function useDniSearch(selectedProvince, selectedIndicator) {
  const [dni, setDni] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

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
        const response = await api.get(`/api/search/dni/${targetDni}?${params.toString()}`);
        setResult(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Error en la busqueda');
      } finally {
        setLoading(false);
      }
    },
    [dni, selectedProvince, selectedIndicator],
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
