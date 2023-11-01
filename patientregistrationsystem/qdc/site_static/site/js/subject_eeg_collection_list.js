/**
 * Created by evandro on 8/25/16.
 */

"use strict";

var requisition_id = 0;

document.addEventListener("DOMContentLoaded", () => {
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

async function check_requisition() {
    const url = "/experiment/eeg_data/get_process_requisition_status/" + requisition_id;

    const response_fetch = await fetch(url);
    const response = await response_fetch.json();

    document.getElementById('label_process_requisition_status').innerHTML = response['message'];
    if (response['status'] == "finished") {
        $('#pleaseWaitDialog').modal('hide');
        document.getElementById('label_process_requisition_status').innerHTML = "";
    } else {
        setTimeout(check_requisition, 1000);
    }

    // $.getJSON(url, function (response) {
    //     document.getElementById('label_process_requisition_status').innerHTML = response['message'];
    //     if(response['status'] == "finished"){
    //         $('#pleaseWaitDialog').modal('hide');
    //     document.getElementById('label_process_requisition_status').innerHTML = "";
    //     } else {
    //         setTimeout(check_requisition, 1000);
    //     }
    // });
}
