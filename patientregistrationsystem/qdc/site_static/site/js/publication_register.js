/**
 * Created by evandro on 14/03/17.
 */

"use strict";

function showDialogAndEnableRemoveButton () {
    $('#remove_button').prop('disabled', false);
    $('#modalRemove').modal('show');
}

function show_modal_remove_experiment_from_publication(experiment_id){
    var  modal_remove = document.getElementById('remove-experiment');
    modal_remove.setAttribute("value", 'remove-' + experiment_id);
    $('#modalRemoveExperiment').modal('show');
}
