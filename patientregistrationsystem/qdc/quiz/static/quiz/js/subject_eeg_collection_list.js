/**
 * Created by evandro on 8/25/16.
 */

$(function(){
    $("[data-toggle=tooltip]").tooltip();
});

var requisition_id = 0;

$(document).ready(function () {
    requisition_id = $("#process_requisition").val();
});

// function generate_requisition_id() {
//   function s4() {
//     return Math.floor((1 + Math.random()) * 0x10000)
//       .toString(16)
//       .substring(1);
//   }
//   return s4() +  '-' + s4();
// }

function handle_processing() {
    $('#pleaseWaitDialog').modal('show');
    check_requisition();
    setTimeout(check_requisition, 1000);
}

function check_requisition() {
    var url = "/experiment/eeg_data/get_process_requisition_status/" + requisition_id;
    $.getJSON(url, function (response) {
        document.getElementById('label_process_requisition_status').innerHTML = response['message'];
        if(response['status'] == "finished"){
            $('#pleaseWaitDialog').modal('hide');
        document.getElementById('label_process_requisition_status').innerHTML = "";
        } else {
            setTimeout(check_requisition, 1000);
        }
    });
}
