/**
 * Hook custom đơn giản quản lý đóng/mở Modal UI
 */

import { useState, useCallback } from 'react';

export function useModalState(initialState: boolean = false) {
  const [isOpen, setIsOpen] = useState<boolean>(initialState);

  const openModal = useCallback(() => setIsOpen(true), []);
  const closeModal = useCallback(() => setIsOpen(false), []);
  const toggleModal = useCallback(() => setIsOpen((prev) => !prev), []);

  return {
    isOpen,
    openModal,
    closeModal,
    toggleModal,
  };
}
