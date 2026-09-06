document.getElementById("year").textContent = new Date().getFullYear();

const navToggle = document.getElementById("navToggle");
const nav = document.getElementById("nav");

navToggle.addEventListener("click", () => {
  const isOpen = nav.classList.toggle("is-open");
  navToggle.setAttribute("aria-expanded", String(isOpen));
});

nav.addEventListener("click", (event) => {
  if (event.target.tagName === "A") {
    nav.classList.remove("is-open");
    navToggle.setAttribute("aria-expanded", "false");
  }
});

const ctaForm = document.getElementById("ctaForm");
const ctaNote = document.getElementById("ctaNote");

ctaForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const name = ctaForm.elements.name.value.trim();
  ctaNote.textContent = `Thanks${name ? ", " + name : ""} — we'll be in touch shortly. You can also reach us at hello@amidas.si.`;
  ctaForm.reset();
});
