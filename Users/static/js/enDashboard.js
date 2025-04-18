document
        .querySelector(".side-nav-toggle")
        .addEventListener("click", function () {
          document.querySelector(".side-nav").classList.toggle("expanded");
        });

      // For mobile view
      const mobileToggle = document.querySelector(".mobile-toggle");

      // Check if screen size is small
      function checkScreenSize() {
        if (window.innerWidth <= 576) {
          mobileToggle.style.display = "flex";
        } else {
          mobileToggle.style.display = "none";
        }
      }

      // Initial check
      checkScreenSize();

      // Listen for resize events
      window.addEventListener("resize", checkScreenSize);

      // Mobile toggle functionality
      mobileToggle.addEventListener("click", function () {
        document.querySelector(".side-nav").classList.toggle("expanded");
      });