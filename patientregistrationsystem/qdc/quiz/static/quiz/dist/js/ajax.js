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

});

function searchSuccess(data, textStatus, jqXHR)
{
    $('#search-results').html(data);
    $('#search-results1').html(data); //workaround to handle modal for patient excluded
                                      //see id="search-results1" in register.html
}
