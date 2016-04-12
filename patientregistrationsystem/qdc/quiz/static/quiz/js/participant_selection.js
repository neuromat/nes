/**
 * Created by evandro on 4/11/16.
 */


$(document).ready(function () {

    var all_participants_radio = $("#id_selection_type_0");
    var selected_participants_radio = $("#id_selection_type_1");
    var selected_participants_fields_div = $("#selected_participants_fields");

    var gender_checkbox = $("#id_gender_selection");
    var gender_options = $("#id_gender");

    var marital_status_checkbox = $("#id_marital_status_selection");
    var marital_status_options = $("#id_marital_status");

    var age_checkbox = $("#id_age_selection");
    var min_age_field = $("#id_min_age");
    var max_age_field = $("#id_max_age");

    selected_participants_radio.click(function () {
        selected_participants_fields_div.prop('disabled', false);
        selected_participants_fields_div.css('visibility', 'visible');
    });

    all_participants_radio.click(function () {
        selected_participants_fields_div.prop('disabled', true);

        if (gender_checkbox.is(":checked")) {gender_checkbox.click();}
        if (marital_status_checkbox.is(":checked")) {marital_status_checkbox.click();}
        if (age_checkbox.is(":checked")) {age_checkbox.click();}

        selected_participants_fields_div.css('visibility', 'hidden');
    });

    gender_checkbox.click(function() {
        if (gender_checkbox.is(":checked")) {
            gender_options.prop('disabled', false);
        } else {
            gender_options.prop('disabled', true);
        }
    });

    marital_status_checkbox.click(function() {
        if (marital_status_checkbox.is(":checked")) {
            marital_status_options.prop('disabled', false);
        } else {
            marital_status_options.prop('disabled', true);
        }
    });

    age_checkbox.click(function() {
        if (age_checkbox.is(":checked")) {
            min_age_field.prop('disabled', false);
            max_age_field.prop('disabled', false);
        } else {
            min_age_field.prop('disabled', true);
            max_age_field.prop('disabled', true);
        }
    });

});
