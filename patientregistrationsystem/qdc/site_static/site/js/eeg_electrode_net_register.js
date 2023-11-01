/**
 * Created by evandro on 6/13/16.
 */

"use strict";
document.addEventListener("DOMContentLoaded", () => {

    var cap_flag = $("#cap_flag");

    if (!cap_flag.prop("checked")) {
        cap_container_refresh();
    }

    cap_flag.on("change", function () {
        cap_container_refresh();
    });
});

function cap_container_refresh() {

    var cap_flag = $("#cap_flag");
    var div_cap = $("#div_cap");
    var material_field = $("#id_material");

    //alert(cap_flag.prop("disabled"));

    if (cap_flag.prop("checked")) {
        material_field.prop("disabled", false);
        material_field.prop("required", true);
        div_cap.show();
    } else {
        material_field.prop("disabled", true);
        material_field.prop("required", false);
        div_cap.prop("disabled", true);
        div_cap.hide();
    }
}
