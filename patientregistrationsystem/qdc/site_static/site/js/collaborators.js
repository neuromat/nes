/**
 * Created by carlosribas on 27/04/2018.
 */
"use strict";

function show_modal_remove_collaborator(researcher_id) {
    var modal_remove = document.getElementById('removeCollaborator');
    modal_remove.setAttribute("value", 'remove_collaborator-' + researcher_id);

    $('#modalCollaboratorRemove').modal('show');
}