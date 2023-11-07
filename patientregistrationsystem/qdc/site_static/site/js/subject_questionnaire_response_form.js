/**
 * Created by evandro on 22/11/16.
 */

"use strict";

document.addEventListener("DOMContentLoaded", () => {
    let show_unanswered_checkbox = document.getElementById("id_show_unanswered_checkbox");
    let no_response_elements = document.getElementsByClassName("no-response");

    // hide all questions with no-response
    change_display(no_response_elements, 'none');

    if (show_unanswered_checkbox) {
        show_unanswered_checkbox.addEventListener("click", (e) => {
            if (show_unanswered_checkbox.checked) {
                change_display(no_response_elements, '');
            } else {
                change_display(no_response_elements, 'none');
            }
        });
    }
});

function change_display(list, str) {
    for (let element of list) {
        element.style.display = str;
    }
}