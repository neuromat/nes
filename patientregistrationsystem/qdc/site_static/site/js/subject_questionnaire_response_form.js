/**
 * Created by evandro on 22/11/16.
 */

"use strict";
document.addEventListener("DOMContentLoaded", () => {

    var show_unanswered_checkbox = $("#id_show_unanswered_checkbox");

    // hide all questions with no-response
    // $( ".no-response" ).css( "border", "3px solid red" )
    $(".no-response").hide();

    show_unanswered_checkbox.on("click", function () {
        if (show_unanswered_checkbox.is(":checked")) {
            $(".no-response").show();
        } else {
            $(".no-response").hide();
        }
    });

});
