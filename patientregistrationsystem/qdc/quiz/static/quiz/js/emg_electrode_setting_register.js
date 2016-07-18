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
    
    emg_electrode_placement.change(function() {

        var emg_electrode_placement_id = $(this).val();
        var select_muscle_side = $("select#id_muscle_side");

        if (emg_electrode_placement_id == "") {
            emg_electrode_placement_id = "0";
        }

        var url = "/experiment/emg_setting/get_muscle_side_by_electrode_placement/" + emg_electrode_placement_id;

        $.getJSON(url, function(all_sides) {
            var options = '<option value="" selected="selected">---------</option>';
            for (var i = 0; i < all_sides.length; i++) {
                options += '<option value="' + all_sides[i].pk + '">' + all_sides[i].fields['name'] + '</option>';
            }
            select_muscle_side.html(options);
            // select_equipment.change();
        });


    });

});
