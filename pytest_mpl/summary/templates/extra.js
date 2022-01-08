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

// Search, sort and filter
var options = {
    valueNames: ['test-name', 'status-sort', 'rms-sort', 'filter-classes',
        'rms-value', 'baseline-hash-value', 'result-hash-value']
};
var resultsList = new List('results', options);
resultsList.sort('status-sort', {order: "desc"});

var filterClasses = [];
var filterElements = document.getElementById('filterForm').getElementsByClassName('filter');
for (var i = 0, elem; elem = filterElements[i++];) {
    filterClasses.push(elem.id);
}
countClasses();

function applyFilters() {
    var cond_and = document.getElementById('filterForm').elements['conditionand'].checked;
    var filters = [];
    var filterElements = document.getElementById('filterForm').getElementsByClassName('filter');
    for (var i = 0, elem; elem = filterElements[i++];) {
        if (elem.checked) {
            filters.push(elem.id);
        }
    }
    if (filters.length == 0) {
        resultsList.filter();  // Show all if nothing selected
        return countClasses();
    }
    resultsList.filter(function (item) {
        var inc = false;
        for (var i = 0, filt; filt = filters[i++];) {
            if (item.values()['filter-classes'].includes(filt)) {
                if (!cond_and) {
                    return true;
                }
                inc = true;
            } else {
                if (cond_and) {
                    return false;
                }
            }
        }
        return inc;
    });
    countClasses();
}

function resetFilters() {
    resultsList.filter();
    document.getElementById("filterForm").reset();
    countClasses();
}

function countClasses() {
    for (var i = 0, filt; filt = filterElements[i++];) {
        var count = 0;
        if (document.getElementById('filterForm').elements['conditionand'].checked) {
            var itms = resultsList.visibleItems;
        } else {
            var itms = resultsList.items;
        }
        for (var j = 0, itm; itm = itms[j++];) {
            if (itm.values()['filter-classes'].includes(filt.id)) {
                count++;
            }
        }
        var badge = filt.parentElement.getElementsByClassName('badge')[0];
        badge.innerHTML = count.toString();
    }
}
