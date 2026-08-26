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

  let currentIndex = 0;

  /**
   * Scales the 1280x720 stage to fit current viewport with crisp 16:9 aspect ratio
   */
  function fitStage() {
    if (!stage) return;
    const paddingX = 40;
    const paddingY = 40;
    const availableWidth = window.innerWidth - paddingX;
    const availableHeight = window.innerHeight - paddingY;

    const scaleX = availableWidth / SLIDE_WIDTH;
    const scaleY = availableHeight / SLIDE_HEIGHT;
    const scale = Math.min(scaleX, scaleY, 1.35); // Allow slight upscale for 2K/4K recording

    stage.style.transform = `scale(${scale})`;
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

      // Re-trigger CSS animations on active slide
      if (isActive) {
        slide.style.animation = 'none';
        void slide.offsetHeight; // trigger reflow
        slide.style.animation = '';
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
   * Toggle fullscreen mode for video recording
   */
  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(err => {
        console.warn(`Fullscreen error: ${err.message}`);
      });
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
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

  // Initialize
  window.addEventListener('resize', fitStage);
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
    getCurrentIndex: () => currentIndex,
    getTotalSlides: () => totalSlides
  };
})();
