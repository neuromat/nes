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

    // alert(muscle_side_field.prop("disabled"));
    // refresh
    if (! select_muscle_side.val() || ! muscle_side_field.prop("disabled") ) {
        muscle_side_select_refresh();
    }

    emg_electrode_placement.change(function() {
        muscle_side_select_refresh();
    });

});

function muscle_side_select_refresh() {

    var emg_electrode_placement_id = $("#id_emg_electrode_placement").val();
    var select_muscle_side = $("select#id_muscle_side");

    if (emg_electrode_placement_id == "") {
        select_muscle_side.html('<option value="" selected="selected">---------</option>');
        muscle_side_show_field(false);
    }
    else {
        var url = "/experiment/emg_setting/get_muscle_side_by_electrode_placement/" + emg_electrode_placement_id;

        $.getJSON(url, function(all_sides) {

            if (all_sides.length > 0) {

                muscle_side_show_field(true);

                var string_selected = "";

                var options = '<option value="">---------</option>';
                for (var i = 0; i < all_sides.length; i++) {
                    string_selected = "";
                    if (all_sides[i].pk == select_muscle_side.val()) {
                        string_selected = ' selected="selected"';
                    }
                    options += '<option value="' + all_sides[i].pk + '"' + string_selected + '>' + all_sides[i].fields['name'] + '</option>';
                }
                select_muscle_side.html(options);
            }
            else {
                muscle_side_show_field(false);
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
