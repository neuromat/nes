/**
 * Created by evandro on 5/5/16.
 */

$(function(){
    $("[data-toggle=tooltip]").tooltip();
});

$(document).ready(function () {

    var equipment_category_id = $("#id_equipment_category").prop("value");
    var select_equipment_model = $("select#id_equipment_model");
    var select_equipment = $("select#id_equipment_selection");
    var select_manufacturer = $("select#id_manufacturer");

    select_manufacturer.change(function() {

        var manufacturer_id = $(this).val();

        if (manufacturer_id == "") {
            manufacturer_id = "0";
        }

        var url = "/experiment/equipment/get_models_by_manufacturer/" + equipment_category_id + "/" + manufacturer_id;

        $.getJSON(url, function(models) {
            var options = '<option value="" selected="selected">---------</option>';
            for (var i = 0; i < models.length; i++) {
                options += '<option value="' + models[i].pk + '">' + models[i].fields['identification'] + '</option>';
            }
            select_equipment_model.html(options);
        });

        url = "/experiment/equipment/get_equipment_by_manufacturer/" + equipment_category_id + "/" + manufacturer_id;

        $.getJSON(url, function(all_equipment) {
            var options = '<option value="" selected="selected">---------</option>';
            for (var i = 0; i < all_equipment.length; i++) {
                options += '<option value="' + all_equipment[i].pk + '">' + all_equipment[i].fields['identification'] + '</option>';
            }
            select_equipment.html(options);
        });
    });

    select_equipment_model.change(function() {

        var model_id = $(this).val();
        var manufacturer_id = select_manufacturer.val();

        if (manufacturer_id == "") {
            manufacturer_id = "0";
        }

        if (model_id == "") {
            model_id = "0";
        }

        var url = "/experiment/equipment/get_equipment_by_manufacturer_and_model/" + equipment_category_id + "/" + manufacturer_id + "/" + model_id;

        $.getJSON(url, function(all_equipment) {
            var options = '<option value="" selected="selected">---------</option>';
            for (var i = 0; i < all_equipment.length; i++) {
                options += '<option value="' + all_equipment[i].pk + '">' + all_equipment[i].fields['identification'] + '</option>';
            }
            select_equipment.html(options);
        });
    });

    select_equipment.change(function() {

        var equipment_id = $(this).val();
        var description_field = $("#id_description");
        var serial_number_field = $("#id_serial_number");

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
