
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

function show_modal_remove_team_person(team_person_id) {
    var  modal_remove = document.getElementById('removeTeamPerson');
    modal_remove.setAttribute("value", 'remove-' + team_person_id);

    $('#modalComponentConfigurationRemove').modal('show');
}

function show_modal_alter_is_coordinator(team_person_id) {
    var  modal_change_is_coordinator = document.getElementById('changeIsCoordinator');
    modal_change_is_coordinator.setAttribute("value", 'change-' + team_person_id);

    $('#modalComponentIs_coordinator').modal('show');
}

function hideNewPersonButton() {
    $('#new_person_btn').hide();
}