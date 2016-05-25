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

    select_manufacturer.change(function() {

        var manufacturer_id = $(this).val();

        if (manufacturer_id == "") {
            manufacturer_id = "0";
        }

        var url = "/experiment/equipment/get_equipment_by_manufacturer/" + eeg_setting_type + "/" + manufacturer_id;


            $.getJSON(url, function(all_equipment) {
                var options = '<option value="" selected="selected">---------</option>';
                for (var i = 0; i < all_equipment.length; i++) {
                    if(eeg_setting_type == "eeg_solution"){
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

        if (equipment_id == "") {
            description_field.prop('value', "");
            if (eeg_setting_type == "eeg_machine") {
                software_version.prop('value', "");
                number_of_channels.prop('value', "");
            }
        } else {

            if (eeg_setting_type == "eeg_solution") {
                var url = "/experiment/solution/" + equipment_id + "/attributes";

                $.getJSON(url, function (solution) {
                    description_field.prop('value', solution['description']);
                });
            }else if(eeg_setting_type == "eeg_filter"){
                var url = "/experiment/filter/" + equipment_id + "/attributes";

                $.getJSON(url, function (filter) {
                    description_field.prop('value', filter['description']);
                });
            }else{
                var url = "/experiment/equipment/" + equipment_id + "/attributes";

                $.getJSON(url, function(equipment) {
                    description_field.prop('value', equipment['description']);
                    if (eeg_setting_type == "eeg_machine") {
                        software_version.prop('value', equipment['software_version']);
                        number_of_channels.prop('value', equipment['number_of_channels']);
                    }
                    if(eeg_setting_type == "eeg_amplifier"){
                        gain.prop('value', equipment['gain']);
                    }
                });
            }

        }
    });
});
