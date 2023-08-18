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
                'search_text': $('#keywords').val(),
                'research_project_id': $('#research_project_id').val(),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            },
            success: searchSuccessKeywords,
            dataType: 'html'
        });
    });

    function searchSuccessKeywords(data, textStatus, jqXHR) {
        $('#search-results-keywords').html(data);
    }

    // Workaround for cleaning end_date input field to avoid error message
    // when start_date (required) is filled and end_date is not filled.
    // TODO:
    // see if it's a matter of Bootstrap Validator and JQuery Date picker
    // libraries.
    $("#id_save_button").click(function (e) {
        console.log($("#id_start_date").val());
        if ( $("#id_end_date").val() == "__/__/____" ) {
            $("#id_end_date").val("");
        }
        if ( $("#id_start_date").val() == "__/__/____" ) {
            $("#id_start_date").val("");
        }
    });
});

function showDialogAndEnableRemoveButton () {
    // "When there is only one single-line text input field in a form, the
    // user agent should accept Enter in that field as a request to submit
    // the form."
    // http://www.w3.org/MarkUp/html-spec/html-spec_8.html#SEC8.2
    // That's why we need to keep the Exclude button disabled.
    $('#remove_button').prop('disabled', false);

    $('#modalRemove').modal('show');
}

function disableRemoveButton() {
    $('#remove_button').prop('disabled', true);
}
