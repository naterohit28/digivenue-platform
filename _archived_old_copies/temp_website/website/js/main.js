/**
 * DIGIVENUE — GLOBAL JAVASCRIPT
 * Handles: IntersectionObserver entrance animations,
 *          Navigation scroll behavior,
 *          Mobile menu toggle,
 *          Smooth anchor scrolling.
 *
 * Philosophy: No frameworks. No libraries.
 * Vanilla JS, minimal footprint, maximum control.
 * Every behavior is purposeful and constitutional.
 */

'use strict';

/* ──────────────────────────────────────────
   1. INTERSECTION OBSERVER — ENTRANCE ANIMATIONS
   Watches .fade-up, .fade-in, .slide-right,
   .slide-left, and .img-reveal elements.
   Adds .is-visible when they enter the viewport.
   ────────────────────────────────────────── */

const OBSERVE_THRESHOLD = 0.12;  // 12% visible before trigger
const OBSERVE_MARGIN    = '0px 0px -48px 0px'; // Bottom margin pulls trigger up slightly

function initEntranceObserver() {
  const animatedEls = document.querySelectorAll(
    '.fade-up, .fade-in, .slide-right, .slide-left, .img-reveal'
  );

  if (!animatedEls.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          // Unobserve after trigger — animation plays once
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: OBSERVE_THRESHOLD,
      rootMargin: OBSERVE_MARGIN,
    }
  );

  animatedEls.forEach((el) => observer.observe(el));
}


/* ──────────────────────────────────────────
   2. NAVIGATION SCROLL BEHAVIOR
   Three states:
     — Transparent (at top of page)
     — Opaque + border (scrolled down)
     — Hidden (scrolling down quickly)
     — Revealed (scrolling up)
   ────────────────────────────────────────── */

function initNavScroll() {
  const nav = document.querySelector('.site-nav');
  if (!nav) return;

  let lastScrollY     = window.scrollY;
  let scrollThreshold = 80;    // px scrolled before nav becomes opaque
  let hideThreshold   = 200;   // px scrolled before nav can hide
  let ticking         = false;

  function updateNav() {
    const currentScrollY = window.scrollY;
    const scrollingDown  = currentScrollY > lastScrollY;
    const scrollDelta    = Math.abs(currentScrollY - lastScrollY);

    // Add/remove scrolled state (opaque background)
    if (currentScrollY > scrollThreshold) {
      nav.classList.add('is-scrolled');
    } else {
      nav.classList.remove('is-scrolled');
      nav.classList.remove('is-hidden'); // Never hide at top
    }

    // Hide on scroll down (only past hideThreshold)
    if (currentScrollY > hideThreshold) {
      if (scrollingDown && scrollDelta > 4) {
        nav.classList.add('is-hidden');
      } else if (!scrollingDown) {
        nav.classList.remove('is-hidden');
      }
    }

    lastScrollY = currentScrollY;
    ticking = false;
  }

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(updateNav);
      ticking = true;
    }
  }, { passive: true });
}


/* ──────────────────────────────────────────
   3. MOBILE MENU TOGGLE
   Opens/closes the full-screen mobile drawer.
   Locks body scroll when open.
   ────────────────────────────────────────── */

function initMobileMenu() {
  const nav    = document.querySelector('.site-nav');
  const toggle = document.querySelector('.nav-toggle');
  const drawer = document.querySelector('.nav-mobile-drawer');

  if (!nav || !toggle || !drawer) return;

  function openMenu() {
    nav.classList.add('menu-open');
    document.body.style.overflow = 'hidden';
    toggle.setAttribute('aria-expanded', 'true');
    toggle.setAttribute('aria-label', 'Close menu');
  }

  function closeMenu() {
    nav.classList.remove('menu-open');
    document.body.style.overflow = '';
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open menu');
  }

  toggle.addEventListener('click', () => {
    if (nav.classList.contains('menu-open')) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  // Close menu when a drawer link is clicked
  drawer.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', closeMenu);
  });

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && nav.classList.contains('menu-open')) {
      closeMenu();
    }
  });
}


/* ──────────────────────────────────────────
   4. SMOOTH ANCHOR SCROLLING
   Intercepts internal anchor link clicks.
   Scrolls smoothly, accounting for fixed nav height.
   ────────────────────────────────────────── */

function initSmoothScroll() {
  const nav     = document.querySelector('.site-nav');
  const navHeight = nav ? nav.offsetHeight : 80;

  document.addEventListener('click', (e) => {
    const link = e.target.closest('a[href^="#"]');
    if (!link) return;

    const href   = link.getAttribute('href');
    if (href === '#') return;

    const target = document.querySelector(href);
    if (!target) return;

    e.preventDefault();

    const targetY = target.getBoundingClientRect().top
                    + window.scrollY
                    - navHeight
                    - 24; // 24px breathing room

    window.scrollTo({
      top:      Math.max(0, targetY),
      behavior: 'smooth',
    });
  });
}


/* ──────────────────────────────────────────
   5. ACTIVE NAV LINK TRACKING
   Watches sections in viewport, highlights
   the corresponding nav link.
   ────────────────────────────────────────── */

function initActiveNavLinks() {
  const sections  = document.querySelectorAll('section[id]');
  const navLinks  = document.querySelectorAll('.nav-links a[href^="#"]');

  if (!sections.length || !navLinks.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          navLinks.forEach((link) => {
            link.classList.toggle(
              'is-active',
              link.getAttribute('href') === `#${id}`
            );
          });
        }
      });
    },
    {
      threshold: 0.4, // Section must be 40% visible to activate its link
      rootMargin: '-20% 0px -60% 0px',
    }
  );

  sections.forEach((section) => observer.observe(section));
}


/* ──────────────────────────────────────────
   6. AUDIT LOADER (reusable utility)
   Called by audit.js — exposed globally.
   Simulates scanning progress with staggered
   label reveals and fill animations.
   ────────────────────────────────────────── */

window.DigiVenue = window.DigiVenue || {};

window.DigiVenue.runAuditLoader = function (steps, onComplete) {
  /**
   * steps: Array of { label: string, duration: number }
   * onComplete: callback fired after all steps complete
   */
  const container = document.querySelector('[data-audit-steps]');
  if (!container) {
    if (onComplete) onComplete();
    return;
  }

  let index = 0;

  function runStep() {
    if (index >= steps.length) {
      if (onComplete) onComplete();
      return;
    }

    const step = steps[index];
    const item = container.children[index];

    if (item) {
      item.classList.add('is-active');
      const fill = item.querySelector('.audit-progress__fill');
      if (fill) {
        // Animate fill bar to 100%
        fill.style.width = '0%';
        requestAnimationFrame(() => {
          fill.style.transition = `width ${step.duration}ms var(--ease-out)`;
          fill.style.width = '100%';
        });
      }
    }

    index++;
    setTimeout(runStep, step.duration + 120);
  }

  runStep();
};


/* ──────────────────────────────────────────
   7. UTILITY: Debounce
   Used for resize and scroll handlers.
   ────────────────────────────────────────── */

window.DigiVenue.debounce = function (fn, delay = 100) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
};


/* ──────────────────────────────────────────
   INIT — Run all behaviors on DOM ready
   ────────────────────────────────────────── */

function init() {
  initEntranceObserver();
  initNavScroll();
  initMobileMenu();
  initSmoothScroll();
  initActiveNavLinks();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  // DOM already ready
  init();
}
