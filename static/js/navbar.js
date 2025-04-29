document.addEventListener('DOMContentLoaded', function () {
    // Only run if server-side active state didn't work
    if (!document.querySelector('.side-nav-link.active')) {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.side-nav-link[href]');

        navLinks.forEach(link => {
            // Compare paths more reliably
            const linkPath = new URL(link.href).pathname;
            if (linkPath === currentPath ||
                currentPath.startsWith(linkPath) && linkPath !== '/') {
                link.classList.add('active');
            }
        });
    }

    // Add smooth transition after initial load
    setTimeout(() => {
        document.body.classList.add('dom-loaded');
    }, 50);
});