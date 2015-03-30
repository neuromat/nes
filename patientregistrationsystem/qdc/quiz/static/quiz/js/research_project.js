/**
 * Created by diogopedrosa on 3/19/15.
 */

$(document).ready(function () {
    //Search for keywords in search mode
    $('#keywords').keyup(function() {
        $.ajax({
            type: "POST",
            url: "/experiment/keyword/search/",
            data: {
                'search_text' : $('#keywords').val(),
                'research_project_id' : $('#research_project_id').val(),
                'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
            },
            success: searchSuccessKeywords,
            dataType: 'html'
        });
    });

    function searchSuccessKeywords(data, textStatus, jqXHR) {
        $('#search-results-keywords').html(data);
    }
});