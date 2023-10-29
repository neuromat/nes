/**
 * Created by diogopedrosa on 3/19/15.
 */

function show_modal_remove (patient_id, diagnosis_id){
    var  modal_remove = document.getElementById('removeDiagnosis');
    modal_remove.setAttribute( "href", '/patient/diagnosis/delete/' + patient_id + '/' + diagnosis_id);
    $('#modalRemove').modal('show');
}
function show_modal_detail(diagnosis_id){
    $("#diagnosis_date-" + diagnosis_id).mask("99/99/9999");
    $('#modalDetail' + diagnosis_id).modal('show');
}

$(document).ready(function () {
    //Search in CID-10 table
    $('#id_whichComplementaryExam').keyup(function() {

        $.ajax({
            type: "POST",
            url: "/patient/medical_record/cid-10/",
            data: {
                'search_text': ($('#id_whichComplementaryExam').val().length >= 3 ?
                    $('#id_whichComplementaryExam').val() : ''),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),
                'patient_id': $('#patient_id').val(),
                'medical_record': $('#medical_record_id').val()
            },
            success: searchSuccessDiseases,
            dataType: 'html'

        });
    });

    function searchSuccessDiseases(data, textStatus, jqXHR) {
        $('#search-results-diseases').html(data);
    }
});
