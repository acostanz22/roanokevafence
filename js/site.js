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
      if (window.matchMedia("(max-width: 1039px)").matches) closeMenu();
    });
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeMenu();
  });

  var quote = document.querySelector(".quote-card");
  var bar = document.querySelector(".mobile-bar");
  if (quote && bar && "IntersectionObserver" in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          var hide = entry.isIntersecting && entry.intersectionRatio > 0.2;
          bar.classList.toggle("is-hidden", hide);
        });
      },
      { threshold: [0, 0.2, 0.5] }
    );
    observer.observe(quote);
  }
})();
