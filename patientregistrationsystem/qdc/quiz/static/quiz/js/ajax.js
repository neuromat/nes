$(function(){
    //Search for patient in search mode
    $('#nameKey').keyup(function() {

        $.ajax({
            type: "POST",
            url: "/patient/search/",
            data: {
                'search_text' : $('#nameKey').val(),
                'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
            },
            success: searchSuccess,
            dataType: 'html'
        });

    });

    //Search for homonym patient
    $('#name').keyup(function() {

        $.ajax({
            type: "POST",
            url: "/patient/verify_homonym/",
            data: {
                'search_text': $('#name').val(),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            },
            success:searchSuccess,
            dataType: 'html'
        });

    });

    //Serch for same cpf
    $('#cpf').keyup(function() {

        $.ajax({
            type: "POST",
            url: "/patient/verify_homonym/",
            data: {
                'search_text': $('#cpf').val(),
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
            url: "/patient/medical_record/cid-10/",
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

    $('#get_diseases').keyup(function() {
        var get_diseases = $('#get_diseases');
        $.ajax({
            type: "POST",
            url: "/experiment/group_diseases/cid-10/",
            data: {
                'search_text': (get_diseases.val().length >= 3 ? get_diseases.val() : ''),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),
                'group_id': $('#group_id').val()
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
                'group_id': $('#group_id').val(),
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
