(function () {
  var button = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (!button || !nav) return;

  function closeMenu() {
    document.body.classList.remove("nav-open");
    button.setAttribute("aria-expanded", "false");
  }

  button.addEventListener("click", function () {
    var open = document.body.classList.toggle("nav-open");
    button.setAttribute("aria-expanded", open ? "true" : "false");
  });

  nav.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", function () {
      if (window.matchMedia("(max-width: 959px)").matches) closeMenu();
    });
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeMenu();
  });
})();
