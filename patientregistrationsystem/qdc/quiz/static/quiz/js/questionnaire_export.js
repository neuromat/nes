/**
 *  select fields from doublelist in export
 */

jQuery(document).ready(function ($) {

    $("select[name='from[]']").multiselect();

    var multiselect_lists = $("select[id ^='multiselect']");
    $(multiselect_lists)
        .on('dblclick', function(){
            updateFieldsSelectionCounter();
    });

    var multiselect_buttons = $("button[id ^='multiselect']");
    $(multiselect_buttons).on('click', function(){
        updateFieldsSelectionCounter();
    });



});

function updateFieldsSelectionCounter() {
    var multiselect_to = $("select[name='to[]']");
    var fields_counter = $("span[id ^='badge']");

    $(fields_counter).each(function (index, element){

        $(element).text(multiselect_to.eq(index).children().length);
    });
}
