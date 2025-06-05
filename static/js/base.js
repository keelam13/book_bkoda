/**
 * Hides all alert messages on the page after a 5 second delay.
 */
setTimeout(function () {
    document.querySelectorAll('.alert').forEach(function (alert) {
        alert.remove();
    });
}, 5000);