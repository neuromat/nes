$(document).ready(function () {

    $("#unlimited_number_of_fills").click(function () {
        var unlimited = $("#unlimited_number_of_fills").is(":checked");
        $("#number_of_fills").prop('disabled', unlimited);
        $("#number_of_fills").prop('value', "");
    });

    $("#undefined_interval_between_fills").click(function () {
        var undefined = $("#undefined_interval_between_fills").is(":checked");
        $("#interval_between_fills_value").prop('disabled', undefined);
        $("#interval_between_fills_unit").prop('disabled', undefined);

        $("#interval_between_fills_value").prop('value', "");
        $("#interval_between_fills_unit").prop('value', "");
    });

});
