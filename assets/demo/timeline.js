// Plays a demo page as one timeline, so render.py can step it frame by frame.
//
// Every .step appears in document order, `data-wait` seconds after the one
// before it (default 0.05); a step with `data-after="id"` keeps off that
// clock and shows `data-wait` seconds after step id instead. A .type step is
// typed at 30 ms a character. A .step with `data-until="id"` disappears when
// the step with that id appears; put it in a .swap with its replacement so
// the layout does not jump. A <pre class="stream"> becomes a step that shows
// its box, then one step per line. <body data-hold="4"> holds the last frame that long.
//
// The page loops when opened in a browser; render.py pauses it and sets the
// time itself, reading the length from window.demo.duration.

for (const pre of document.querySelectorAll("pre.stream")) {
  pre.innerHTML = pre.innerHTML
    .replace(/^\n|\n$/g, "")
    .split("\n")
    .map((line) => `<div class="step">${line || " "}</div>`)
    .join("");
  pre.classList.add("step");
}

const view = document.querySelector(".screen");
const scroller = view.firstElementChild;
const steps = [...document.querySelectorAll(".step")];
const shownAt = new Map();
const animations = [];
let t = 0;

const schedule = (el, at) => {
  shownAt.set(el, at);
  if (el.id) shownAt.set(el.id, at);
};
for (const el of steps.filter((s) => !s.dataset.after)) {
  schedule(el, (t += Number(el.dataset.wait ?? 0.05)));
  if (el.classList.contains("type")) t += el.textContent.length * 0.03;
}
for (const el of steps.filter((s) => s.dataset.after)) schedule(el, shownAt.get(el.dataset.after) + Number(el.dataset.wait ?? 0));

for (const el of steps) {
  const t = shownAt.get(el);
  el.style.opacity = 0;
  if (el.classList.contains("type")) {
    const n = el.textContent.length;
    animations.push(el.animate(
      [{ opacity: 1, clipPath: "inset(0 100% 0 0)" }, { opacity: 1, clipPath: "inset(0 0 0 0)" }],
      { delay: t * 1000, duration: n * 30, easing: `steps(${n})`, fill: "both" },
    ));
  } else {
    animations.push(el.animate([{ opacity: 0 }, { opacity: 1 }], { delay: t * 1000, duration: 1, fill: "both" }));
  }
}

for (const el of steps.filter((s) => s.dataset.until)) {
  const gone = shownAt.get(el.dataset.until);
  animations.push(el.animate([{ visibility: "visible" }, { visibility: "hidden" }], { delay: gone * 1000, duration: 1, fill: "forwards" }));
}

const duration = Math.max(...shownAt.values()) + Number(document.body.dataset.hold ?? 4);

// A step with `data-scroll` turns the page just before it shows: the element
// named by that id (or the step itself) glides to the top of .screen.
const origin = scroller.getBoundingClientRect().top;
const frames = [{ offset: 0, transform: "translateY(0px)" }];
let y = 0;
for (const el of steps.filter((s) => s.dataset.scroll !== undefined)) {
  const target = document.getElementById(el.dataset.scroll) ?? el;
  const at = shownAt.get(el);
  frames.push({ offset: (at - 0.4) / duration, transform: `translateY(${-y}px)`, easing: "ease-in-out" });
  y = target.getBoundingClientRect().top - origin;
  frames.push({ offset: (at - 0.05) / duration, transform: `translateY(${-y}px)` });
}
frames.push({ offset: 1, transform: `translateY(${-y}px)` });
animations.push(scroller.animate(frames, { duration: duration * 1000, fill: "both", easing: "linear" }));

// CSS animations (spinners, blinking dots) loop on their own.
animations.push(...document.getAnimations().filter((a) => !animations.includes(a)));

window.demo = {
  duration,
  seek(seconds) {
    for (const a of animations) {
      a.pause();
      a.currentTime = seconds * 1000;
    }
  },
};

let start = performance.now();
(function loop(now) {
  if (window.demo.paused) return;
  const s = (now - start) / 1000;
  if (s > duration) start = now;
  window.demo.seek(Math.min(s, duration));
  requestAnimationFrame(loop);
})(start);
