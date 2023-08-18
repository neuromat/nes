/**
 * Created by mruizo on 20/10/16.
 */


$(document).ready(function () {
    var select_manufacturer = $("select#id_manufacturer");
    var select_tmsdevice = $("select#id_tms_device");
    var select_coilmodel = $("select#id_coil_model");

    select_manufacturer.change(function() {
        var manufacturer_id = $(this).val();

        if (manufacturer_id == "") {
            manufacturer_id = "0";
        }

        var url = "/experiment/equipment/get_equipment_by_manufacturer/tms_device/" + manufacturer_id;

        $.getJSON(url, function(all_equipment) {
            var options = '<option value="" selected="selected">---------</option>';
            for (var i = 0; i < all_equipment.length; i++) {
                    options += '<option value="' + all_equipment[i].pk + '">' + all_equipment[i].fields['identification'] + '</option>';
            }

            select_tmsdevice.html(options);
            select_tmsdevice.change();
        });
    });

    select_tmsdevice.change(function () {
       var tmsdevice_id = $(this).val();
       var description_field = $("#id_description");

       var url = "/experiment/equipment/" + tmsdevice_id + "/attributes";

       if(tmsdevice_id == ""){
           description_field.prop('value', "");
       }else{
           $.getJSON(url, function (equipment) {
               description_field.prop('value', equipment['description']);
           })
       }

    });

    select_coilmodel.change(function () {
       var coilmodel_id = $(this).val();
       var description_field = $("#id_coil_description");

       var url = "/experiment/coilmodel/" + coilmodel_id + "/attributes";

       if(coilmodel_id == ""){
           description_field.prop('value', "");
       }else{
           $.getJSON(url, function (equipment) {
               description_field.prop('value', equipment['description']);
           })
       }

    });

});


