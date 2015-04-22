/**
 * Created by diogopedrosa on 4/17/15.
 */

$(document).ready(function () {
    var unlimited_number_of_repetitions = $("#unlimited_number_of_repetitions");
    var id_number_of_repetitions = $("#id_number_of_repetitions");

    var undefined_interval = $("#undefined_interval");
    var id_interval_between_repetitions_value = $("#id_interval_between_repetitions_value");
    var id_interval_between_repetitions_unit = $("#id_interval_between_repetitions_unit");

    if (id_number_of_repetitions.val() == "") {
        id_number_of_repetitions.prop('disabled', true);
        unlimited_number_of_repetitions.prop('checked', true);
    }

    if (id_interval_between_repetitions_value.val() == "") {
        id_interval_between_repetitions_value.prop('disabled', true);
        id_interval_between_repetitions_unit.prop('disabled', true);
        undefined_interval.prop('checked', true);
    }

    function manage_interval_disable_flag() {
        var should_disable = !(
                unlimited_number_of_repetitions.is(":checked") ||
                Number(id_number_of_repetitions.val()) > 1);
        var undefined = $("#undefined_interval").is(":checked")

        id_interval_between_repetitions_value.prop('disabled', should_disable || undefined);
        id_interval_between_repetitions_unit.prop('disabled', should_disable || undefined);

        undefined_interval.prop('disabled', should_disable);

        if (should_disable) {
            fix_bootstrap_error_message();
        }
    }

    function fix_bootstrap_error_message() {
        setInterval(function () {
            $("#div_form_interval_between_repetitions_value").removeClass("has-error")
            $("#div_for_errors_in_interval_between_repetitions_value").children("ul").remove();
            $("#div_form_interval_between_repetitions_unit").removeClass("has-error")
            $("#div_for_errors_in_interval_between_repetitions_unit").children("ul").remove();
            $("#submit_button").removeClass("disabled");
        }, 500);
    }

    unlimited_number_of_repetitions.click(function () {
        var unlimited = unlimited_number_of_repetitions.is(":checked");
        id_number_of_repetitions.prop('disabled', unlimited);
        id_number_of_repetitions.prop('value', "");

        manage_interval_disable_flag();
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
        var should_disable = undefined_interval.is(":checked");

        id_interval_between_repetitions_value.prop('disabled', should_disable);
        id_interval_between_repetitions_unit.prop('disabled', should_disable);

        id_interval_between_repetitions_value.prop('value', "");
        id_interval_between_repetitions_unit.prop('value', "");

        if (should_disable) {
            fix_bootstrap_error_message();
        }

    });
});