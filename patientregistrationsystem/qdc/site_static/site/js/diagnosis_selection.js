/**
 * Created by mruizo on 27/01/17.
 */

$(document).ready(function () {

    $('#get_diagnosis').on("keyup", function () {
        var get_diagnosis = $('#get_diagnosis');

        fetch_post(
            "/export/get_diagnosis/",
            {
                'search_text': (get_diagnosis.val().length >= 3 ? get_diagnosis.val() : ''),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),
            },
            searchSuccessDiagnoses,
        );

        // $.ajax({
        //     type: "POST",
        //     url: "/export/get_diagnosis/",
        //     data: {
        //         'search_text': (get_diagnosis.val().length >= 3 ? get_diagnosis.val() : ''),
        //         'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),
        //     },
        //     success: searchSuccessDiagnoses,
        //     dataType: 'html'

        // });
    });

    function searchSuccessDiagnoses(data, textStatus, jqXHR) {
        $('#search-results-diagnosis').html(data);
    }

    $('#get_diseases').autocomplete({
        source: "/experiment/group_diseases/cid-10/",
        minLength: 3,
    });

});