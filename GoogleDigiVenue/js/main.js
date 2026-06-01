/**
 * DIGIVENUE — GLOBAL JAVASCRIPT
 * Handles: IntersectionObserver entrance animations,
 *          Navigation scroll behaviour,
 *          Mobile menu toggle,
 *          Smooth anchor scrolling.
 *
 * Philosophy: No frameworks. No libraries.
 * Vanilla JS, minimal footprint, maximum control.
 * Every behaviour is purposeful and constitutional.
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
      behaviour: 'smooth',
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
   8. FLOATING WHATSAPP BUTTON
   Injected into every page. Fixed bottom-right.
   Adapts label on desktop, icon-only on mobile.
   ────────────────────────────────────────── */

function initWhatsAppFloat() {
  // Don't add if one already exists in the HTML
  if (document.querySelector('.wa-float')) return;

  const wa = document.createElement('a');
  wa.href = 'https://wa.me/919819576256?text=I%20would%20like%20to%20know%20more%20about%20DigiVenue%20for%20my%20banquet%20hall.';
  wa.className = 'wa-float';
  wa.target = '_blank';
  wa.rel = 'noopener noreferrer';
  wa.setAttribute('aria-label', 'Chat on WhatsApp');

  wa.innerHTML = `
    <svg class="wa-float__icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
    </svg>
    <span class="wa-float__label">Chat on WhatsApp</span>
  `;

  document.body.appendChild(wa);
}


/* ──────────────────────────────────────────
   9. COUNT-UP ANIMATION
   ────────────────────────────────────────── */

function initCountUp() {
  const els = document.querySelectorAll('.countup[data-target]');
  if (!els.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el     = entry.target;
        const target = parseInt(el.dataset.target, 10);
        const duration = 1400;
        const start    = performance.now();

        function tick(now) {
          const elapsed  = now - start;
          const progress = Math.min(elapsed / duration, 1);
          const eased = 1 - Math.pow(1 - progress, 3);
          el.textContent = Math.round(eased * target);
          if (progress < 1) requestAnimationFrame(tick);
        }

        requestAnimationFrame(tick);
        observer.unobserve(el);
      });
    },
    { threshold: 0.3 }
  );

  els.forEach((el) => observer.observe(el));
}


/* ──────────────────────────────────────────
   10. GROWTH CHART LINE DRAW
   ────────────────────────────────────────── */

function initGrowthChart() {
  const chart = document.querySelector('.growth-viz__chart');
  if (!chart) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.25 }
  );

  observer.observe(chart);
}


/* ──────────────────────────────────────────
   INIT — Run all behaviors on DOM ready
   ────────────────────────────────────────── */

function init() {
  initEntranceObserver();
  initNavScroll();
  initMobileMenu();
  initSmoothScroll();
  initActiveNavLinks();
  initWhatsAppFloat();
  initCountUp();
  initGrowthChart();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  // DOM already ready
  init();
}
