/**
 * Created by diogopedrosa on 3/17/15.
 */

// We can't use Masked Input Plugin (http://digitalbush.com/projects/masked-input-plugin/) because some numbers
// have 10 and others have 11 digits.
//jQuery(function($){
//   $("#id_number").mask("(99) 99999-9999");
//});

// A possible approach could be as described in http://php.eduardokraus.com/plugin-jquery-masked-input-para-celular,
// but it does not look good to me because other cities are also increasing the number of digits.

"use strict";
document.addEventListener("DOMContentLoaded", () => {
    $('.telephone_number').on("focus", function () {
        $(this).val($(this).val().replace(/\D/g,''));
    });

    $('.telephone_number').on("blur", function () {
        number = $(this).val().replace(/\D/g,'');

        // 011 98888 8888
        if (number.length == 12 && number.substring(0,1) == '0')
            $(this).val('(' + number.substring(1,3) + ') ' + number.substring(3,8) + '-' + number.substring(8,12));
        else if (number.length == 11)
            // 011 8888 8888
            if (number.substring(0,1) == '0')
                $(this).val('(' + number.substring(1,3) + ') ' + number.substring(3,7) + '-' + number.substring(7,11));
            // 11 98888 8888
            else
                $(this).val('(' + number.substring(0,2) + ') ' + number.substring(2,7) + '-' + number.substring(7,11));
        // 11 8888 8888
        else if (number.length == 10)
            $(this).val('(' + number.substring(0,2) + ') ' + number.substring(2,6) + '-' + number.substring(6,10));
    });
});