$(document).ready(function () {

    $("#date_fill").mask("99/99/9999");

    $("#id_date_birth").mask("99/99/9999");

    $("#exam_date").mask("99/99/9999");

    $("#date").mask("99/99/9999");

    $("#id_smoker_0").click(function () {
        $("#id_amount_cigarettes").prop('disabled', false);
    });

    $("#id_smoker_1").click(function () {
        var x = document.getElementById("id_amount_cigarettes");
        x.value = "";
        $("#id_amount_cigarettes").prop('disabled', true);
    });

    $("#id_alcoholic_0").click(function () {
        $("#id_freqAlcoholic").prop('disabled', false);
        $("#id_periodAlcoholic").prop('disabled', false);
    });

    $("#id_alcoholic_1").click(function () {
        var x = document.getElementById("id_freqAlcoholic");
        var y = document.getElementById("id_periodAlcoholic");
        x.value = "";
        y.value = "";
        $("#id_freqAlcoholic").prop('disabled', true);
        $("#id_periodAlcoholic").prop('disabled', true);
    });

    $("#id_cpf").mask("999.999.999-99");

    $("#nexttab").click(function () {
        var $tabs = $('.tabbable li');
        $tabs.filter('.active').next('li').find('a[data-toggle="tab"]').tab('show');
    });


    $('#id_cellphone').val();
    $('#id_cellphone').change(function () {
        $('#id_cellphone').unmask();
    });

    $('#id_cellphone').focus(function () {
        $('#id_cellphone').unmask();
    });

    $('#id_cellphone').blur(function () {
        if ($("#id_cellphone").val().length == 11)
            $("#id_cellphone").mask("(99) 99999-9999");
        else if ($("#id_cellphone").val().length == 10)
            $("#id_cellphone").mask("(99) 9999-9999");
        else
            $("#id_cellphone").unmask();
    });

    $('#id_phone').val();
    $('#id_phone').change(function () {
        $('#id_phone').unmask();
    });

    $('#id_phone').focus(function () {
        $('#id_phone').unmask();
    });

    $('#id_phone').blur(function () {
        if ($("#id_phone").val().length == 11)
            $("#id_phone").mask("(99) 99999-9999");
        else if ($("#id_phone").val().length == 10)
            $("#id_phone").mask("(99) 9999-9999");
        else
            $("#id_phone").unmask();
    });

    $('#id_zipcode').val();
    $('#id_zipcode').change(function () {
        $('#id_zipcode').unmask();
    });

    $('#id_zipcode').focus(function () {
        $('#id_zipcode').unmask();
    });

    $('#id_zipcode').blur(function () {
        if (this.value.length == 8) {
            $('#id_zipcode').mask('99999-999');
        }
    });

    //Ajax part to show modal if patient with same name exists in database
    $('#id_name').blur(function () {
        var myElem = document.getElementById('patient_homonym');
        if (myElem != null) $('#modalHomonym').modal('show');

        var myElemExcluded = document.getElementById('patient_homonym_excluded');
        if (myElemExcluded != null) $('#modalHomonymExcluded').modal('show');
    });

    //Ajax part to show modal if patient with same cpf exists in database
    $('#id_cpf').blur(function () {
        var myElem = document.getElementById('patient_homonym');
        if (myElem != null) $('#modalHomonym').modal('show');

        var myElemExcluded = document.getElementById('patient_homonym_excluded');
        if (myElemExcluded != null) $('#modalHomonymExcluded').modal('show');
    });

    $("#prevtab").click(function () {
        var $tabs = $('.tabbable li');
        $tabs.filter('.active').prev('li').find('a[data-toggle="tab"]').tab('show');
    });

    $("#savetab2").click(function () {
        $("#form_id").submit();
    });

    $("#editPatient").click(function () {
        $("#name").unbind("blur");
        document.getElementById('action').value = "edit";
        $("#form_id").submit();
    });

    $("#removePatient").click(function () {
        document.getElementById('action').value = "remove";
        $("#form_id").submit();
    });

    $("#savetab").click(function () {
        //disable blur if patient has homonym
        $("#id_name").unbind("blur");

        var name_value = $.trim($("#id_name").val());
        var date_birth_value = $.trim($("#id_date_birth").val());
        var gender_value = $.trim($("#id_gender").val());
        var cpf_value = $.trim($("#id_cpf").val());

        if (name_value.length == 0 || date_birth_value.length == 0 || gender_value.length == 0) {
            showErrorMessageTemporary("Campos obrigatórios devem ser preenchidos.");
            jumpToElement('name');
            document.getElementById('date_birth').focus();
            document.getElementById('gender').focus();
            document.getElementById('name').focus();
            $("#idTabs li:eq( 0 ) a").tab('show');

        } else {

            var email_value = $.trim($('#id_email').val());

            if (email_value.length != 0 && !validateEmail(email_value)) {
                showErrorMessageTemporary("Preencha os campos corretamente. Campo de e-mail inválido");
            } else {

                if (cpf_value.length == 0) {
                    $("#myModal").modal('show');
                }
                else {
                    $("#form_id").submit();
                }
            }
        }
    });

    $("#save_exam").click(function () {

        var date_value = $.trim($("#exam_date").val());
        var description_value = $.trim($("#exam_description").val());

        if (date_value.length == 0 || description_value.length == 0) {
            showErrorMessageTemporary("Campos obrigatórios devem ser preenchidos.");
            jumpToElement('exam_date');
            document.getElementById('exam_date').focus();
            document.getElementById('exam_description').focus();
        } else {
            $("#form_exam").submit();
        }
    });

    $("#save_exam2").click(function () {
        $("#form_exam").submit();
    });

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var activeTab = e.target.id;

        if (document.getElementById('currentTab') != undefined)
            document.getElementById('currentTab').value = activeTab;
    });

});

function popup(URL) {

    var width = 650;
    var height = 550;

    var left = (screen.width / 2) - (width / 2);
    var top = (screen.height / 2) - (height / 2);

    var opener = window.open(URL, 'janela', 'width=' + width + ', height=' + height + ', top=' + top + ', left=' + left + ', scrollbars=yes, status=no, toolbar=no, location=no, directories=no, menubar=no, resizable=no, fullscreen=no');

    return opener;


}

function validateEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}
