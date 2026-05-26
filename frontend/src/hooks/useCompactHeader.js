import { useEffect, useState } from 'react';

function useCompactHeader(threshold = 56) {
  const [compact, setCompact] = useState(false);

  useEffect(() => {
    const updateHeaderMode = () => {
      setCompact(window.scrollY > threshold);
    };

    updateHeaderMode();
    window.addEventListener('scroll', updateHeaderMode, { passive: true });
    return () => window.removeEventListener('scroll', updateHeaderMode);
  }, [threshold]);

  return compact;
}

export default useCompactHeader;
