/**
 * Presentation Component: Main Layout không có AppHeader
 */

import React from 'react';

export interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div
      className="font-sans bg-slate-50/90 text-slate-900 flex flex-col overflow-hidden min-h-screen relative"
      style={{ height: '100vh' }}
    >
      {/* Background ambient lighting */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-400/10 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-indigo-400/10 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* Main Content Area */}
      <main
        className="flex-1 overflow-y-auto px-6 py-5 flex flex-col screen-animate"
      >
        <div className="max-w-7xl mx-auto w-full flex-1 flex flex-col">
          {children}
        </div>
      </main>
    </div>
  );
};


