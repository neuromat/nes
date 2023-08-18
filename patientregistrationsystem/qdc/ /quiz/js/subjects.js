/**
 * Created by diogopedrosa on 3/19/15.
 */

$(function(){
    $("[data-toggle=tooltip]").tooltip();
});

function show_modal_remove (subject_id){
    var modal_remove = document.getElementById('remove-participant');
    modal_remove.removeAttribute("disabled");
    modal_remove.setAttribute("value", 'remove-' + subject_id);
    $('#modalRemove').modal('show');
}

function disable_remove_button (){
    var modal_remove = document.getElementById('remove-participant');
    modal_remove.setAttribute("disabled", "disabled");
    modal_remove.setAttribute("value", 'remove');
}