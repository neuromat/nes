/**
 * Created by diogopedrosa on 4/24/15.
 */
"use strict";

$(document).ready(
    function () {
        var id_number_of_mandatory_components = $("#id_number_of_mandatory_components");
        var all_mandatory_components = $("#id_all_mandatory");
        var not_all_mandatory_components = $("#id_not_all_mandatory");

        if (id_number_of_mandatory_components.val() == "") {
            id_number_of_mandatory_components.prop('disabled', true);
            id_number_of_mandatory_components.prop('required', false);
            all_mandatory_components.prop('checked', true);
        } else {
            not_all_mandatory_components.prop('checked', true);
        }

        all_mandatory_components.click(function () {
            id_number_of_mandatory_components.prop('value', "");
            id_number_of_mandatory_components.prop('disabled', true);
            id_number_of_mandatory_components.prop('required', false);
            fix_bootstrap_error_message();
        });

        not_all_mandatory_components.click(function () {
            id_number_of_mandatory_components.prop('disabled', false);
            id_number_of_mandatory_components.prop('required', true);
            id_number_of_mandatory_components.focus();
        });

        function fix_bootstrap_error_message() {
            setTimeout(function () {
                $("#div_form_number_of_mandatory_components").removeClass("has-error")
                $("#div_for_errors_in_number_of_mandatory_components").children("ul").remove();
                $("#submit_button").removeClass("disabled");
            }, 500);
        }

        // Change icon while collapsing or expanding an accordion
        $(".collapsed").click(expand)

        function expand() {
            // Replace right arrow by the down arrow
            $(this).find(".fa-chevron-right").switchClass('fa-chevron-right', 'fa-chevron-down');

            // Change the listener of the click event
            $(this).unbind("click");
            $(this).click(collapse)

            // Replace the title of the tootip
            $(this).children(".panel-heading").attr("data-original-title", gettext("Collapse"));
        }

        $(".expanded").click(collapse)

        function collapse() {
            // Replace down arrow by the right arrow
            $(this).find(".fa-chevron-down").switchClass('fa-chevron-down', 'fa-chevron-right');

            // Change the listener of the click event
            $(this).unbind("click");
            $(this).click(expand)

            // Replace the title of the tootip
            $(this).children(".panel-heading").attr("data-original-title", gettext("Expand"));
        }

        // Following two handlers avoid expanding and collapsing an accordion while clicking to move or remove a line.
        $(".collapsed a").click(function (e) {
            e.stopPropagation();
        });

        $(".expanded a").click(function (e) {
            e.stopPropagation();
        });
    });

// This method is needed because if we use href in the <a/> element directly nothing happens, because of the collapse and
// expand actions of the accordion.
function move_accordion(url) {
    window.location.assign(url);
}

function show_modal_remove(list_name, accordion_position, conf_position) {
    var modal_remove = document.getElementById('removeComponentConfiguration');
    modal_remove.setAttribute("value", 'remove-' + list_name + '-' + accordion_position + '-' + conf_position);

    $("#modalRemoveMessage").html(gettext("Are you sure you want to delete this use of step from list?"));

    $('#modalComponentConfigurationRemove').modal('show');
}

function show_modal_remove_many(list_name, accordion_position, length) {
    var modal_remove = document.getElementById('removeComponentConfiguration');
    modal_remove.setAttribute("value", 'remove-' + list_name + '-' + accordion_position);

    $("#modalRemoveMessage").html(gettext("Are you sure you want to delete these ") + length + gettext("  uses of step from list?"));

    $('#modalComponentConfigurationRemove').modal('show');
}
