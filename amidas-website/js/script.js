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

if (ctaForm) {
  ctaForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const name = ctaForm.elements.name.value.trim();

    let lang = "en";
    try {
      lang = localStorage.getItem("amidas-lang") || "en";
    } catch (e) {
      /* ignore */
    }
    const dict = (window.AMIDAS_I18N && window.AMIDAS_I18N[lang]) || {};
    const prefix = dict["contact.form.thanksPrefix"] || "Thanks";
    const body =
      dict["contact.form.thanksBody"] ||
      " — we'll be in touch shortly. You can also reach us at hello@amidas.si.";

    ctaNote.textContent = `${prefix}${name ? ", " + name : ""}${body}`;
    ctaForm.reset();
  });
}
