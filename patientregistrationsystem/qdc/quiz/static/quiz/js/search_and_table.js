const RESULTS_PER_PAGE = 3;
const list = $("#search-results-patients");
const nameKey = $("#nameKey");
let dataResults = [];
let totalPages = 0;

function pagination(data, page) {
    let start = (page - 1) * RESULTS_PER_PAGE ;
    let end = start + RESULTS_PER_PAGE;
    return data.slice(start, end);
}

function searchSuccessPatient(data, textStatus, jqXHR) {
    dataResults = data.split(/<li>/).map(row => row = '<li>' + row);
    dataResults.shift();
    totalPages = Math.ceil(dataResults.length / RESULTS_PER_PAGE);
    list.html(pagination(dataResults, 1));
}

function searchRequest(url, query){
    $.ajax({
        type: "POST",
        url: url,
        data: {
            'search_text' : query,
            'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
        },
        success: searchSuccessPatient,
        dataType: 'html'
    });
}

function searchAndTable(url, ajaxExtras={}) {
    let page = 1;

    // Handle search requests
    const defaultQuery = ' ';

    //Search for patient in search mode
    nameKey.keyup( function(e) {
        e.target.value !== '' ? searchRequest(url, e.target.value) : searchRequest(url, defaultQuery);
    });

    // Handle pagination control
    $("#nextBtn, #prevBtn").click(function(e) {
        if ((e.target.id === 'nextBtn') && (page !== totalPages)) {
            page++;
        } else if ((e.target.id === 'prevBtn') && (page !== 1)) {
            page--;
        }
        list.html(pagination(dataResults, page));
    });

    // Initial query
    searchRequest(url, defaultQuery);
}