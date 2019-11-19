/**
 * Created by diogopedrosa on 3/19/15.
 */

$(document).ready(function () {
    const list = $('#search-results-patients');
    let dataResults = [];
    let page = 1;
    let resultsPerPage = 14;
    let totalPages = 0;

    // Handle string results
    function searchSuccessPatient(data, textStatus, jqXHR) {
        dataResults = data.split(/<li>/).map(row => row = '<li>' + row);
        dataResults.shift();
        totalPages = Math.ceil(dataResults.length / resultsPerPage);
        list.html(pagination(dataResults, page, resultsPerPage));
    }

    // Handle search requests
    const defaultQuery = ' ';

    //Search for patient in search mode
    $('#nameKey').keyup( function(e){
        e.target.value !== '' ? searchRequest(e.target.value) : searchRequest(defaultQuery);
    });

    function searchRequest(query){
        $.ajax({
            type: "POST",
            url: "/patient/search/",
            data: {
                'search_text' : query,
                'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
            },
            success: searchSuccessPatient,
            dataType: 'html'
        });
    }

    // Handle results pagination
    function pagination(data, page, resultsPerPage) {
        let start = (page - 1) * resultsPerPage ;
        let end = start + resultsPerPage;
        return data.slice(start, end);
    }

    // Handle pagination control
    $('#nextBtn, #prevBtn').click(function(e) {
        if ((e.target.id === 'nextBtn') && (page !== totalPages)){
            page++;
        } else if ((e.target.id === 'prevBtn') && (page !== 1)) {
            page--;
        }
        list.html(pagination(dataResults, page, resultsPerPage));
    });

    // Initial query
    searchRequest(defaultQuery);
});