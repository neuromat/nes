/**
 * Created by diogopedrosa on 3/19/15.
 */

$(function(){
    $("[data-toggle=tooltip]").tooltip();
});

function show_modal_remove (subject_id){
    var  modal_remove = document.getElementById('remove-participant');
    modal_remove.removeAttribute("disabled");
    modal_remove.setAttribute("value", 'remove-' + subject_id);
    $('#modalRemove').modal('show');
}

function disable_remove_button (){
    var  modal_remove = document.getElementById('remove-participant');
    modal_remove.setAttribute("disabled", "disabled");
    modal_remove.setAttribute("value", 'remove');
}

$(document).ready(function () {
    const list = $("#search-results-patients");
    let dataResults = [];
    let page = 1;
    let resultsPerPage = 5;
    let totalPages = 0;

    // Handle string results
    function searchSuccessSubjects(data, textStatus, jqXHR) {
        dataResults = data.split(/<li>/).map(row => row = '<li>' + row);
        dataResults.shift();
        totalPages = Math.ceil(dataResults.length / resultsPerPage);
        list.html(pagination(dataResults, page, resultsPerPage));
    }

    // Handle search requests
    const defaultQuery = ' ';

    //Search for patient in search mode
    $('#subject_name').keyup( function(e){
        e.target.value !== '' ? searchRequest(e.target.value) : searchRequest(defaultQuery);
    });

    //Search for patient in search mode
    function searchRequest(query) {
        $.ajax({
            type: "POST",
            url: "/experiment/subject/search/",
            data: {
                'search_text' : query,
                'group_id': $('#group_id').val(),
                'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
            },
            success: searchSuccessSubjects,
            dataType: 'html'
        });
    }

    // Handle results pagination
    function pagination(data, page, resultsPerPage){
        let start = (page - 1) * resultsPerPage ;
        let end = start + resultsPerPage;
        return data.slice(start, end);
    }

    // Handle pagination control
    $('#nextBtn, #prevBtn').click(function(e){
        if((e.target.id === 'nextBtn') && (page !== totalPages)){
            page++;
        } else {

            if((e.target.id === 'prevBtn') && (page !== 1)){
                page--;
            }
        }
        list.html(pagination(dataResults, page, resultsPerPage));
    });

    // Initial query
    searchRequest(defaultQuery);
});