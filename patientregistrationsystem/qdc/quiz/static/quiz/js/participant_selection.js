/**
 * Created by evandro on 4/11/16.
 */


$(document).ready(function () {

    var all_participants_radio = $("#id_selection_type_0");
    var selected_participants_radio = $("#id_selection_type_1");
    var selected_participants_fields_div = $("#selected_participants_fields");

    selected_participants_radio.click(function () {
        selected_participants_fields_div.css('visibility', 'visible');
    });

    all_participants_radio.click(function () {
        selected_participants_fields_div.css('visibility', 'hidden');
    });

})

