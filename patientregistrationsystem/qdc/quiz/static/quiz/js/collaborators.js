/**
 * Created by carlosribas on 27/04/2018.
 */

function show_modal_remove_collaborator(collaborator_id) {
    var  modal_remove = document.getElementById('removeCollaborator');
    modal_remove.setAttribute("value", 'remove_collaborator-' + collaborator_id);

    $('#modalCollaboratorRemove').modal('show');
}