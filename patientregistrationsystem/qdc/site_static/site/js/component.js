/**
 * Created by diogopedrosa on 4/17/15.
 */
"use strict";

$(document).ready(function () {
    var unlimited_number_of_repetitions = $("#id_repetitions_0");
    var limited_number_of_repetitions = $("#id_repetitions_1");
    var id_number_of_repetitions = $("#id_number_of_repetitions");

    var interval_div = $("#interval_div");

    var undefined_interval = $("#id_interval_0");
    var defined_interval = $("#id_interval_1");
    var id_interval_between_repetitions_value = $("#id_interval_between_repetitions_value");
    var id_interval_between_repetitions_unit = $("#id_interval_between_repetitions_unit");

    if (id_number_of_repetitions.val() == "") {
        id_number_of_repetitions.prop('disabled', true);
        id_number_of_repetitions.prop('required', false);
        unlimited_number_of_repetitions.prop('checked', true);
    } else {
        limited_number_of_repetitions.prop('checked', true);

        if (id_number_of_repetitions.val() == 1) {
            interval_div.css('visibility', 'hidden');
        }
    }

    if (id_interval_between_repetitions_value.val() == "") {
        id_interval_between_repetitions_value.prop('disabled', true);
        id_interval_between_repetitions_value.prop('required', false);
        id_interval_between_repetitions_unit.prop('disabled', true);
        id_interval_between_repetitions_unit.prop('required', false);
        undefined_interval.prop('checked', true);
    } else {
        defined_interval.prop('checked', true);
    }

    function manage_interval_disable_flag() {
        var should_disable = !(
                unlimited_number_of_repetitions.is(":checked") ||
                Number(id_number_of_repetitions.val()) > 1);
        var undefined = undefined_interval.is(":checked")

        id_interval_between_repetitions_value.prop('disabled', should_disable || undefined);
        id_interval_between_repetitions_unit.prop('disabled', should_disable || undefined);

        if (should_disable) {
            fix_bootstrap_error_message_interval();
            interval_div.css('visibility', 'hidden');
        } else {
            interval_div.css('visibility', 'visible');
        }
    }

    function fix_bootstrap_error_message_interval() {
        setTimeout(function () {
            $("#div_form_interval_between_repetitions_value").removeClass("has-error");
            $("#div_for_errors_in_interval_between_repetitions_value").children("ul").remove();
            $("#div_form_interval_between_repetitions_unit").removeClass("has-error");
            $("#div_for_errors_in_interval_between_repetitions_unit").children("ul").remove();
            $("#submit_button").removeClass("disabled");
        }, 500);
    }

    function fix_bootstrap_error_message_repetitions() {
        setTimeout(function () {
            $("#div_form_number_of_repetitions").removeClass('has-error');
            $("#div_for_errors_in_number_of_repetitions").children('ul').remove();
            $("#submit_button").removeClass('disabled');
        }, 500);
    }

    unlimited_number_of_repetitions.click(function () {
        manage_interval_disable_flag();
        id_number_of_repetitions.prop('value', '');
        id_number_of_repetitions.prop('readonly', true);
        fix_bootstrap_error_message_repetitions();
    });

    limited_number_of_repetitions.click(function () {
        manage_interval_disable_flag();
        id_number_of_repetitions.prop('disabled', false);
        id_number_of_repetitions.prop('readonly', false);
        id_number_of_repetitions.focus();
        fix_bootstrap_error_message_repetitions();
    });

    // Keypress is not always called. That's why we're using keyup.
    id_number_of_repetitions.keyup(function () {
        manage_interval_disable_flag();
    });

    // Sometimes this is useless because the value of the text input is still unchanged when this handler is called.
    id_number_of_repetitions.on("paste", function () {
        manage_interval_disable_flag();
    });

    undefined_interval.click(function () {
        id_interval_between_repetitions_value.prop('disabled', true);
        id_interval_between_repetitions_value.prop('required', false);
        id_interval_between_repetitions_unit.prop('disabled', true);
        id_interval_between_repetitions_unit.prop('required', false);

        id_interval_between_repetitions_value.prop('value', "");
        id_interval_between_repetitions_unit.prop('value', "");

        fix_bootstrap_error_message_interval();
    });

    defined_interval.click(function () {
        id_interval_between_repetitions_value.prop('disabled', false);
        id_interval_between_repetitions_value.prop('required', true);
        id_interval_between_repetitions_unit.prop('disabled', false);
        id_interval_between_repetitions_unit.prop('required', true);

        id_interval_between_repetitions_value.focus();
    });

});

function redirect_with_number_of_uses(url) {
    if (url.indexOf('?') === -1) {
        window.location.assign(url + "?number_of_uses=" + $("#id_number_of_uses_to_insert").val());
    } else {
        window.location.assign(url + "&number_of_uses=" + $("#id_number_of_uses_to_insert").val());
    }
}
