$(function(){
    //Search for patient in search mode
    $('#nameKey').keyup(function() {

        $.ajax({
            type: "POST",
            url: "/quiz/patient/search/",
            data: {
                'search_text' : $('#nameKey').val(),
                'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
            },
            success: searchSuccess,
            dataType: 'html'
        });

    });

    //Search for homonym patient
    $('#full_name').keyup(function() {

        $.ajax({
            type: "POST",
            url: "/quiz/patient/verify_homonym/",
            data: {
                'search_text': $('#full_name').val(),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            },
            success:searchSuccess,
            dataType: 'html'
        });

    });

    //Serch for same cpf
    $('#cpf_id').keyup(function() {

        $.ajax({
            type: "POST",
            url: "/quiz/patient/verify_homonym/",
            data: {
                'search_text': $('#cpf_id').val(),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            },
            success:searchSuccess,
            dataType: 'html'
        });

    });

    //Search in CID-10 table
    $('#id_whichComplementaryExam').keyup(function() {

            $.ajax({
                type: "POST",
                url: "/quiz/patient/medical_record/cid-10/",
                data: {
                    'search_text': ($('#id_whichComplementaryExam').val().length >= 3 ?
                        $('#id_whichComplementaryExam').val() : ''),
                    'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),
                    'patient_id': $('#patient_id').val(),
                    'medical_record': $('#medical_record_id').val()
                },
                success: searchSuccess,
                dataType: 'html'

            });
    });

    //Search for patient in search mode
    $('#subject_name').keyup(function() {

        $.ajax({
            type: "POST",
            url: "/experiment/subject/search/",
            data: {
                'search_text' : $('#subject_name').val(),
                'experiment_id': $('#experiment_id').val(),
                'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
            },
            success: searchSuccess,
            dataType: 'html'
        });

    });

});


function searchSuccess(data, textStatus, jqXHR) {
    $('#search-results-subjects').html(data);
    $('#search-results').html(data);
    $('#search-results1').html(data); //workaround to handle modal for patient excluded
                                      //see id="search-results1" in register.html
}
