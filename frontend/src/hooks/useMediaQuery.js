import { useEffect, useState } from 'react';

function getMediaMatch(query) {
  if (typeof window === 'undefined') return false;
  return window.matchMedia(query).matches;
}

function useMediaQuery(query) {
  const [matches, setMatches] = useState(() => getMediaMatch(query));

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    const updateMatches = () => setMatches(mediaQuery.matches);

    updateMatches();
    mediaQuery.addEventListener('change', updateMatches);
    return () => mediaQuery.removeEventListener('change', updateMatches);
  }, [query]);

  return matches;
}

export default useMediaQuery;
