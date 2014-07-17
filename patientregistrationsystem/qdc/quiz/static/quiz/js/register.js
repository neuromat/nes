$(document).ready(function () {

    $("#birthday").mask("99/99/9999");

    $("#exam_date").mask("99/99/9999");

    $("#nerve_surgery_1").click(function () {
        $("#id_nerve_surgery_type").prop('disabled', true);
    });

    $("#fracture_history_1").click(function () {
        $("#scapula_fracture_side").prop('disabled', true);
        $("#clavicle_fracture_side").prop('disabled', true);
        $("#rib_fracture_0").prop('disabled', true);
        $("#rib_fracture_1").prop('disabled', true);
        $("#cervical_vertebrae_fracture_0").prop('disabled', true);
        $("#cervical_vertebrae_fracture_1").prop('disabled', true);
        $("#cervical_vertebrae_fracture_2").prop('disabled', true);
        $("#cervical_vertebrae_fracture_3").prop('disabled', true);
        $("#cervical_vertebrae_fracture_4").prop('disabled', true);
        $("#cervical_vertebrae_fracture_5").prop('disabled', true);
        $("#cervical_vertebrae_fracture_6").prop('disabled', true);
        $("#thoracic_vertebrae_fracture_0").prop('disabled', true);
        $("#thoracic_vertebrae_fracture_1").prop('disabled', true);
        $("#thoracic_vertebrae_fracture_2").prop('disabled', true);
        $("#thoracic_vertebrae_fracture_3").prop('disabled', true);
        $("#thoracic_vertebrae_fracture_4").prop('disabled', true);
        $("#thoracic_vertebrae_fracture_5").prop('disabled', true);
        $("#thoracic_vertebrae_fracture_6").prop('disabled', true);
        $("#thoracic_vertebrae_fracture_7").prop('disabled', true);
        $("#thoracic_vertebrae_fracture_8").prop('disabled', true);
        $("#thoracic_vertebrae_fracture_9").prop('disabled', true);
        $("#thoracic_vertebrae_fracture_10").prop('disabled', true);
        $("#thoracic_vertebrae_fracture_11").prop('disabled', true);
        $("#lumbosacral_vertebrae_fracture_0").prop('disabled', true);
        $("#lumbosacral_vertebrae_fracture_1").prop('disabled', true);
        $("#lumbosacral_vertebrae_fracture_2").prop('disabled', true);
        $("#lumbosacral_vertebrae_fracture_3").prop('disabled', true);
        $("#lumbosacral_vertebrae_fracture_4").prop('disabled', true);
        $("#lumbosacral_vertebrae_fracture_5").prop('disabled', true);
        $("#lumbosacral_vertebrae_fracture_6").prop('disabled', true);
        $("#lumbosacral_vertebrae_fracture_7").prop('disabled', true);
        $("#superior_members_fracture_side").prop('disabled', true);
        $("#inferior_members_fracture_side").prop('disabled', true);
        $("#pelvis_fracture_side").prop('disabled', true);
    });

    $("#orthopedic_surgery_1").click(function () {
        $("#scapula_surgery_side").prop('disabled', true);
        $("#clavicle_surgery_side").prop('disabled', true);
        $("#rib_surgery_0").prop('disabled', true);
        $("#rib_surgery_1").prop('disabled', true);
        $("#cervical_vertebrae_surgery_0").prop('disabled', true);
        $("#cervical_vertebrae_surgery_1").prop('disabled', true);
        $("#thoracic_vertebrae_surgery_0").prop('disabled', true);
        $("#thoracic_vertebrae_surgery_1").prop('disabled', true);
        $("#lumbosacral_vertebrae_surgery_0").prop('disabled', true);
        $("#lumbosacral_vertebrae_surgery_1").prop('disabled', true);
        $("#superior_members_surgery_side").prop('disabled', true);
        $("#inferior_members_surgery_side").prop('disabled', true);
        $("#pelvis_surgery_side").prop('disabled', true);
    });

    $("#id_smoker_0").click(function () {
        $("#id_amount_cigarettes").prop('disabled', false);
    });

    $("#id_smoker_1").click(function () {
        $("#id_amount_cigarettes").prop('disabled', true);
    });

    $("#id_alcoholic_0").click(function () {
        $("#id_freqSmok").prop('disabled', false);
        $("#id_periodSmok").prop('disabled', false);
    });

    $("#id_alcoholic_1").click(function () {
        $("#id_freqSmok").prop('disabled', true);
        $("#id_periodSmok").prop('disabled', true);
    });


    $("#cpf_id").mask("999.999.999-99");

    $("#nexttab").click(function () {
        var $tabs = $('.tabbable li');
        $tabs.filter('.active').next('li').find('a[data-toggle="tab"]').tab('show');
    });


    $('#cellphone').val();
    $('#cellphone').change(function () {
        $('#cellphone').unmask();
    });

    $('#cellphone').focus(function () {
        $('#cellphone').unmask();
    });

    $('#cellphone').blur(function () {
        if ($("#cellphone").val().length == 11)
            $("#cellphone").mask("(99) 99999-9999");
        else if ($("#cellphone").val().length == 10)
            $("#cellphone").mask("(99) 9999-9999");
        else
            $("#cellphone").unmask();
    });

    $('#phone').val();
    $('#phone').change(function () {
        $('#phone').unmask();
    });

    $('#phone').focus(function () {
        $('#phone').unmask();
    });

    $('#phone').blur(function () {
        if ($("#phone").val().length == 11)
            $("#phone").mask("(99) 99999-9999");
        else if ($("#phone").val().length == 10)
            $("#phone").mask("(99) 9999-9999");
        else
            $("#phone").unmask();
    });

    $('#zipcode').val();
    $('#zipcode').change(function () {
        $('#zipcode').unmask();
    });

    $('#zipcode').focus(function () {
        $('#zipcode').unmask();
    });

    $('#zipcode').blur(function () {
        if (this.value.length == 8) {
            $('#zipcode').mask('99999-999');
        }
    });

    //Ajax part to show modal if patient with same name exists in database
    $('#full_name').blur(function() {
        var myElem = document.getElementById('patient_homonym');
        if (myElem != null) $('#modalHomonym').modal('show');

        var myElemExcluded = document.getElementById('patient_homonym_excluded');
        if (myElemExcluded != null) $('#modalHomonymExcluded').modal('show');
    });

    //Ajax part to show modal if patient with same cpf exists in database
    $('#cpf_id').blur(function() {
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
        //disable blur if patient has homonym
        $("#full_name").unbind("blur");
        document.getElementById('action').value = "edit";
        $("#form_id").submit();
    });

    $("#removePatient").click(function () {
        document.getElementById('action').value = "remove";
        $("#form_id").submit();
    });

//    $("#removeUser").click(function () {
//        document.getElementById('action').value = "remove";
//        $("#user_form").submit();
//    });

    $("#savetab").click(function () {
        //disable blur if patient has homonym
        $("#full_name").unbind("blur");

        var name_value = $.trim($("#full_name").val());
        var date_birth_value = $.trim($("#birthday").val());
        var gender_value = $.trim($("#gender_id").val());
        var cpf_value = $.trim($("#cpf_id").val());

        if (name_value.length == 0 || date_birth_value.length == 0 || gender_value.length == 0) {
            showErrorMessageTemporary("Campos obrigatórios devem ser preenchidos.");
            jumpToElement('full_name');
            document.getElementById('birthday').focus();
            document.getElementById('gender_id').focus();
            document.getElementById('full_name').focus();
        } else {

            var email_value = $.trim($('#email').val());

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

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var activeTab = e.target.id;

        if (document.getElementById('currentTab') != undefined)
            document.getElementById('currentTab').value = activeTab;
    });

});


function validateEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}
