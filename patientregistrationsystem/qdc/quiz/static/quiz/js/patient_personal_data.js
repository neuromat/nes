/**
 * Created by diogopedrosa on 3/18/15.
 */

$(document).ready(function () {
    var original_name = $('#id_name').val();
    var original_cpf = $('#id_cpf').val();

    // Ajax to search for homonym patient by name
    $('#id_name').blur(function() {
        var new_name = $('#id_name').val();

        if (new_name != original_name) {
            $.ajax({
                type: "POST",
                url: "/patient/verify_homonym/",
                data: {
                    'search_text': new_name,
                    'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
                },
                success: searchSuccessHomonym,
                dataType: 'html'
            });

            $.ajax({
                type: "POST",
                url: "/patient/verify_homonym_excluded/",
                data: {
                    'search_text': new_name,
                    'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
                },
                success: searchSuccessHomonymExcluded,
                dataType: 'html'
            });
        }
    });

    // Ajax to search for homonym patient by CPF
    $('#id_cpf').blur(function() {
        var new_cpf = $('#id_cpf').val();

        if (new_cpf != original_cpf) {
            $.ajax({
                type: "POST",
                url: "/patient/verify_homonym/",
                data: {
                    'search_text': new_cpf,
                    'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
                },
                success: searchSuccessHomonym,
                dataType: 'html'
            });

            $.ajax({
                type: "POST",
                url: "/patient/verify_homonym_excluded/",
                data: {
                    'search_text': new_cpf,
                    'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
                },
                success: searchSuccessHomonymExcluded,
                dataType: 'html'
            });
        }
    });

    function searchSuccessHomonym(data, textStatus, jqXHR) {
        $('#search-results-homonym').html(data);

        var myElem = document.getElementById('patient_homonym');

        if (myElem != null) {
            $('#modalHomonym').modal('show');
        }
    }

    function searchSuccessHomonymExcluded(data, textStatus, jqXHR) {
        $('#search-results-homonym-excluded').html(data);

        var myElemExcluded = document.getElementById('patient_homonym_excluded');

        if (myElemExcluded != null) {
            $('#modalHomonymExcluded').modal('show');
        }
    }

    $("#modalHomonymCancel").click(function () {
        var myElem = document.getElementById('patient_homonym');

        if (myElem != null) {
            myElem.parentNode.removeChild(myElem);
        }
    });

    $("#modalHomonymExcludedCancel").click(function () {
        var myElemExcluded = document.getElementById('patient_homonym_excluded');

        if (myElemExcluded != null) {
            myElemExcluded.parentNode.removeChild(myElemExcluded);
        }
    });

    // TODO Use plugin correctly
    $("#id_date_birth").mask("99/99/9999");
    var ua = navigator.userAgent.toLowerCase();
    var isNotAndroid = ua.indexOf("android") <= -1; //&& ua.indexOf("mobile");
    if(isNotAndroid) {

        $("#id_date_birth").mask("99/99/9999");

        $("#id_date").mask("99/99/9999");

        $("#id_cpf").mask("999.999.999-99");

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
    }

    $("#savetab").click(function () {
        var name_value = $.trim($("#id_name").val());
        var date_birth_value = $.trim($("#id_date_birth").val());
        var gender_value = $.trim($("#id_gender").val());
        var cpf_value = $.trim($("#id_cpf").val());

        if (name_value.length == 0 || date_birth_value.length == 0 || gender_value.length == 0) {
            showErrorMessageTemporary("Campos obrigatórios devem ser preenchidos.");
            jumpToElement('id_name');
            document.getElementById('id_date_birth').focus();
            document.getElementById('id_gender').focus();
            document.getElementById('id_name').focus();
        } else {
            var email_value = $.trim($('#id_email').val());

            if (email_value.length != 0 && !validateEmail(email_value)) {
                showErrorMessageTemporary("Preencha os campos corretamente. Campo de e-mail inválido");
            } else {
                if (cpf_value.length == 0) {
                    $("#myModal").modal('show');
                } else {
                    $("#form_id").submit();
                }
            }
        }
    });

    $("#noCPF_modal").click(function () {
        $("#form_id").submit();
    });

    $("#more_phones").click(function () {
        document.getElementById('action').value = "more_phones";
        $("#form_id").submit();
    });
});

function validateEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}
