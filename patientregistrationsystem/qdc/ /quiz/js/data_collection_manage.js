/**
 * Created by evandro on 26/03/18.
 */
$(document).ready(function () {

    var selection_remove_radio = $("#selection_remove");
    var selection_transfer_radio = $("#selection_transfer");
    var transfer_selection_div = $("#transfer_selection_div");

    var button_remove = $("#button_remove");
    var button_transfer = $("#button_transfer");

    selection_remove_radio.click(function () {
        if (transfer_selection_div.css('visibility') != "hidden"){
            transfer_selection_div.css('visibility', 'hidden');
            transfer_selection_div.collapse('hide');
        }
        button_remove.prop('disabled', false);
        button_transfer.prop('disabled', true);
    });

    selection_transfer_radio.click(function () {
        transfer_selection_div.css('visibility', 'visible');
        transfer_selection_div.collapse('show');
        button_remove.prop('disabled', true);
        button_transfer.prop('disabled', false);
    });

});


function check_data_selection(transfer) {

    // check selected data
    is_data_selected = false;
    data_collection_selection = document.getElementsByClassName("data-collection-selection");
    var i;
    for (i = 0; i < data_collection_selection.length; i++) {
        if(data_collection_selection[i].checked){
            is_data_selected = true;
        }
    }

    if (! is_data_selected){
        showErrorMessage(gettext("No data collection selected."));
        return false;
    }

    // when transfer, check target step
    if (transfer){
        is_step_selected = false;
        step_option = document.getElementsByName("transfer_to");
        var i;
        for (i = 0; i < step_option.length; i++) {
            if(step_option[i].checked){
                is_step_selected = true;
            }
        }
        if (! is_step_selected){
            showErrorMessage(gettext("No target step selected."));
            return false;
        }
    }

    return true;
}
