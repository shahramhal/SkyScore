document.addEventListener("DOMContentLoaded", function () {
    // Initialize tooltip structure (uncomment if not in HTML)
    const tooltip = document.getElementById('card-tooltip');
    if (tooltip && !tooltip.innerHTML.trim()) {
        tooltip.innerHTML = `
          <div class="tooltip-header">
            <span>Description</span>
            <span class="tooltip-close">&times;</span>
          </div>
          <div class="tooltip-body"></div>
        `;
    }

    // Add click handlers to all card items
    document.querySelectorAll('.card-item, .summary-card').forEach(card => {
        card.addEventListener('click', function (e) {
            e.stopPropagation();
            showTooltip(this);
        });
    });

    // Close button handler
    const closeBtn = document.querySelector('.tooltip-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            hideTooltip();
        });
    }

    // Close tooltip when clicking outside
    document.addEventListener('click', function (e) {
        const tooltip = document.getElementById('card-tooltip');
        if (!tooltip.contains(e.target) &&
            !e.target.closest('.card-item') &&
            !e.target.closest('.summary-card')) {
            hideTooltip();
        }
    });

    // Navigation toggle code
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

function showTooltip(element) {
    const description = element.getAttribute('data-description');
    if (!description) return;

    const tooltip = document.getElementById('card-tooltip');
    if (!tooltip) return;

    const tooltipBody = tooltip.querySelector('.tooltip-body');
    if (!tooltipBody) return;

    // Update tooltip content
    tooltipBody.textContent = description;

    // Position tooltip
    const rect = element.getBoundingClientRect();
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
}

function hideTooltip() {
    const tooltip = document.getElementById('card-tooltip');
    if (tooltip) {
        tooltip.classList.remove('visible');
    }
}