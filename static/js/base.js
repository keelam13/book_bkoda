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
    if (backToTopButton) {
        backToTopButton.addEventListener('click', function (e) {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
});
