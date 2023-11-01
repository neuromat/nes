"use strict";

document.addEventListener("DOMContentLoaded", () => {

    $(".invalidLink").on("click", function (e) {
        e.preventDefault();
        $('#modalInvalidLink').modal('show');
    });

    // The following 5 handlers prepare to show a confirmation modal by storing the future tab number.
    $("#linkToTab0").on("click", function (e) {
        document.getElementById('nextTab').value = '0';
        document.getElementById('nextTabURL').value = $(this).attr('href');
        tabClick(e);
    });

    $("#linkToTab1").on("click", function (e) {
        document.getElementById('nextTab').value = '1';
        document.getElementById('nextTabURL').value = $(this).attr('href');
        tabClick(e);
    });

    $("#linkToTab2").on("click", function (e) {
        document.getElementById('nextTab').value = '2';
        document.getElementById('nextTabURL').value = $(this).attr('href');
        tabClick(e);
    });

    $("#linkToTab3").on("click", function (e) {
        document.getElementById('nextTab').value = '3';
        document.getElementById('nextTabURL').value = $(this).attr('href');
        tabClick(e);
    });

    $("#linkToTab4").on("click", function (e) {
        document.getElementById('nextTab').value = '4';
        document.getElementById('nextTabURL').value = $(this).attr('href');
        tabClick(e);
    });

    // Handle the confirmation for saving data after clicking on a different tab.
    $("#savetab_modal_save").on("click", function () {
        document.getElementById('action').value = "change_tab";
        $("#form_id").trigger("submit");
    });

    // Handle the option for not saving data after clicking on a different tab.
    $("#savetab_modal_dont_save").on("click", function () {
        window.location = document.getElementById('nextTabURL').value;
    });

    $("#editPatient").on("click", function () {
        document.getElementById('action').value = "edit";
        $("#form_id").trigger("submit");
    });

    $("#removePatient").on("click", function () {
        document.getElementById('action').value = "remove";
        $("#form_id").trigger("submit");
    });

    $("#prevtab").on("click", function () {
        document.getElementById('action').value = "show_previous";
        $("#form_id").trigger("submit");
    });

    $("#nexttab").on("click", function () {
        document.getElementById('action').value = "show_next";
        $("#form_id").trigger("submit");
    });

    $("#save_exam").on("click", function () {
        var date_value = $("#exam_date").val().trim();
        var description_value = $("#exam_description").val().trim();

        if (date_value.length == 0 || description_value.length == 0) {
            showErrorMessageTemporary(gettext("Obligatory fields must be filled."));
            jumpToElement('exam_date');
            document.getElementById('exam_date').focus();
            document.getElementById('exam_description').focus();
        } else {
            $("#form_exam").trigger("submit");
        }
    });
});

function tabClick(e, url) {
    e.preventDefault();
    $('#modalSaveTab').modal('show');
}
