$(document).ready(function(){
    $("#birthday").mask("99/99/9999");

});

$(document).ready(function(){
    $("#verCerFractOptionsRadios1").click(function(){
        $("#id_fieldSetClavFract").prop('disabled', false);
    });
});

//exame complementar

$(document).ready(function(){
    $("#complementaryExameOptionsRadios1").click(function(){
        $("#id_whichComplementaryExame").prop('disabled', false);
    });
});

$(document).ready(function(){
    $("#complementaryExameOptionsRadios2").click(function(){
        $("#id_whichComplementaryExame").prop('disabled', true);
    });
});

//cirurgia de nervo

$(document).ready(function(){
    $("#nerveSurgOptionsRadios1").click(function(){
        $("#id_nerveSurgery").prop('disabled', false);
    });
});

$(document).ready(function(){
    $("#nerveSurgOptionsRadios2").click(function(){
        $("#id_nerveSurgery").prop('disabled', true);
    });
});

//vertebral lombo sacral

$(document).ready(function(){
    $("#verLomSacOptionsRadios1").click(function(){
        $("#id_fieldVerLomSac").prop('disabled', false);
    });
});

$(document).ready(function(){
    $("#verLomSacOptionsRadios2").click(function(){
        $("#id_fieldVerLomSac").prop('disabled', true);
    });
});

//vertebral lombo sacral relacionada

$(document).ready(function(){
    $("#verLomSacRelatedOptionsRadios1").click(function(){
        $("#id_fieldVerLomSacRelated").prop('disabled', false);
    });
});

$(document).ready(function(){
    $("#verLomSacRelatedOptionsRadios2").click(function(){
        $("#id_fieldVerLomSacRelated").prop('disabled', true);
    });
});

//historia da fratura
$(document).ready(function(){
    $("#fractHistOptionsRadios1").click(function(){
        $("#id_fieldFractHistory").prop('disabled', false);
    });
});

$(document).ready(function(){
    $("#fractHistOptionsRadios2").click(function(){
        $("#id_fieldFractHistory").prop('disabled', true);
    });
});

//historia da fratura relacionada
$(document).ready(function(){
    $("#relatedFractOptionsRadios1").click(function(){
        $("#id_fieldRelatedFractHistory").prop('disabled', false);
    });
});

$(document).ready(function(){
    $("#relatedFractOptionsRadios2").click(function(){
        $("#id_fieldRelatedFractHistory").prop('disabled', true);
    });
});

//historia cirurgia ortopedica

$(document).ready(function(){
    $("#orthSurgOptionsRadios1").click(function(){
        $("#id_fieldSetOrtSurg").prop('disabled', false);
    });
});

$(document).ready(function(){
    $("#orthSurgOptionsRadios2").click(function(){
        $("#id_fieldSetOrtSurg").prop('disabled', true);
    });
});

$(document).ready(function(){
    $("#verCerFractOptionsRadios2").click(function(){
        $("#id_fieldSetClavFract").prop('disabled', true);
    });
});


//fratura vertebral toracica relacionada
$(document).ready(function(){
    $("#verTorFractRelatedOptionsRadios1").click(function(){
        $("#id_fieldSetVerTorFractRelated").prop('disabled', false);
    });
});

$(document).ready(function(){
    $("#verTorFractRelatedOptionsRadios2").click(function(){
        $("#id_fieldSetVerTorFractRelated").prop('disabled', true);
    });
});


//fratura vertebral toracica
$(document).ready(function(){
    $("#verTorFractOptionsRadios1").click(function(){
        $("#id_fieldSetVerTorFract").prop('disabled', false);
    });
});

$(document).ready(function(){
    $("#verTorFractOptionsRadios2").click(function(){
        $("#id_fieldSetVerTorFract").prop('disabled', true);
    });
});

//lesoes vasculares
$(document).ready(function(){
    $("#vascularLesionsOptionsRadios1").click(function(){
        $("#id_fieldSetvascularLesions").prop('disabled', false);
    });
});

$(document).ready(function(){
    $("#vascularLesionsOptionsRadios2").click(function(){
        $("#id_fieldSetvascularLesions").prop('disabled', true);
    });
});

//fratura vertebral cervical relacionada
$(document).ready(function(){
    $("#verCerFractRelatedOptionsRadios1").click(function(){
        $("#id_fieldSetClavFractRelated").prop('disabled', false);
    });
});

$(document).ready(function(){
    $("#verCerFractRelatedOptionsRadios2").click(function(){
        $("#id_fieldSetClavFractRelated").prop('disabled', true);
    });

});

//fumante
$(document).ready(function(){
    $("#id_smoker_0").click(function(){
        $("#id_amount_cigarettes").prop('disabled', false);
    });
});

$(document).ready(function(){
    $("#id_smoker_1").click(function(){
        $("#id_amount_cigarettes").prop('disabled', true);
    });
});

//alcolismo
$(document).ready(function(){
    $("#id_alcoholic_0").click(function(){
        $("#id_freqSmok").prop('disabled', false);
        $("#id_periodSmok").prop('disabled', false);
    });
});

$(document).ready(function(){
    $("#id_alcoholic_1").click(function(){
        $("#id_freqSmok").prop('disabled', true);
        $("#id_periodSmok").prop('disabled', true);
    });
});

$(document).ready(function(){
    $("#cpf_id").mask("999.999.999-99");
});

$(document).ready(function(){
    $("#zipcode").mask("99999-999");
});

$(document).ready(function () {
    $("#phone").mask("(99) 9999-9999");
});

$(document).ready(function(){
    $("#id_chosen_state").on("change.bfhselectbox",function(){
        var state = $(this).val();
        if(state == "SP")
            $("#cellphone").mask("(99) 99999-9999");
        else
            $("#cellphone").mask("(99) 9999-9999");
    });
});

$(document).ready(function(){
    $("#nexttab").click(function(){
        var $tabs = $('.tabbable li');
        $tabs.filter('.active').next('li').find('a[data-toggle="tab"]').tab('show');
    });
});

$(document).ready(function(){
    $("#prevtab").click(function(){
        var $tabs = $('.tabbable li');
        $tabs.filter('.active').prev('li').find('a[data-toggle="tab"]').tab('show');
    });
});

$(document).ready(function(){
    $("#savetab2").click(function(){
        $("#form_id").submit();
    });
});

$(document).ready(function(){
    $("#savetab").click(function() {
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
                $("#form_id").submit();
            }
        }
    });
});


