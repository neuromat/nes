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

    if (! select_muscle_side.val() || ! muscle_side_field.prop("disabled") ) {
        muscle_side_select_refresh();
    }

    if (emg_electrode_placement.val()) {
        surface_show_field(true);
    }

    emg_electrode_placement.change(function() {
        muscle_side_select_refresh();
    });

    select_electrode.change(function () {
       var electrode_id = $(this).val();
       var description_field = $("#id_description");
        description_field.prop( "disabled", true );

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

        // surface_show_field(false);
        // muscle_side_show_field(false);
        document.getElementById("id_description").value = "";

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
            //select_electrode.change();
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

            if (data_placement.length > 0) {

                muscle_side_show_field(true);

                var string_selected = "";

                var options = '<option value="">---------</option>';

                for (var i = 0; i < data_placement.length; i++) {
                    string_selected = "";
                    if (data_placement[i].pk == select_muscle_side.val()) {
                        string_selected = ' selected="selected"';
                    }
                    options += '<option value="' + data_placement[i].pk + '"' + string_selected + '>' + data_placement[i].fields['name'] + '</option>';
                }
                select_muscle_side.html(options);
            }else {
                muscle_side_show_field(false);
            }
            
        });
        surface_show_field(true);
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

    var emg_electrode_type = $("#id_electrode_type").val();
    var div_start_posture = $("#div-start_posture");
    var start_posture_field = $("#id_start_posture");
    var div_orientation = $("#div-orientation");
    var orientation_field = $("#id_orientation");
    var fixation_on_the_skin_field = $("#id_fixation_on_the_skin");
    var div_fixation_on_the_skin = $("#div-fixation_on_the_skin");
    var reference_electrode_field = $("#id_reference_electrode");
    var div_reference_electrode = $("#div-reference_electrode");
    var clinical_test_field = $("#id_clinical_test");
    var div_clinical_test = $("#div-clinical_test");
    var div_method_of_insertion = $("#div-method_of_insertion");
    var method_of_insertion_field = $("#id_method_of_insertion");
    var div_depth_of_insertion = $("#div-depth_of_insertion");
    var depth_of_insertion_field = $("#id_depth_of_insertion");

    start_posture_field.prop( "disabled", true );
    orientation_field.prop( "disabled", true );
    fixation_on_the_skin_field.prop( "disabled", true );
    reference_electrode_field.prop( "disabled", true );
    clinical_test_field.prop( "disabled", true );
    method_of_insertion_field.prop( "disabled", true );
    depth_of_insertion_field.prop( "disabled", true );

    if (show) {
        var emg_electrode_placement_id = $("#id_emg_electrode_placement").val();
        var url = "/experiment/emg_setting/get_description_by_placement/" + emg_electrode_type + "/" + emg_electrode_placement_id;
        if(emg_electrode_type == "surface"){
            $.getJSON(url, function(data_placement){
                document.getElementById("id_start_posture").value = data_placement.start_posture;
                document.getElementById("id_orientation").value = data_placement.orientation;
                document.getElementById("id_fixation_on_the_skin").value = data_placement.fixation_on_the_skin;
                document.getElementById("id_reference_electrode").value = data_placement.reference_electrode;
                document.getElementById("id_clinical_test").value = data_placement.clinical_test;
            });
            div_start_posture.show();
            div_orientation.show();
            div_fixation_on_the_skin.show();
            div_reference_electrode.show();
            div_clinical_test.show();
            div_method_of_insertion.hide();
            div_method_of_insertion.prop( "disabled", true );
            div_depth_of_insertion.hide();
            div_depth_of_insertion.prop( "disabled", true );
        }else if(emg_electrode_type == "intramuscular"){
            $.getJSON(url, function(data_placement){
                document.getElementById("id_method_of_insertion").value = data_placement.method_of_insertion;
                document.getElementById("id_depth_of_insertion").value = data_placement.depth_of_insertion;
            });
            div_method_of_insertion.show();
            div_depth_of_insertion.show();
            div_start_posture.prop( "disabled", true );
            div_start_posture.hide();
            div_orientation.prop( "disabled", true );
            div_orientation.hide();
            div_fixation_on_the_skin.prop( "disabled", true );
            div_fixation_on_the_skin.hide();
            div_reference_electrode.prop( "disabled", true );
            div_reference_electrode.hide();
            div_clinical_test.prop( "disabled", true );
            div_clinical_test.hide();
        }else if(emg_electrode_type == "needle"){
            $.getJSON(url, function(data_placement){
                
            });
        }

    } else {
        if(emg_electrode_type == "surface"){
            div_start_posture.prop( "disabled", true );
            div_start_posture.hide();
            div_orientation.prop( "disabled", true );
            div_orientation.hide();
            div_fixation_on_the_skin.prop( "disabled", true );
            div_fixation_on_the_skin.hide();
            div_reference_electrode.prop( "disabled", true );
            div_reference_electrode.hide();
            div_clinical_test.prop( "disabled", true );
            div_clinical_test.hide();
        }
        if(emg_electrode_type == "intramuscular"){
            div_method_of_insertion.hide();
            div_method_of_insertion.prop( "disabled", true );
            div_depth_of_insertion.hide();
            div_depth_of_insertion.prop( "disabled", true );
        }

    }
}