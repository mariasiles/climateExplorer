// ────────────────────────────────────────────────────────────────────────
// CLIMATE EXPLORER — scroll progress, nav anchors, lazy iframes, fade-in
// ────────────────────────────────────────────────────────────────────────

(function () {
  "use strict";

  // ── Scroll progress bar ──────────────────────────────────────────────
  const bar = document.querySelector(".scroll-progress");
  function updateProgress() {
    const h = document.documentElement;
    const max = h.scrollHeight - h.clientHeight;
    const pct = max > 0 ? (h.scrollTop / max) * 100 : 0;
    if (bar) bar.style.width = pct + "%";
  }
  document.addEventListener("scroll", updateProgress, { passive: true });
  updateProgress();

  // ── Section dots active state ────────────────────────────────────────
  const dots = document.querySelectorAll(".section-dots a");
  const sections = Array.from(document.querySelectorAll("section[id]"));
  function updateDots() {
    const mid = window.innerHeight / 2;
    let activeIdx = 0;
    sections.forEach((s, i) => {
      const rect = s.getBoundingClientRect();
      if (rect.top <= mid) activeIdx = i;
    });
    dots.forEach((d, i) => d.classList.toggle("active", i === activeIdx));
  }
  document.addEventListener("scroll", updateDots, { passive: true });
  updateDots();

  // ── Fade-in on scroll (IntersectionObserver) ─────────────────────────
  const fadeEls = document.querySelectorAll(".fade-section");
  const fadeObs = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        e.target.classList.add("in");
        fadeObs.unobserve(e.target);
      }
    });
  }, { threshold: 0.08, rootMargin: "0px 0px -8% 0px" });
  fadeEls.forEach((el) => fadeObs.observe(el));

  // ── Lazy-load iframes ────────────────────────────────────────────────
  const lazyFrames = document.querySelectorAll("iframe[data-src]");
  const frameObs = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        const f = e.target;
        f.src = f.dataset.src;
        f.removeAttribute("data-src");
        f.addEventListener("load", () => {
          f.parentElement.classList.add("loaded");
        }, { once: true });
        frameObs.unobserve(f);
      }
    });
  }, { threshold: 0, rootMargin: "300px 0px" });
  lazyFrames.forEach((f) => frameObs.observe(f));

  // ── Smooth scroll for nav-cta scroll-to-top ──────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const id = a.getAttribute("href");
      if (id === "#") return;
      const target = document.querySelector(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  // ── Year in footer ───────────────────────────────────────────────────
  const yr = document.getElementById("year");
  if (yr) yr.textContent = new Date().getFullYear();
})();
