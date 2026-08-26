/**
 * DATA WHERE HOUSE? — Slide Presenter Helper
 * Provides timer tracking for 60-second pitch rehearsal and dynamic slide behaviors.
 */

(function () {
  'use strict';

  // Pitch slide timing metadata (in seconds) according to 1-minute script
  const SLIDE_TIMINGS = [
    { slide: 1, targetSec: 8,  name: "Ảo tưởng về sự đơn giản" },
    { slide: 2, targetSec: 10, name: "Thực tế & 5 câu hỏi bế tắc" },
    { slide: 3, targetSec: 7,  name: "Giải pháp: Data Where House?" },
    { slide: 4, targetSec: 18, name: "AI Agent End-to-End Pipeline" },
    { slide: 5, targetSec: 8,  name: "Human-in-the-loop & Guardrails" },
    { slide: 6, targetSec: 6,  name: "Tự động sinh DDL & Sandbox" },
    { slide: 7, targetSec: 8,  name: "Giá trị cốt lõi / Slogan" }
  ];

  let pitchTimer = null;
  let elapsedSeconds = 0;
  let isTimerRunning = false;

  function startPitchTimer() {
    if (isTimerRunning) return;
    isTimerRunning = true;
    elapsedSeconds = 0;
    
    pitchTimer = setInterval(() => {
      elapsedSeconds++;
      const timerDisplay = document.getElementById('pitch-timer');
      if (timerDisplay) {
        const mins = Math.floor(elapsedSeconds / 60);
        const secs = elapsedSeconds % 60;
        timerDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')} / 01:05`;
      }
    }, 1000);
  }

  function stopPitchTimer() {
    clearInterval(pitchTimer);
    isTimerRunning = false;
  }

  function resetPitchTimer() {
    stopPitchTimer();
    elapsedSeconds = 0;
    const timerDisplay = document.getElementById('pitch-timer');
    if (timerDisplay) timerDisplay.textContent = "00:00 / 01:05";
  }

  // Keyboard shortcut: 'T' toggles rehearsal timer
  document.addEventListener('keydown', (e) => {
    if (e.key === 't' || e.key === 'T') {
      if (isTimerRunning) {
        stopPitchTimer();
      } else {
        startPitchTimer();
      }
    } else if (e.key === 'r' || e.key === 'R') {
      resetPitchTimer();
      if (window.Presentation) {
        window.Presentation.goTo(0);
      }
    }
  });

  // Listen to slide changes
  document.addEventListener('slidechange', (e) => {
    const { index, total } = e.detail;
    // Auto start timer on slide 1 if first interaction
    if (index === 0 && !isTimerRunning && elapsedSeconds === 0) {
      // Optional: don't auto start unless user presses 'T' or space
    }
    console.log(`[Presentation] Slide ${index + 1}/${total}`);
  });

  window.PresenterHelper = {
    startTimer: startPitchTimer,
    stopTimer: stopPitchTimer,
    resetTimer: resetPitchTimer,
    timings: SLIDE_TIMINGS
  };
})();
