/**
 * Created by diogopedrosa on 3/19/15.
 */

$(function(){
    $("[data-toggle=tooltip]").tooltip();
});

function show_modal_remove (group_id, classification_of_diseases_id){
    var  modal_remove = document.getElementById('removeClassificationOfDiseases');
    modal_remove.setAttribute( "href", '/experiment/diagnosis/delete/' + group_id + '/' + classification_of_diseases_id);
    $('#modalRemoveClassificationOfDiseases').modal('show');
}

function show_modal_remove_experimental_protocol(){
    $('#modalRemoveExperimentalProtocol').modal('show');
}

$(document).ready(function () {
    $('#get_diseases').keyup(function() {
        var get_diseases = $('#get_diseases');
        $.ajax({
            type: "POST",
            url: "/experiment/group_diseases/cid-10/",
            data: {
                'search_text': (get_diseases.val().length >= 3 ? get_diseases.val() : ''),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),
                'group_id': $('#group_id').val()
            },
            success: searchSuccessDiseases,
            dataType: 'html'

        });
    });

    function searchSuccessDiseases(data, textStatus, jqXHR) {
        $('#search-results-diseases').html(data);
    }
});