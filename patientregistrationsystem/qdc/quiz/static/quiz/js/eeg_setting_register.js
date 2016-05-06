/**
 * Created by evandro on 5/5/16.
 */

$(function(){
    $("[data-toggle=tooltip]").tooltip();
});

function show_modal_remove_equipment(equipment_id){
    var  modal_remove = document.getElementById('remove-equipment');
    modal_remove.setAttribute("value", 'remove-' + equipment_id)
    $('#modalRemoveEquipment').modal('show');
}

