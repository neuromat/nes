/**
 * Created by diogopedrosa on 3/19/15.
 */

$(document).ready(function () {
    //Search for patient in search mode
    $('#subject_name').keyup(function() {
        $.ajax({
            type: "POST",
            url: "/experiment/subject/search/",
            data: {
                'search_text' : $('#subject_name').val(),
                'group_id': $('#group_id').val(),
                'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
            },
            success: searchSuccessSubjects,
            dataType: 'html'
        });
    });

    function searchSuccessSubjects(data, textStatus, jqXHR) {
        $('#search-results-subjects').html(data);
    }
});