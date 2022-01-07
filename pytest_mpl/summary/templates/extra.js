// Remove all elements of class mpl-hash if hash test not run
if (document.body.classList[0] == 'no-hash-test') {
    document.querySelectorAll('.mpl-hash').forEach(function (elem) {
        elem.parentElement.removeChild(elem);
    });
}

// Enable tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
})
