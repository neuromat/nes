/**
 * Created by evandro on 5/5/16.
 */

"use strict";

$(document).ready(function () {

    var eeg_setting_type = $("#eeg_setting_type").prop("value");
    var select_equipment = $("select#id_equipment_selection");
    var select_manufacturer = $("select#id_manufacturer");
    var description_field = $("#id_description");
    var software_version = $("#id_software_version");
    var number_of_channels = $("#id_number_of_channels");
    var number_of_channels_used = $("#id_number_of_channels_used");
    var gain = $("#id_gain");

    var select_localization_system = $("#id_localization_system_selection");

    var equipment_type = eeg_setting_type;
    if (equipment_type == "eeg_electrode_net_system") {
        equipment_type = "eeg_electrode_net";
    }

    // setting initially the max value of the number of channels
    number_of_channels_used.prop('max', number_of_channels.prop('value'));

    select_manufacturer.change(function () {

        var manufacturer_id = $(this).val();

        if (manufacturer_id == "") {
            manufacturer_id = "0";
        }

        var url = "/experiment/equipment/get_equipment_by_manufacturer/" + equipment_type + "/" + manufacturer_id;

        $.getJSON(url, function (all_equipment) {
            var options = '<option value="" selected="selected">---------</option>';
            for (var i = 0; i < all_equipment.length; i++) {
                if (equipment_type == "eeg_solution") {
                    options += '<option value="' + all_equipment[i].pk + '">' + all_equipment[i].fields['name'] + '</option>';
                } else {
                    options += '<option value="' + all_equipment[i].pk + '">' + all_equipment[i].fields['identification'] + '</option>';
                }

            }
            select_equipment.html(options);
            select_equipment.change();
        });

    });

    select_equipment.change(function () {

        var equipment_id = $(this).val();
        var url = "";

        if (equipment_id == "") {
            description_field.prop('value', "");
            if (equipment_type == "eeg_machine") {
                software_version.prop('value', "");
                number_of_channels.prop('value', "");
            }
        } else {

            if (equipment_type == "eeg_solution") {
                var url = "/experiment/solution/" + equipment_id + "/attributes";

                $.getJSON(url, function (solution) {
                    description_field.prop('value', solution['description']);
                });
            } else if (equipment_type == "filter") {
                var url = "/experiment/filter/" + equipment_id + "/attributes";

                $.getJSON(url, function (filter) {
                    description_field.prop('value', filter['description']);
                });
            } else {
                var url = "/experiment/equipment/" + equipment_id + "/attributes";

                $.getJSON(url, function (equipment) {
                    description_field.prop('value', equipment['description']);
                    if (equipment_type == "eeg_machine") {
                        software_version.prop('value', equipment['software_version']);
                        number_of_channels.prop('value', equipment['number_of_channels']);
                        number_of_channels_used.prop('max', equipment['number_of_channels']);
                    }
                    if (equipment_type == "amplifier") {
                        gain.prop('value', equipment['gain']);
                    }
                });

                // In the EEG Electrode Net Setting, when there is not Localization System
                // if (equipment_type == "eeg_electrode_net" && select_localization_system.val() == "" ) {
                if (equipment_type == "eeg_electrode_net") {

                    // update the electrode net list
                    url = "/experiment/equipment/get_localization_system_by_electrode_net/" + equipment_id;

                    $.getJSON(url, function (all_localization_system) {
                        var first_option = '';
                        var options = '';
                        var has_selected = false;
                        var string_selected = '';
                        for (var i = 0; i < all_localization_system.length; i++) {
                            string_selected = '';
                            if (parseInt(select_localization_system.val()) == all_localization_system[i].pk) {
                                has_selected = true;
                                string_selected = 'selected="selected"'
                            }
                            options += '<option value="' + all_localization_system[i].pk + '" ' + string_selected + '>' + all_localization_system[i].fields['name'] + '</option>';
                        }
                        if (has_selected) {
                            first_option = '<option value="">---------</option>';
                        } else {
                            first_option = '<option value="" selected="selected">---------</option>';
                        }

                        select_localization_system.html(first_option + options);
                        select_localization_system.change();
                    });
                }
            }
        }
    });

    select_localization_system.change(function () {

        var system_id = $(this).val();

        if (system_id != "") {

            // When there is not Equipment selected
            if (select_equipment.val() == "") {

                // Update Equipment List (according the filters of 'Manufacturer', and 'Localization System')

                var manufacturer_id = select_manufacturer.val();
                if (manufacturer_id == "") {
                    manufacturer_id = "0";
                }

                url = "/experiment/equipment/get_equipment_by_manufacturer_and_localization_system/" + manufacturer_id + "/" + system_id;

                $.getJSON(url, function (all_equipment) {
                    var options = '<option value="" selected="selected">---------</option>';
                    for (var i = 0; i < all_equipment.length; i++) {
                        options += '<option value="' + all_equipment[i].pk + '">' + all_equipment[i].fields['identification'] + '</option>';
                    }
                    select_equipment.html(options);
                    select_equipment.change();
                });
            }
        }
    });

});
