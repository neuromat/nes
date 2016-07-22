/**
 * Created by evandro on 5/5/16.
 */

$(function(){
    $("[data-toggle=tooltip]").tooltip();
});

function show_modal_remove_setting(emg_electrode_setting_type){
    var  modal_remove = document.getElementById('remove-electrode-setting');
    modal_remove.setAttribute("value", 'remove-' + emg_electrode_setting_type);
    $('#modalRemoveElectrodeSetting').modal('show');
}

$(document).ready(function () {
    
    var emg_electrode_placement = $("#id_emg_electrode_placement");
    var select_muscle_side = $("select#id_muscle_side");
    var muscle_side_field = $("#id_muscle_side");
    var select_electrode = $("select#id_electrode");
    var select_electrode_type = $("select#id_electrode_type");
    var start_posture_field = $("#id_start_posture");

    if (! select_muscle_side.val() || ! muscle_side_field.prop("disabled") ) {
        muscle_side_select_refresh();
    }

    emg_electrode_placement.change(function() {
        muscle_side_select_refresh();
    });

    select_electrode.change(function () {
       var electrode_id = $(this).val();
       var description_field = $("#id_description");

       var url = "/experiment/emg_setting/get_electrode_model/" + electrode_id + "/attributes";

       if(electrode_id == ""){
           description_field.prop('value', "");
       }else{
           $.getJSON(url, function (electrode) {
               description_field.prop('value', electrode['description']);
           })
       }
    });
    
    select_electrode_type.change(function() {

        var electrode_type = $(this).val();

        if (electrode_type == "") {
            electrode_type = "0";
        }

        var url = "/experiment/emg_setting/get_electrode_by_type/" + electrode_type;

        $.getJSON(url, function(electrode_type_list) {
            var options = '<option value="" selected="selected">---------</option>';
            for (var i = 0; i < electrode_type_list.length; i++) {
                    options += '<option value="' + electrode_type_list[i].pk + '">' + electrode_type_list[i].fields['name'] + '</option>';
            }
            select_electrode.html(options);
            select_electrode.change();
        });
        
        var url = "/experiment/emg_setting/get_electrode_placement_by_type/" + electrode_type;

        $.getJSON(url, function(electrode_placement_list) {
            var options_placement = '<option value="" selected="selected">---------</option>';
            for (var i = 0; i < electrode_placement_list.length; i++) {
                    options_placement += '<option value="' + electrode_placement_list[i].id + '">' + electrode_placement_list[i].description + '</option>';
            }
            emg_electrode_placement.html(options_placement);
            emg_electrode_placement.change();
        });

    });

});

function muscle_side_select_refresh() {

    var emg_electrode_placement_id = $("#id_emg_electrode_placement").val();
    var select_muscle_side = $("select#id_muscle_side");

    if (emg_electrode_placement_id == "") {
        select_muscle_side.html('<option value="" selected="selected">---------</option>');
        muscle_side_show_field(false);
        surface_show_field(false);
    }
    else {
        var url = "/experiment/emg_setting/get_muscle_side_by_electrode_placement/" + emg_electrode_placement_id;

        $.getJSON(url, function(data_placement) {

            if (data_placement.muscle_side.length > 0) {

                muscle_side_show_field(true);

                var string_selected = "";

                var options = '<option value="">---------</option>';
                sides = data_placement.muscle_side;
                for (var i = 0; i < sides.length; i++) {
                    string_selected = "";
                    if (sides[i].pk == select_muscle_side.val()) {
                        string_selected = ' selected="selected"';
                    }
                    options += '<option value="' + sides[i].pk + '"' + string_selected + '>' + sides[i].name + '</option>';
                }
                select_muscle_side.html(options);
            }else {
                muscle_side_show_field(false);
            }

            if(data_placement.anatomical_description_list.length > 0){
                surface_show_field(true);
            }else{
                surface_show_field(false);
            }

        });
    }
}

function muscle_side_show_field(show) {

    var div_muscle_side = $("#div-muscle-side");
    var muscle_side_field = $("#id_muscle_side");

    if (show) {
        muscle_side_field.prop( "disabled", false );
        div_muscle_side.show();
    } else {
        muscle_side_field.prop( "disabled", true );
        div_muscle_side.prop( "disabled", true );
        div_muscle_side.hide();
    }
}

function surface_show_field(show) {

    var div_start_posture = $("#div-start_posture");
    var start_posture_field = $("#id_start_posture");
    var div_orientation = $("#div-orientation");
    var orientation_field = $("#id_orientation");

    if (show) {
        start_posture_field.prop( "disabled", false );
        div_start_posture.show();
        orientation_field.prop( "disabled", false );
        div_orientation.show();
    } else {
        start_posture_field.prop( "disabled", true );
        div_start_posture.prop( "disabled", true );
        div_start_posture.hide();
        orientation_field.prop( "disabled", true );
        div_orientation.prop( "disabled", true );
        div_orientation.hide();
    }
}