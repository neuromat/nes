/**
 *  select fields from doublelist in export
 */

jQuery(document).ready(function ($) {

    $("select[name='from[]']").multiselect({
        keepRenderingSort: true
    });

    var multiselect_lists = $("select[id ^='multiselect']");
    $(multiselect_lists)
        .on('dblclick', function(){
            updateFieldsSelectionCounter();
    });

    var multiselect_buttons = $("button[id ^='multiselect']");
    $(multiselect_buttons).on('click', function(){
        updateFieldsSelectionCounter();
    });

});


function updateFieldsSelectionCounter() {
    var multiselect_to = $("select[name='to[]']");
    var fields_counter = $("span[id ^='badge']");

    $(fields_counter).each(function (index, element){

        $(element).text(multiselect_to.eq(index).children().length);
    });
}

function validateFormExport() {

    var checkbox_per_participant = $("#id_per_participant").prop("checked");
    var checkbox_per_questionnaire = $("#id_per_questionnaire").prop("checked");
    var fields_selected = 0;
    var fields_counter = $("span[id ^='badge']");

    //alert(checkbox_per_participant);
    //alert(checkbox_per_questionnaire);

    $(fields_counter).each(function (index, element){
        fields_selected = fields_selected + parseInt($(element).text());
    });

    if (fields_selected) {
        if (! (checkbox_per_participant || checkbox_per_questionnaire) )
        {
            // error: when there is at least one questionnaire field selected,
            // per participant/questionnaire must be selected
            return 1;
        }
    }
    else {
        if (checkbox_per_participant || checkbox_per_questionnaire)
        {
            // warning: it is good to know that if at least one per participant/questionnaire is selected,
            // at least one questionnaire field have to be selected
            return 2;
        }

    }

    return 0;

}

function onClickRun() {
    //alert("entrou click");
    var field_counter = $("span[id ^='badge']:first");
    var check_validation = validateFormExport();

    if (check_validation == 0){
        return true;
    }
    else{
        if (check_validation == 1){
            showErrorMessage(gettext("Either one or both Per participant/Per questionnaire must be set."));
            $("#id_per_participant").focus();
        }
        else{
            showWarningMessage(gettext("At least one questionnaire field have to be set."));
            $(field_counter).focus();
        }
        return false;
    }
}

function validate_participant_form() {
    var patient_selected = $("#patient_selected")
    var len = $("select[name='patient_selected'] option:selected").length;
    if (len)
        return true;
    else
        false;
}

function validate_questionnaire_form() {
    var to_experiment = $("#to_experiment[]")
    var len_ent = $("select[name='to[]'] option:selected").length;
    var len_exp = $("select[name='to_experiment[]'] option:selected").length;

    if (len_ent || len_exp)
        return true;
    else
        false;
}

function onClickRunfromExperiment() {
    // var field_counter = $("span[id ^='badge']:first");
    // var check_validation = ValidateParticipantExport();
    var checkbox_per_participant = $("#id_per_participant").prop("checked");
    var checkbox_per_questionnaire = $("#id_per_questionnaire").prop("checked");
    if (checkbox_per_participant && checkbox_per_questionnaire) {
        if (validate_participant_form())
            return true;
        else
            showWarningMessage(gettext("At least one field from participant/questionnaire have to be set."));
            return false;
    }else if(checkbox_per_participant && !checkbox_per_questionnaire) {
        if (validate_participant_form()) return true;
        else
            showWarningMessage(gettext("At least one field from participant have to be set."));
        return false;
    }
    // }else if(!checkbox_per_participant && checkbox_per_questionnaire){
    //     if(validate_questionnaire_form()) return true;
    //     else
    //         showWarningMessage(gettext("At least one field from participant/questionnaire have to be set."));
    //         return false;
    // }

}
