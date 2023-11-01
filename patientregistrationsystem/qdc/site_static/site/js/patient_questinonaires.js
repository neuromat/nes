/**
 * Created by diogopedrosa on 3/18/15.
 */

// The inclusion of disabled class in a submit button can't be done in the
// template, because Bootstrap overwrite it.
"use strict";
document.addEventListener("DOMContentLoaded", () => {
    setTimeout(function() { $("#save_submit_button").addClass("disabled"); }, 50);

    var additional_survey_selected = $("#additional_survey_selected");
    
    additional_survey_selected.on("change", function () {
        var selected = $("#additional_survey_selected option:selected");
        var fill_button = $("#fill_button");
        if (selected.val() == '') {
            fill_button.attr('disabled', true);
            fill_button.attr('href', '');
        } else {
            var href_template = fill_button.attr('href_template');
            fill_button.attr('disabled', false);
            fill_button.attr('href', href_template.replace('{survey_id}', selected.val()));
        }
    })
});

function showAdditionalSurveyDialog() {
    $('#modalAdditionalSurvey').modal('show');
}
