/**
 * DATA WHERE HOUSE? — Presentation Engine
 * Handles slide navigation, keyboard controls, 16:9 stage scaling, and video presenter mode.
 */

(function () {
  'use strict';

  const SLIDE_WIDTH = 1280;
  const SLIDE_HEIGHT = 720;

  const stage = document.getElementById('stage');
  const progressBar = document.getElementById('progress-bar');
  const slideElements = Array.from(document.querySelectorAll('.slide'));
  const totalSlides = slideElements.length;
  const audioElement = document.getElementById('pitch-audio');
  const audioBtn = document.getElementById('audio-btn');
  const fsBtn = document.getElementById('fs-btn');
  const timerBtn = document.getElementById('timer-btn');

  let currentIndex = 0;

  /**
   * Scales the 1280x720 stage to fit current viewport.
   * When in fullscreen, stretches edge-to-edge with no padding or black side bars.
   */
  function fitStage() {
    if (!stage) return;
    const isFullscreen = !!document.fullscreenElement;

    if (isFullscreen) {
      document.body.classList.add('fullscreen-mode');
      const scaleX = window.innerWidth / SLIDE_WIDTH;
      const scaleY = window.innerHeight / SLIDE_HEIGHT;
      stage.style.transform = `scale(${scaleX}, ${scaleY})`;
    } else {
      document.body.classList.remove('fullscreen-mode');
      const paddingX = 40;
      const paddingY = 40;
      const availableWidth = window.innerWidth - paddingX;
      const availableHeight = window.innerHeight - paddingY;

      const scaleX = availableWidth / SLIDE_WIDTH;
      const scaleY = availableHeight / SLIDE_HEIGHT;
      const scale = Math.min(scaleX, scaleY, 1.35); // Allow slight upscale for 2K/4K recording

      stage.style.transform = `scale(${scale})`;
    }
  }

  /**
   * Go to specific slide index
   * @param {number} targetIndex
   */
  function goToSlide(targetIndex) {
    if (targetIndex < 0 || targetIndex >= totalSlides) return;
    currentIndex = targetIndex;

    slideElements.forEach((slide, idx) => {
      const isActive = idx === currentIndex;
      slide.classList.toggle('active', isActive);

      // Re-trigger CSS animations on inner content elements of active slide
      if (isActive) {
        const animElems = slide.querySelectorAll('.anim-in');
        animElems.forEach(el => {
          el.style.animation = 'none';
          void el.offsetHeight; // trigger reflow
          el.style.animation = '';
        });
      }
    });

    // Update progress bar
    if (progressBar) {
      const progressPercent = ((currentIndex + 1) / totalSlides) * 100;
      progressBar.style.width = `${progressPercent}%`;
    }

    // Dispatch custom slide change event
    document.dispatchEvent(new CustomEvent('slidechange', {
      detail: { index: currentIndex, total: totalSlides, element: slideElements[currentIndex] }
    }));
  }

  function nextSlide() {
    if (currentIndex < totalSlides - 1) {
      goToSlide(currentIndex + 1);
    }
  }

  function prevSlide() {
    if (currentIndex > 0) {
      goToSlide(currentIndex - 1);
    }
  }

  /**
   * Toggle fullscreen mode for video recording (edge-to-edge)
   */
  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().then(() => {
        fitStage();
      }).catch(err => {
        console.warn(`Fullscreen error: ${err.message}`);
      });
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen().then(() => {
          fitStage();
        });
      }
    }
  }

  /**
   * Toggle MP3 Voice Audio playback
   */
  function updateAudioUI() {
    if (!audioBtn || !audioElement) return;
    if (!audioElement.paused) {
      audioBtn.classList.add('playing');
      audioBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i> M (Đang phát)';
    } else {
      audioBtn.classList.remove('playing');
      audioBtn.innerHTML = '<i class="fa-solid fa-volume-xmark"></i> M (Voice)';
    }
  }

  function toggleAudio() {
    if (!audioElement) return;
    if (audioElement.paused) {
      audioElement.play().then(() => {
        updateAudioUI();
        if (window.PresenterHelper && !window.PresenterHelper.isTimerRunning()) {
          window.PresenterHelper.startTimer();
        }
      }).catch(err => {
        console.warn('Audio play error:', err);
      });
    } else {
      audioElement.pause();
      updateAudioUI();
    }
  }

  /**
   * Keyboard shortcuts for seamless video recording
   */
  function handleKeydown(e) {
    // Disable shortcuts if user is inside an input/editable area
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    switch (e.key) {
      case 'ArrowRight':
      case 'PageDown':
      case ' ': // Spacebar
      case 'Enter':
      case 'l':
      case 'L':
        e.preventDefault();
        nextSlide();
        break;

      case 'ArrowLeft':
      case 'PageUp':
      case 'Backspace':
      case 'h':
      case 'H':
        e.preventDefault();
        prevSlide();
        break;

      case 'Home':
        e.preventDefault();
        goToSlide(0);
        break;

      case 'End':
        e.preventDefault();
        goToSlide(totalSlides - 1);
        break;

      case 'f':
      case 'F':
        e.preventDefault();
        toggleFullscreen();
        break;

      case 'm':
      case 'M':
        e.preventDefault();
        toggleAudio();
        break;

      case '1': case '2': case '3': case '4': case '5': case '6': case '7': case '8': case '9':
        const num = parseInt(e.key, 10);
        if (num <= totalSlides) {
          e.preventDefault();
          goToSlide(num - 1);
        }
        break;
    }
  }

  // Mouse click navigation (Right side clicks next, Left side clicks prev)
  function handleStageClick(e) {
    if (e.target.closest('.shortcuts-hint') || e.target.closest('button')) return;
    const rect = stage.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    if (clickX > rect.width * 0.7) {
      nextSlide();
    } else if (clickX < rect.width * 0.3) {
      prevSlide();
    }
  }

  // Auto hide mouse cursor after 2s of inactivity (useful for video recording)
  let cursorTimer;
  function handleMouseMove() {
    document.body.classList.remove('recording-mode');
    clearTimeout(cursorTimer);
    cursorTimer = setTimeout(() => {
      document.body.classList.add('recording-mode');
    }, 2500);
  }

  // Audio listeners
  if (audioElement) {
    audioElement.addEventListener('play', updateAudioUI);
    audioElement.addEventListener('pause', updateAudioUI);
    audioElement.addEventListener('ended', updateAudioUI);
  }

  if (audioBtn) {
    audioBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleAudio();
    });
  }

  if (fsBtn) {
    fsBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleFullscreen();
    });
  }

  if (timerBtn) {
    timerBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (window.PresenterHelper) {
        if (window.PresenterHelper.isTimerRunning()) {
          window.PresenterHelper.stopTimer();
        } else {
          window.PresenterHelper.startTimer();
        }
      }
    });
  }

  // Initialize
  window.addEventListener('resize', fitStage);
  document.addEventListener('fullscreenchange', fitStage);
  document.addEventListener('keydown', handleKeydown);
  if (stage) stage.addEventListener('click', handleStageClick);
  window.addEventListener('mousemove', handleMouseMove);

  // Initial setup
  fitStage();
  goToSlide(0);

  // Expose API globally
  window.Presentation = {
    goTo: goToSlide,
    next: nextSlide,
    prev: prevSlide,
    toggleFullscreen: toggleFullscreen,
    toggleAudio: toggleAudio,
    getCurrentIndex: () => currentIndex,
    getTotalSlides: () => totalSlides
  };
})();
