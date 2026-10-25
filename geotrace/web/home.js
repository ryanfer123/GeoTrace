"use strict";

// The reference split is functional independently of the motion libraries.
(() => {
  const split = document.getElementById("home-split");
  const later = document.getElementById("home-later-image");
  const divider = document.getElementById("home-divider");
  const value = document.getElementById("home-split-value");
  split?.addEventListener("input", () => {
    const position = Number(split.value);
    later.style.clipPath = `inset(0 0 0 ${position}%)`;
    divider.style.left = `${position}%`;
    value.value = `${position} / ${100 - position}`;
  });

  document.querySelectorAll(".mobile-menu nav a").forEach((link) => {
    link.addEventListener("click", () => {
      document.querySelector(".mobile-menu").open = false;
    });
  });

  const images = document.querySelectorAll(".comparison-frame img");
  images.forEach((image) => {
    image.addEventListener("error", () => {
      const figure = image.closest("figure");
      if (!figure || figure.querySelector(".image-unavailable")) return;
      const message = document.createElement("p");
      message.className = "image-unavailable";
      message.textContent =
        "The reference image could not be loaded. Open the workspace to inspect the source request and try the comparison again.";
      figure.append(message);
    });
  });

  if (!window.gsap || !window.ScrollTrigger || !window.Lenis) return;
  gsap.registerPlugin(ScrollTrigger);
  const media = gsap.matchMedia();
  media.add("(prefers-reduced-motion: no-preference)", () => {
    // One scroll engine, preserving native layout and accessible controls.
    const lenis = new Lenis({
      duration: 0.8,
      smoothWheel: true,
      syncTouch: false,
      anchors: true,
      prevent: (node) => Boolean(node.closest("input,summary,.mobile-menu")),
    });
    const tick = (time) => lenis.raf(time * 1000);
    gsap.ticker.add(tick);
    lenis.on("scroll", ScrollTrigger.update);

    const intro = gsap.timeline({ defaults: { ease: "power3.out" } });
    intro
      .from(".hero-word", { y: 22, duration: 0.65, stagger: 0.045 }, 0)
      .from(
        ".hero-description,.hero-actions",
        { y: 12, duration: 0.55, stagger: 0.08 },
        0.12,
      )
      .from(".hero-figure", { y: 18, duration: 0.7 }, 0.1);

    const reveals = Array.from(
      document.querySelectorAll(".reveal-heading"),
    ).map((heading) => {
      const originalNodes = Array.from(heading.childNodes);
      const originalLabel = heading.getAttribute("aria-label");
      heading.setAttribute(
        "aria-label",
        originalNodes
          .map((node) => (node.nodeName === "BR" ? " " : node.textContent))
          .join("")
          .replace(/\s+/g, " ")
          .trim(),
      );
      const fragment = document.createDocumentFragment();
      originalNodes.forEach((node) => {
        if (node.nodeType !== Node.TEXT_NODE) {
          fragment.append(node.cloneNode(true));
          return;
        }
        node.textContent.split(/(\s+)/).forEach((part) => {
          if (!part.trim()) {
            fragment.append(document.createTextNode(part));
            return;
          }
          const word = document.createElement("span");
          word.className = "heading-word";
          word.setAttribute("aria-hidden", "true");
          word.textContent = part;
          fragment.append(word);
        });
      });
      heading.replaceChildren(fragment);
      const tween = gsap.from(heading.querySelectorAll(".heading-word"), {
        y: 15,
        duration: 0.55,
        stagger: 0.035,
        ease: "power2.out",
        scrollTrigger: { trigger: heading, start: "top 94%", once: true },
      });
      return {
        revert() {
          tween.revert();
          heading.replaceChildren(...originalNodes);
          if (originalLabel === null) heading.removeAttribute("aria-label");
          else heading.setAttribute("aria-label", originalLabel);
        },
      };
    });
    let active = true;
    const refresh = () => {
      if (!active) return;
      lenis.resize();
      ScrollTrigger.refresh();
    };
    document.fonts.ready.then(refresh);
    images.forEach((image) => image.addEventListener("load", refresh));
    const visibility = () => (document.hidden ? lenis.stop() : lenis.start());
    document.addEventListener("visibilitychange", visibility);
    const disclosures = document.querySelectorAll("details");
    disclosures.forEach((details) =>
      details.addEventListener("toggle", refresh),
    );
    return () => {
      active = false;
      intro.revert();
      reveals.forEach((reveal) => reveal.revert());
      images.forEach((image) => image.removeEventListener("load", refresh));
      document.removeEventListener("visibilitychange", visibility);
      disclosures.forEach((details) =>
        details.removeEventListener("toggle", refresh),
      );
      gsap.ticker.remove(tick);
      lenis.destroy();
    };
  });
  window.addEventListener("pagehide", () => media.revert(), { once: true });
})();
