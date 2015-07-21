/**
 * Created by diogopedrosa on 3/18/15.
 */

// The inclusion of disabled class in a submit button can't be done in the template, because Bootstrap overwrite it.
$(document).ready(function () {
    setTimeout(function() { $("#save_submit_button").addClass("disabled"); }, 50);
});