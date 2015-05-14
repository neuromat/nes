/**
 * Created by diogopedrosa on 4/24/15.
 */

$(document).ready(function () {
    var id_number_of_mandatory_components = $("#id_number_of_mandatory_components");
    var all_mandatory_components = $("#id_all_mandatory");
    var not_all_mandatory_components = $("#id_not_all_mandatory");

    if (id_number_of_mandatory_components.val() == "") {
        id_number_of_mandatory_components.prop('disabled', true);
        all_mandatory_components.prop('checked', true);
    } else {
        not_all_mandatory_components.prop('checked', true);
    }

    all_mandatory_components.click(function () {
        id_number_of_mandatory_components.prop('value', "");
        id_number_of_mandatory_components.prop('disabled', true);
        fix_bootstrap_error_message();
    });

    not_all_mandatory_components.click(function () {
        id_number_of_mandatory_components.prop('disabled', false);
        id_number_of_mandatory_components.focus();
    });

    function fix_bootstrap_error_message() {
        setTimeout(function () {
            $("#div_form_number_of_mandatory_components").removeClass("has-error")
            $("#div_for_errors_in_number_of_mandatory_components").children("ul").remove();
            $("#submit_button").removeClass("disabled");
        }, 500);
    }

    $(function(){
        $("[data-toggle=tooltip]").tooltip();
    });
});

    function show_modal_remove(component_configuration_id) {
        var  modal_remove = document.getElementById('removeComponentConfiguration');
        modal_remove.setAttribute( "value", 'remove-' + component_configuration_id);
        $('#modalComponentConfigurationRemove').modal('show');
    }
