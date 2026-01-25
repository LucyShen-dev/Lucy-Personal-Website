const revealOnScroll = () => {
  const elements = document.querySelectorAll("[data-reveal]");
  if (!elements.length) {
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
        }
      });
    },
    { threshold: 0.2 }
  );

  elements.forEach((el) => observer.observe(el));
};

const horizontalSections = Array.from(document.querySelectorAll("[data-horizontal]"));
let animationFrame = null;

const updateHorizontalSections = () => {
  animationFrame = null;
  const scrollY = window.scrollY;
  const viewportHeight = window.innerHeight;
  const viewportWidth = window.innerWidth;

  horizontalSections.forEach((section) => {
    const track = section.querySelector(".horizontal-track");
    if (!track) {
      return;
    }

    const totalWidth = track.scrollWidth;
    const scrollDistance = Math.max(0, totalWidth - viewportWidth + 80);
    const sectionHeight = scrollDistance + viewportHeight;
    section.style.height = `${sectionHeight}px`;

    const sectionTop = section.offsetTop;
    const scrollProgress = Math.min(
      1,
      Math.max(0, (scrollY - sectionTop) / Math.max(1, sectionHeight - viewportHeight))
    );
    const translateX = -scrollDistance * scrollProgress;
    track.style.transform = `translateX(${translateX.toFixed(2)}px)`;
  });
};

const requestHorizontalUpdate = () => {
  if (!animationFrame) {
    animationFrame = requestAnimationFrame(updateHorizontalSections);
  }
};

window.addEventListener("resize", requestHorizontalUpdate);
window.addEventListener("scroll", requestHorizontalUpdate, { passive: true });

revealOnScroll();
updateHorizontalSections();

const initTypewriter = () => {
  const headings = document.querySelectorAll("[data-typewriter]");
  if (!headings.length) {
    return;
  }

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const startTypewriter = (heading) => {
    if (heading.dataset.typewriterStarted === "true") {
      return;
    }

    const fullText = heading.dataset.typewriterText || heading.textContent;
    if (!fullText) {
      return;
    }

    heading.dataset.typewriterText = fullText;
    heading.dataset.typewriterStarted = "true";

    if (prefersReducedMotion) {
      heading.textContent = fullText;
      return;
    }

    heading.textContent = "";
    heading.classList.add("is-typing");

    let index = 0;
    const typeNext = () => {
      heading.textContent = fullText.slice(0, index + 1);
      index += 1;
      if (index < fullText.length) {
        const lastChar = fullText[index - 1];
        const delay = lastChar === "." || lastChar === "," ? 180 : lastChar === " " ? 45 : 55;
        window.setTimeout(typeNext, delay);
      }
    };

    window.setTimeout(typeNext, 300);
  };

  const scrollTargets = [];

  headings.forEach((heading) => {
    const trigger = heading.dataset.typewriterTrigger || "load";
    if (trigger === "scroll") {
      scrollTargets.push(heading);
      return;
    }
    startTypewriter(heading);
  });

  if (scrollTargets.length) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            startTypewriter(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.35 }
    );

    scrollTargets.forEach((heading) => observer.observe(heading));
  }
};

const initPolaroidStacks = () => {
  const stacks = document.querySelectorAll("[data-polaroid]");
  if (!stacks.length) {
    return;
  }

  stacks.forEach((stack) => {
    const cards = Array.from(stack.querySelectorAll(".polaroid-card"));
    let isAnimating = false;

    const triggerPrint = (card) => {
      if (!card) {
        return;
      }
      card.classList.add("is-printing");
      const handleAnimationEnd = () => {
        card.classList.remove("is-printing");
        card.removeEventListener("animationend", handleAnimationEnd);
      };
      card.addEventListener("animationend", handleAnimationEnd);
    };

    const updateStack = () => {
      cards.forEach((card, index) => {
        card.style.setProperty("--stack-index", index);
        card.classList.toggle("is-top", index === 0);
      });
    };

    const rotateStack = () => {
      if (isAnimating) {
        return;
      }
      isAnimating = true;
      const topCard = cards[0];
      const nextCard = cards[1];
      if (!topCard || !nextCard) {
        isAnimating = false;
        return;
      }
      triggerPrint(nextCard);

      const handleAnimationEnd = () => {
        cards.push(cards.shift());
        updateStack();
        isAnimating = false;
        nextCard.removeEventListener("animationend", handleAnimationEnd);
      };

      nextCard.addEventListener("animationend", handleAnimationEnd);
    };

    stack.addEventListener("click", (event) => {
      const target = event.target.closest(".polaroid-card");
      if (!target || !target.classList.contains("is-top")) {
        return;
      }
      rotateStack();
    });

    const camera = stack.closest(".polaroid-printer")?.querySelector(".instax-camera");
    if (camera) {
      camera.addEventListener("click", () => {
        rotateStack();
      });
    }

    updateStack();
    triggerPrint(cards[0]);
  });
};

initTypewriter();
initPolaroidStacks();
