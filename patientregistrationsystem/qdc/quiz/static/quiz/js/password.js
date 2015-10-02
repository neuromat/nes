/**
 * Created by diogopedrosa on 3/10/15.
 */

var beginCheckPassword1 = false;

function checkPass(){
    var password1 = $('#id_new_password1').val();
    var password2 = $('#id_new_password2').val();
    var confirmation = $('#id_new_password2_form_group');
    if(password1 && (password1 == password2)){
        confirmation.attr('class', 'has-success');
        $('#id_new_password1_form_group').removeClass('has-error');
        $("#message").text("");
        return false;
    }else{
        confirmation.attr('class', 'has-error');
        $("#message").text(gettext("Senhas não combinam"));
        return true;
    }
}

$(function(){
    $("[data-toggle=tooltip]").tooltip();
    $( "form" ).submit(function( event ) {
        if(checkPass())
            event.preventDefault();
        if(passwordForce() < 20 && $('#id_new_password1').val()){
            showErrorMessageTemporary(gettext("Senha deve conter pelo menos 8 caracteres, incluindo ao menos uma letra maiúscula, dígito ou caractere especial."));
            event.preventDefault();
        }
    })
});

function passwordForce(){
    var password = document.getElementById("id_new_password1").value;
    var force = 0;
    if(password){
        if((password.length >= 8)) {
            if (password.length > 12) {
                force += 5;
            }
            if (password.match(/[a-z]+/)) {
                force += 10;
            }
            if (password.match(/[A-Z]+/)) {
                force += 20;
            }
            if (password.match(/[0-9]+/)) {
                force += 20;
            }
            if (password.match(/[ !"@#$%&'()*+,-.\/:;<=>?@[\\\]_{|}~]+/)) {
                force += 25;
            }
        }
        showForce(force);
    }
    return force;
}

function showForce(force){
    var show = $("#show");
    if(force < 20){
        show.text(gettext("Fraca"));
        show.removeClass(function() {
            return $(this).attr("class");
        });
        show.addClass("text-danger");
    }else if((force >= 20) && (force < 40)){
        show.text(gettext("Justa"));
        show.removeClass(function() {
            return $(this).attr("class");
        });
        show.addClass("text-warning");
    }else if((force >= 40) && (force < 65)){
        show.text(gettext("Forte"));
        show.removeClass(function() {
            return $(this).attr("class");
        });
        show.addClass("text-success");
    }else{
        show.text(gettext("Excelente"));
        show.removeClass(function() {
            return $(this).attr("class");
        });
        show.addClass("text-primary");
    }
}
