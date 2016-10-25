
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

    // $("#modalRemoveMessage").html(gettext("Are you sure you want to delete this use of step from list?"));

    $('#modalComponentConfigurationRemove').modal('show');
}
