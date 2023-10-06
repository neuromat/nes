/**
 * Created by mruizo on 07/04/17.
 */

function checkPassExt(){
            var password_flag = $("#password_flag");
            if (password_flag.prop("checked")) {
                return(checkPass());
            }
            return false;
        }


        $(document).ready(function () {

        var password_flag = $("#password_flag");

        if (!password_flag.prop("checked")) {
            password_container_refresh();
        }

        password_flag.change(function() {
            password_container_refresh();
        });
    });

        function password_container_refresh() {

            var password_flag = $("#password_flag");
            var div_password = $("#div_password");
            var password_field = $("#id_new_password1");
            var password2_field = $("#id_new_password2");


             //alert(password_flag.prop("disabled"));

            if (password_flag.prop("checked")) {
                password_field.prop( "disabled", false );
                password2_field.prop( "disabled", false );
                div_password.show();
            } else {
                password_field.val("");
                password2_field.val("");
                password_field.prop( "disabled", true );
                password2_field.prop( "disabled", true );
                // div_password.prop( "disabled", true );
                // div_password.hide();
            }
        }