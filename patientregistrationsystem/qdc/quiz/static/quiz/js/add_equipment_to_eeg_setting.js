/**
 * Created by evandro on 5/5/16.
 */

$(function(){
    $("[data-toggle=tooltip]").tooltip();
});

$(document).ready(function () {

    var eeg_setting_type = $("#eeg_setting_type").prop("value");
    var select_equipment = $("select#id_equipment_selection");
    var select_manufacturer = $("select#id_manufacturer");
    var description_field = $("#id_description");
    var software_version = $("#id_software_version");
    var number_of_channels = $("#id_number_of_channels");
    var gain = $("#id_gain");

    var select_localization_system = $("#id_localization_system_selection");
    var system_number_of_electrodes = $("#id_system_number_of_electrodes");

    var equipment_type = eeg_setting_type;
    if (equipment_type == "eeg_electrode_net_system") {
        equipment_type = "eeg_electrode_net";
    }

    select_manufacturer.change(function() {

        var manufacturer_id = $(this).val();

        if (manufacturer_id == "") {
            manufacturer_id = "0";
        }

        var url = "/experiment/equipment/get_equipment_by_manufacturer/" + equipment_type + "/" + manufacturer_id;

        $.getJSON(url, function(all_equipment) {
            var options = '<option value="" selected="selected">---------</option>';
            for (var i = 0; i < all_equipment.length; i++) {
                if(equipment_type == "eeg_solution"){
                    options += '<option value="' + all_equipment[i].pk + '">' + all_equipment[i].fields['name'] + '</option>';
                }else{
                    options += '<option value="' + all_equipment[i].pk + '">' + all_equipment[i].fields['identification'] + '</option>';
                }

            }
            select_equipment.html(options);
            select_equipment.change();
        });

    });

    select_equipment.change(function() {

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

                url = "/experiment/solution/" + equipment_id + "/attributes";

                $.getJSON(url, function(solution){
                   description_field.prop('value', solution['description']) ;
                });

            } else {

                url = "/experiment/equipment/" + equipment_id + "/attributes";

                $.getJSON(url, function(equipment) {
                    description_field.prop('value', equipment['description']);
                    if (equipment_type == "eeg_machine") {
                        software_version.prop('value', equipment['software_version']);
                        number_of_channels.prop('value', equipment['number_of_channels']);
                    }
                    if(equipment_type == "eeg_amplifier"){
                        gain.prop('value', equipment['gain']);
                    }
                });

                // In the EEG Electrode Net Setting, when there is not Localization System
                if (equipment_type == "eeg_electrode_net" && select_localization_system.val() == "" ) {

                    // update the electrode net list

                    url = "/experiment/equipment/get_localization_system_by_electrode_net/" + equipment_id;

                    $.getJSON(url, function(all_localization_system) {
                        var options = '<option value="" selected="selected">---------</option>';
                        for (var i = 0; i < all_localization_system.length; i++) {
                            options += '<option value="' + all_localization_system[i].pk + '">' + all_localization_system[i].fields['name'] + '</option>';
                        }
                        select_localization_system.html(options);
                        select_localization_system.change();
                    });

                }
            }

        }
    });
    
    select_localization_system.change(function() {

        var system_id = $(this).val();

        if (system_id == "") {
            system_number_of_electrodes.prop('value', "");
        } else {

            var url = "/experiment/eeg_localization_system/" + system_id + "/attributes";

            $.getJSON(url, function(eeg_localization_system) {
                system_number_of_electrodes.prop('value', eeg_localization_system['number_of_electrodes']);
            });

            // When there is not Equipment selected
            if (select_equipment.val() == "") {

                // Update Equipment List (according the filters of 'Manufacturer', and 'Localization System')

                var manufacturer_id = select_manufacturer.val();
                if (manufacturer_id == "") {
                    manufacturer_id = "0";
                }

                url = "/experiment/equipment/get_equipment_by_manufacturer_and_localization_system/" + manufacturer_id + "/" + system_id;

                $.getJSON(url, function(all_equipment) {
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
