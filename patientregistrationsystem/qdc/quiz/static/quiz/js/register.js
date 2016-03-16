$(document).ready(function () {

    $(".invalidLink").click(function (e) {
        e.preventDefault();
        $('#modalInvalidLink').modal('show');
    });

    // The following 5 handlers prepare to show a confirmation modal by storing the future tab number.
    $("#linkToTab0").click(function (e) {
        document.getElementById('nextTab').value = '0';
        document.getElementById('nextTabURL').value = $(this).attr('href');
        tabClick(e);
    });

    $("#linkToTab1").click(function (e) {
        document.getElementById('nextTab').value = '1';
        document.getElementById('nextTabURL').value = $(this).attr('href');
        tabClick(e);
    });

    $("#linkToTab2").click(function (e) {
        document.getElementById('nextTab').value = '2';
        document.getElementById('nextTabURL').value = $(this).attr('href');
        tabClick(e);
    });

    $("#linkToTab3").click(function (e) {
        document.getElementById('nextTab').value = '3';
        document.getElementById('nextTabURL').value = $(this).attr('href');
        tabClick(e);
    });

    $("#linkToTab4").click(function (e) {
        document.getElementById('nextTab').value = '4';
        document.getElementById('nextTabURL').value = $(this).attr('href');
        tabClick(e);
    });

    // Handle the confirmation for saving data after clicking on a different tab.
    $("#savetab_modal_save").click(function () {
        document.getElementById('action').value = "change_tab";
        $("#form_id").submit();
    });

    // Handle the option for not saving data after clicking on a different tab.
    $("#savetab_modal_dont_save").click(function () {
        window.location = document.getElementById('nextTabURL').value;
    });

    $("#editPatient").click(function () {
        document.getElementById('action').value = "edit";
        $("#form_id").submit();
    });

    $("#removePatient").click(function () {
        document.getElementById('action').value = "remove";
        $("#form_id").submit();
    });

    $("#prevtab").click(function () {
        document.getElementById('action').value = "show_previous";
        $("#form_id").submit();
    });

    $("#nexttab").click(function () {
        document.getElementById('action').value = "show_next";
        $("#form_id").submit();
    });

    $("#save_exam").click(function () {
        var date_value = $.trim($("#exam_date").val());
        var description_value = $.trim($("#exam_description").val());

        if (date_value.length == 0 || description_value.length == 0) {
            showErrorMessageTemporary(gettext("Obligatory fields must be filled."));
            jumpToElement('exam_date');
            document.getElementById('exam_date').focus();
            document.getElementById('exam_description').focus();
        } else {
            $("#form_exam").submit();
        }
    });
});

function tabClick(e, url) {
    e.preventDefault();
    $('#modalSaveTab').modal('show');
}
