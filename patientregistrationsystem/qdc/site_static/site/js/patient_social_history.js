/**
 * Created by diogopedrosa on 3/18/15.
 */

"use strict";
document.addEventListener("DOMContentLoaded", () => {
    var amount_cigarettes = $("#id_amount_cigarettes");
    var alcohol_frequency = $("#id_alcohol_frequency");
    var alcohol_period = $("#id_alcohol_period");
    var savebutton = $("#save_submit_button").val();

    amount_cigarettes.prop('disabled', true)
    alcohol_frequency.prop('disabled', true);
    alcohol_period.prop('disabled', true);

    $("#id_smoker_0").on("click", function () {
        amount_cigarettes.prop('disabled', false);
        $("input[name=ex_smoker]").attr('disabled', true);
    });

    $("#id_smoker_1").on("click", function () {
        amount_cigarettes.value = "";
        amount_cigarettes.prop('disabled', true);
        $("input[name=ex_smoker]").attr('disabled', false);
    });

    $("#id_alcoholic_0").on("click", function () {
        alcohol_frequency.prop('disabled', false);
        alcohol_period.prop('disabled', false);
    });

    $("#id_alcoholic_1").on("click", function () {
        alcohol_frequency.value = "";
        alcohol_frequency.prop('disabled', true);

        alcohol_period.value = "";
        alcohol_period.prop('disabled', true);
    });

    if ($("#id_smoker_1").is(":checked")) {
        amount_cigarettes.prop('disabled', true);
    }

    if ($("#id_alcoholic_1").is(":checked")) {
        alcohol_frequency.prop('disabled', true);
        alcohol_period.prop('disabled', true);
    }

    if (savebutton != null) {
        if ($("#id_smoker_0").is(":checked")) {
            amount_cigarettes.prop('disabled', false);
        }

        if ($("#id_alcoholic_0").is(":checked")) {
            alcohol_frequency.prop('disabled', false);
            alcohol_period.prop('disabled', false);
        }
    }
});