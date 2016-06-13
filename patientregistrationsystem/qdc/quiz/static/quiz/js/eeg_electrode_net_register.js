/**
 * Created by evandro on 6/13/16.
 */

$(function(){
    $("[data-toggle=tooltip]").tooltip();
});

$(document).ready(function () {

    var cap_flag = $("#cap_flag");

    cap_container_refresh();

    cap_flag.change(function() {
        cap_container_refresh();
    });
});

function cap_container_refresh() {

    var cap_flag = $("#cap_flag");
    var div_cap = $("#div_cap");

    // alert(cap_flag.prop("checked"));

    if (cap_flag.prop("checked")) {
        div_cap.prop( "disabled", false );
        div_cap.show();
    } else {
        div_cap.prop( "disabled", true );
        div_cap.hide();
    }
}
