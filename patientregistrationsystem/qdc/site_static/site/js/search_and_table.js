const RESULTS_PER_PAGE = 14;
const list = $("#list_results");
const searchKey = $("#search_key");
const nextBtn = $("#next_btn");
const prevBtn = $("#prev_btn");
let dataResults = [];
let totalPages = 0;

function pagination(data, page) {
    let start = (page - 1) * RESULTS_PER_PAGE ;
    let end = start + RESULTS_PER_PAGE;
    return data.slice(start, end);
}

function searchSuccessPatient(data, textStatus, jqXHR) {
    //dataResults = data.split(/<li>/).map(row => row = "<li class="list-group-item">" + row)
    dataResults = data.split(/<li>/).map(row => row = "" + row.replace("<a", "<a class='list-group-item list-group-item-action'").replace("</li>", ""));
    dataResults.shift();
    totalPages = Math.ceil(dataResults.length / RESULTS_PER_PAGE);
    list.html(pagination(dataResults, 1));
}

function searchRequest(url, query, ajaxExtras=null){
    let data = {
        'search_text' : query,
        'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
    };
    for (let el in ajaxExtras) {
        if (ajaxExtras.hasOwnProperty(el)) data[el] = ajaxExtras[el];
    }

    $.ajax({
        type: "POST",
        url: url,
        data: data,
        success: searchSuccessPatient,
        dataType: 'html'
    });
}

function searchAndTable(url, ajaxExtras=null, canSeeNames=false) {
    let page = 1;

    // Handle search requests
    const defaultQuery = ' ';

    //Search for patient in search mode
    searchKey.keyup( function(e) {
        e.target.value !== '' ? searchRequest(url, e.target.value, ajaxExtras) : searchRequest(url, defaultQuery, ajaxExtras);
    });

    // Handle pagination control
    nextBtn.click(function () {
        if (page !== totalPages) list.html(pagination(dataResults, ++page));
    });
    prevBtn.click(function () {
        if (page !== 1) list.html(pagination(dataResults, --page));
    });

    // Initial query
    searchRequest(url, defaultQuery, ajaxExtras);
}