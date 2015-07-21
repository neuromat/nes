/**
 * Created by diogopedrosa on 3/19/15.
 */

$(document).ready(function () {
    //Search for patient in search mode
    $('#nameKey').keyup(function() {

        $.ajax({
            type: "POST",
            url: "/patient/search/",
            data: {
                'search_text' : $('#nameKey').val(),
                'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
            },
            success: searchSuccessPatient,
            dataType: 'html'
        });

    });

    function searchSuccessPatient(data, textStatus, jqXHR) {
        $('#search-results-patients').html(data);
    }
});