/**
 * Created by evandro on 5/5/16.
 */

$(function(){
    $("[data-toggle=tooltip]").tooltip();
});

$(document).ready(function () {

    var equipment_type = $("#id_equipment_type").prop("value");
    var select_equipment = $("select#id_equipment_selection");
    var select_manufacturer = $("select#id_manufacturer");
    var description_field = $("#id_description");
    var serial_number_field = $("#id_serial_number");
    
    select_manufacturer.change(function() {

        var manufacturer_id = $(this).val();

        if (manufacturer_id == "") {
            manufacturer_id = "0";
        }

        var url = "/experiment/equipment/get_equipment_by_manufacturer/" + equipment_type + "/" + manufacturer_id;

        $.getJSON(url, function(all_equipment) {
            var options = '<option value="" selected="selected">---------</option>';
            for (var i = 0; i < all_equipment.length; i++) {
                options += '<option value="' + all_equipment[i].pk + '">' + all_equipment[i].fields['identification'] + '</option>';
            }
            select_equipment.html(options);
            select_equipment.change();
        });
    });

    select_equipment.change(function() {

        var equipment_id = $(this).val();

        if (equipment_id == "") {
            description_field.prop('value', "");
            serial_number_field.prop('value', "");
        } else {

            var url = "/experiment/equipment/" + equipment_id + "/attributes";

            $.getJSON(url, function(equipment) {
                description_field.prop('value', equipment['description']);
                serial_number_field.prop('value', equipment['serial_number']);
            });
        }
    });
});
