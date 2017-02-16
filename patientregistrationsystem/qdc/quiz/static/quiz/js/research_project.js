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
});

function showDialogAndEnableRemoveButton () {
    // "When there is only one single-line text input field in a form, the user agent should accept Enter in that
    // field as a request to submit the form."
    // http://www.w3.org/MarkUp/html-spec/html-spec_8.html#SEC8.2
    // That's why we need to keep the Exclude button disabled.
    $('#remove_button').prop('disabled', false);

    $('#modalRemove').modal('show');
}

function disableRemoveButton() {
    $('#remove_button').prop('disabled', true);
}

function show_modal_remove_collaborator(collaborator_id) {
    var  modal_remove = document.getElementById('removeCollaborator');
    modal_remove.setAttribute("value", 'remove_collaborator-' + collaborator_id);


    $('#modalCollaboratorRemove').modal('show');
}

function show_modal_alter_coll_is_coordinator(collaborator_id) {
    var modal_change_coll_is_coordinator = document.getElementById('changeCollIsCoordinator');
    modal_change_coll_is_coordinator.setAttribute("value", 'change_collaborator-' + collaborator_id);

    $('#modalComponent_coll_Is_coordinator').modal('show');
}

