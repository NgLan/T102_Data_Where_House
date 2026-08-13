/**
 * Hook custom debounce giá trị thay đổi theo khoảng thời gian delay
 */

import { useEffect, useState } from 'react';

/**
 * Debounce một giá trị generic T
 * @param value Giá trị đầu vào
 * @param delay Thời gian trễ (ms)
 */
export function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
