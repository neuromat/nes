// /**
//  * Created by diogopedrosa on 3/18/15.
//  */
//
// $(document).ready(function () {
//
//     var smoke_option = document.querySelector('input[name = "smoker"]:checked');
//
//     if (smoke_option != null) {
//         if (smoke_option.value == "True") {
//             $("#id_amount_cigarettes").prop('disabled', false);
//         } else {
//             $("#id_amount_cigarettes").prop('disabled', true);
//         }
//     }
//
//     var alcoholic_option = document.querySelector('input[name = "alcoholic"]:checked');
//
//     if (alcoholic_option != null) {
//         if (alcoholic_option.value == "True") {
//             $("#id_alcohol_frequency").prop('disabled', false);
//             $("#id_alcohol_period").prop('disabled', false);
//         } else {
//             $("#id_alcohol_frequency").prop('disabled', true);
//             $("#id_alcohol_period").prop('disabled', true);
//         }
//     }
//
//     $("#id_smoker_0").click(function () {
//         $("#id_amount_cigarettes").prop('disabled', false);
//     });
//
//     $("#id_smoker_1").click(function () {
//         var amount_cigarettes = $("#id_amount_cigarettes");
//         amount_cigarettes.value = "";
//         amount_cigarettes.prop('disabled', true);
//     });
//
//     $("#id_alcoholic_0").click(function () {
//         $("#id_alcohol_frequency").prop('disabled', false);
//         $("#id_alcohol_period").prop('disabled', false);
//     });
//
//     $("#id_alcoholic_1").click(function () {
//         var alcohol_frequency = $("#id_alcohol_frequency");
//         alcohol_frequency.value = "";
//         alcohol_frequency.prop('disabled', true);
//
//         var alcohol_period = $("#id_alcohol_period");
//         alcohol_period.value = "";
//         alcohol_period.prop('disabled', true);
//     });
// });