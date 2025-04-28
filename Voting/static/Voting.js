document.addEventListener("DOMContentLoaded", function () {
    // Get the tooltip element we already have in HTML
    const tooltip = document.getElementById('card-tooltip');

    // Create tooltip content structure
    tooltip.innerHTML = `
      <div class="tooltip-header">
        <span>Description</span>
        <span class="tooltip-close">&times;</span>
      </div>
      <div class="tooltip-body"></div>
    `;

    const tooltipBody = tooltip.querySelector('.tooltip-body');
    const closeBtn = tooltip.querySelector('.tooltip-close');
    let activeCard = null;

    // Function to close tooltip
    function closeTooltip() {
        tooltip.classList.remove('visible');
        if (activeCard) {
            activeCard.classList.remove('active-tooltip');
            activeCard = null;
        }
    }

    // Close button event
    closeBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        closeTooltip();
    });

    // Card click events
    document.querySelectorAll('.card-item').forEach(card => {
        card.addEventListener('click', function (e) {
            e.stopPropagation();

            const description = this.getAttribute('data-description');
            if (!description) return;

            // If clicking the same card, toggle the tooltip
            if (activeCard === this) {
                closeTooltip();
                return;
            }

            // Close any existing tooltip
            if (activeCard) {
                activeCard.classList.remove('active-tooltip');
            }

            // Update tooltip content
            tooltipBody.textContent = description;
            activeCard = this;
            this.classList.add('active-tooltip');

            // Position tooltip
            const rect = this.getBoundingClientRect();
            tooltip.style.left = `${rect.left}px`;
            tooltip.style.top = `${rect.bottom + window.scrollY + 8}px`;

            // Adjust if going off screen
            const tooltipRect = tooltip.getBoundingClientRect();
            if (tooltipRect.right > window.innerWidth) {
                tooltip.style.left = `${window.innerWidth - tooltipRect.width - 8}px`;
            }
            if (tooltipRect.bottom > window.innerHeight) {
                tooltip.style.top = `${rect.top + window.scrollY - tooltipRect.height - 8}px`;
            }

            tooltip.classList.add('visible');
        });
    });

    // Close tooltip when clicking outside
    document.addEventListener('click', function (e) {
        if (!tooltip.contains(e.target)) {
            closeTooltip();
        }
    });

    // Keep your existing navigation toggle code
    const sideNavToggle = document.querySelector(".side-nav-toggle");
    const mobileToggle = document.querySelector(".mobile-toggle");
    const sideNav = document.querySelector(".side-nav");
    const mainContent = document.querySelector(".main-content");

    function toggleNav() {
        sideNav.classList.toggle("collapsed");
        mainContent.classList.toggle("expanded");
    }

    if (sideNavToggle) {
        sideNavToggle.addEventListener("click", toggleNav);
    }

    if (mobileToggle) {
        mobileToggle.addEventListener("click", function () {
            sideNav.classList.toggle("mobile-open");
        });
    }
});