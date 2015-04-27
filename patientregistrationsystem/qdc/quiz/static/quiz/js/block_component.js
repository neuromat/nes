/**
 * Created by diogopedrosa on 4/24/15.
 */

$(document).ready(function () {
    var id_number_of_mandatory_components = $("#id_number_of_mandatory_components");
    var mandatory_components = $("#mandatory_components");

    if (id_number_of_mandatory_components.val() == "") {
        id_number_of_mandatory_components.prop('disabled', true);
        mandatory_components.prop('checked', true);
    }

    mandatory_components.click(function () {
        var all_mandatory = mandatory_components.is(":checked");

        if (all_mandatory) {
            id_number_of_mandatory_components.prop('value', "");
            id_number_of_mandatory_components.prop('disabled', true);
            fix_bootstrap_error_message();
        } else {
            id_number_of_mandatory_components.prop('disabled', false);
        }
    });

    function fix_bootstrap_error_message() {
        setInterval(function () {
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
