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