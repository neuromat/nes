/**
 * Created by evandro on 6/9/16.
 */

"use strict";

document.addEventListener("DOMContentLoaded", () => {

    var eeg_setting_field = $("#id_eeg_setting");
    var eeg_cap_size_field = $("#id_eeg_cap_size");

    if (eeg_cap_size_field.prop("value") == "") {
        change_cap_size_according_eeg_setting();
    }

    eeg_setting_field.on("change", function () {
        change_cap_size_according_eeg_setting();
    });

});

async function change_cap_size_according_eeg_setting() {

    var eeg_setting_field = $("#id_eeg_setting");
    var eeg_cap_size_field = $("#id_eeg_cap_size");
    var eeg_setting_id = eeg_setting_field.prop("value");
    var div_cap_size = $("#div-cap_size");

    if (eeg_setting_id == "") { eeg_setting_id = "0"; }
    const url = "/experiment/equipment/get_cap_size_list_from_eeg_setting/" + eeg_setting_id;

    const response_fetch = await fetch(url);
    const all_eeg_cap_size = await response_fetch.json();

    var options = '<option value="" selected="selected">---------</option>';
    for (var i = 0; i < all_eeg_cap_size.length; i++) {
        options += '<option value="' + all_eeg_cap_size[i].pk + '">' + all_eeg_cap_size[i].fields['size'] + '</option>';
    }
    eeg_cap_size_field.html(options);

    if (all_eeg_cap_size.length == 0) {
        eeg_cap_size_field.prop("disabled", true);
        eeg_cap_size_field.prop("required", false);
        div_cap_size.hide();
    } else {
        eeg_cap_size_field.prop("disabled", false);
        eeg_cap_size_field.prop("required", true);
        div_cap_size.show();
    }

    // $.getJSON(url, function(all_eeg_cap_size) {
    //     var options = '<option value="" selected="selected">---------</option>';
    //     for (var i = 0; i < all_eeg_cap_size.length; i++) {
    //         options += '<option value="' + all_eeg_cap_size[i].pk + '">' + all_eeg_cap_size[i].fields['size'] + '</option>';
    //     }
    //     eeg_cap_size_field.html(options);

    //     if (all_eeg_cap_size.length == 0) {
    //         eeg_cap_size_field.prop( "disabled", true );
    //         eeg_cap_size_field.prop( "required", false );
    //         div_cap_size.hide();
    //     } else {
    //         eeg_cap_size_field.prop( "disabled", false );
    //         eeg_cap_size_field.prop( "required", true );
    //         div_cap_size.show();
    //     }
    // });
}
