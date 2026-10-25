"use strict";
(() => {
  if (!window.gsap || !window.ScrollTrigger || !window.Lenis) return;
  gsap.registerPlugin(ScrollTrigger);
  const media = gsap.matchMedia();
  media.add("(prefers-reduced-motion: no-preference)", () => {
    const lenis = new Lenis({
      duration: 0.8,
      smoothWheel: true,
      syncTouch: false,
      prevent: (node) => Boolean(node.closest("textarea,select,input")),
    });
    const tick = (time) => lenis.raf(time * 1000);
    gsap.ticker.add(tick);
    lenis.on("scroll", ScrollTrigger.update);
    const intro = gsap
      .timeline({ defaults: { ease: "power3.out" } })
      .from(".title-word", { y: 16, duration: 0.65, stagger: 0.08 })
      .from(".intro p", { y: 9, duration: 0.4 }, 0.12)
      .from(".scene", { y: 14, duration: 0.6 }, 0.1);
    const refresh = () => {
      lenis.resize();
      ScrollTrigger.refresh();
    };
    document.addEventListener("geo:comparison", refresh);
    document.fonts.ready.then(refresh);
    const visibility = () => (document.hidden ? lenis.stop() : lenis.start());
    document.addEventListener("visibilitychange", visibility);
    return () => {
      intro.revert();
      gsap.ticker.remove(tick);
      lenis.destroy();
      document.removeEventListener("geo:comparison", refresh);
      document.removeEventListener("visibilitychange", visibility);
    };
  });
  window.addEventListener("pagehide", () => media.revert(), { once: true });
})();
