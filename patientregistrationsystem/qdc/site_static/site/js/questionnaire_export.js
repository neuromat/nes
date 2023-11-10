/**
 *  select fields from doublelist in export
 */
"use strict";

document.addEventListener("DOMContentLoaded", () => {
    //$("select[name='from[]']").multiselect({ keepRenderingSort: true });

    var multiselect_lists = $("select[id ^='multiselect']");
    $(multiselect_lists)
        .on('dblclick', function () {
            updateFieldsSelectionCounter();
        });

    var multiselect_buttons = $("button[id ^='multiselect']");
    $(multiselect_buttons).on('click', function () {
        updateFieldsSelectionCounter();
        if ($('li#questionnaires_from_experiments_tab').hasClass("active")) {
            updateFieldsSelectionCounter_Experiment();
        }
    });

});

function updateFieldsSelectionCounter() {
    var multiselect_to = $("select[name='to[]']");
    var fields_counter = $("span[id ^='badge']");

    $(fields_counter).each(function (index, element) {
        $(element).text(multiselect_to.eq(index).children().length);
    });
}

function updateFieldsSelectionCounter_Experiment() {
    var multiselect_to = $("select[name='to_experiment[]']");
    var fields_counter = $("span[id ^='badge_experiment']");

    $(fields_counter).each(function (index, element) {
        $(element).text(multiselect_to.eq(index).children().length);
    });
}

function validateFormExport() {
    var checkbox_per_participant = $("#id_per_participant").prop("checked");
    var checkbox_per_questionnaire = $("#id_per_questionnaire").prop("checked");
    var select_participants_attributes = $("select[name='patient_selected'] option:selected").length
    var fields_selected = $("select[name='to[]'] option:selected").length;
    // var fields_counter = $("span[id ^='badge']");

    // $(fields_counter).each(function (index, element) {
    //     fields_selected = fields_selected + parseInt($(element).text());
    // });

    if (fields_selected > 0) {
        if (!(checkbox_per_participant || checkbox_per_questionnaire)) {
            // error: when there is at least one questionnaire field selected,
            // per participant/questionnaire must be selected
            return 1;
        }
    }
    else {
        if (checkbox_per_participant || checkbox_per_questionnaire) {
            // warning: it is good to know that if at least one per participant/questionnaire is selected,
            // at least one questionnaire field have to be selected
            return 2;
        }

    }

    if (!select_participants_attributes) {
        return 3;
    }

    return 0;
}

function onClickRun() {
    var field_counter = $("span[id ^='badge']:first");
    var check_validation = validateFormExport();

    if (check_validation == 0) {
        return true;
    }
    else {
        if (check_validation == 1) {
            showErrorMessage(gettext("Either one or both Per participant/Per questionnaire must be set."));
            $("#id_per_participant").trigger("focus");
        }
        else if (check_validation == 2) {
            showWarningMessage(gettext("At least one questionnaire field have to be set"));
            $(field_counter).trigger("focus");
        }
        else if (check_validation == 3) {
            showWarningMessage(gettext("At least one field from participant have to be set"));
        }
        return false;
    }
}

function validate_participant_form() {
    var patient_selected = $("#patient_selected");
    var len = $("select[name='patient_selected'] option:selected").length;
    return !!len;
}

function validate_questionnaire_form() {
    var to_experiment = $("#to_experiment[]");
    var len_ent = $("select[name='to[]'] option:selected").length;
    var len_exp = $("select[name='to_experiment[]'] option:selected").length;

    return !!(len_ent || len_exp);
}

function onClickRunfromExperiment() {
    var checkbox_per_participant = $("#id_per_participant").prop("checked");
    var checkbox_per_questionnaire = $("#id_per_questionnaire").prop("checked");
    if (checkbox_per_participant && checkbox_per_questionnaire) {
        if (validate_participant_form())
            return true;
        else
            showWarningMessage(gettext("At least one field from participant/questionnaire have to be set."));
        return false;
    } else if (checkbox_per_participant && !checkbox_per_questionnaire) {
        if (validate_participant_form()) return true;
        else
            showWarningMessage(gettext("At least one field from participant have to be set."));
        return false;
    }
}