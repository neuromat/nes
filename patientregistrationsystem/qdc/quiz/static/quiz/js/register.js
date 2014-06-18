$(document).ready(function () {

    $("#birthday").mask("99/99/9999");

    $("#verCerFractOptionsRadios1").click(function () {
        $("#id_fieldSetClavFract").prop('disabled', false);
    });

    $("#complementaryExameOptionsRadios1").click(function () {
        $("#id_whichComplementaryExame").prop('disabled', false);
    });

    $("#complementaryExameOptionsRadios2").click(function () {
        $("#id_whichComplementaryExame").prop('disabled', true);
    });

    $("#nerveSurgOptionsRadios1").click(function () {
        $("#id_nerveSurgery").prop('disabled', false);
    });

    $("#nerveSurgOptionsRadios2").click(function () {
        $("#id_nerveSurgery").prop('disabled', true);
    });

    $("#verLomSacOptionsRadios1").click(function () {
        $("#id_fieldVerLomSac").prop('disabled', false);
    });

    $("#verLomSacRelatedOptionsRadios1").click(function () {
        $("#id_fieldVerLomSacRelated").prop('disabled', false);
    });

    $("#verLomSacRelatedOptionsRadios2").click(function () {
        $("#id_fieldVerLomSacRelated").prop('disabled', true);
    });

    $("#verLomSacOptionsRadios2").click(function () {
        $("#id_fieldVerLomSac").prop('disabled', true);
    });

    $("#fractHistOptionsRadios1").click(function () {
        $("#id_fieldFractHistory").prop('disabled', false);
    });

    $("#fractHistOptionsRadios2").click(function () {
        $("#id_fieldFractHistory").prop('disabled', true);
    });

    $("#relatedFractOptionsRadios1").click(function () {
        $("#id_fieldRelatedFractHistory").prop('disabled', false);
    });

    $("#relatedFractOptionsRadios2").click(function () {
        $("#id_fieldRelatedFractHistory").prop('disabled', true);
    });

    $("#orthSurgOptionsRadios1").click(function () {
        $("#id_fieldSetOrtSurg").prop('disabled', false);
    });

    $("#orthSurgOptionsRadios2").click(function () {
        $("#id_fieldSetOrtSurg").prop('disabled', true);
    });

    $("#verCerFractOptionsRadios2").click(function () {
        $("#id_fieldSetClavFract").prop('disabled', true);
    });

    $("#verTorFractRelatedOptionsRadios1").click(function () {
        $("#id_fieldSetVerTorFractRelated").prop('disabled', false);
    });

    $("#verTorFractRelatedOptionsRadios2").click(function () {
        $("#id_fieldSetVerTorFractRelated").prop('disabled', true);
    });

    $("#verTorFractOptionsRadios1").click(function () {
        $("#id_fieldSetVerTorFract").prop('disabled', false);
    });

    $("#verTorFractOptionsRadios2").click(function () {
        $("#id_fieldSetVerTorFract").prop('disabled', true);
    });

    $("#vascularLesionsOptionsRadios1").click(function () {
        $("#id_fieldSetvascularLesions").prop('disabled', false);
    });

    $("#vascularLesionsOptionsRadios2").click(function () {
        $("#id_fieldSetvascularLesions").prop('disabled', true);
    });

    $("#verCerFractRelatedOptionsRadios1").click(function () {
        $("#id_fieldSetClavFractRelated").prop('disabled', false);
    });

    $("#verCerFractRelatedOptionsRadios2").click(function () {
        $("#id_fieldSetClavFractRelated").prop('disabled', true);
    });

    $("#smokingOptionsRadios1").click(function () {
        $("#id_amount_cigarettes").prop('disabled', false);
    });

    $("#smokingOptionsRadios2").click(function () {
        $("#id_amount_cigarettes").prop('disabled', true);
    });

    $("#alcoholismOptionsRadios1").click(function () {
        $("#id_freqSmok").prop('disabled', false);
        $("#id_periodSmok").prop('disabled', false);
    });

    $("#alcoholismOptionsRadios2").click(function () {
        $("#id_freqSmok").prop('disabled', true);
        $("#id_periodSmok").prop('disabled', true);
    });


    $("#cpf_id").mask("999.999.999-99");

    $("#nexttab").click(function () {
        var $tabs = $('.tabbable li');
        $tabs.filter('.active').next('li').find('a[data-toggle="tab"]').tab('show');
    });


    $('#cellphone').val('');
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

    $('#phone').val('');
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

    $('#zipcode').val('');
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

    $("#prevtab").click(function () {
        var $tabs = $('.tabbable li');
        $tabs.filter('.active').prev('li').find('a[data-toggle="tab"]').tab('show');
    });

    $("#savetab2").click(function () {
        $("#form_id").submit();
    });

    $("#savetab").click(function () {

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
            if (cpf_value.length == 0) {
                $("#myModal").modal('show');
            }
            else {
                if (!validateEmail($('#email').val())) {
                    showErrorMessageTemporary("Preencha os campos corretamente. Campo de e-mail inválido");
                } else {
                    $("#form_id").submit();
                }
            }
        }
    });
});


function validateEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}
