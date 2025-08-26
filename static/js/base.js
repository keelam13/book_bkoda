document.addEventListener('DOMContentLoaded', function () {
    /**
     * Hides alert messages on the page after a 30 second delay.
     */
    setTimeout(function () {
        document.querySelectorAll('.alert:not(.alert-fix-display)').forEach(function (alert) {
            alert.remove();
        });
    }, 30000);

    /** Back to Top Button Logic */
    const backToTopButton = document.getElementById('back-to-top');
    const scrollThreshold = 300;

    if (backToTopButton) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > scrollThreshold) {
                backToTopButton.style.display = 'block';
            } else {
                backToTopButton.style.display = 'none';
            }
        });

        backToTopButton.addEventListener('click', function (e) {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
});
