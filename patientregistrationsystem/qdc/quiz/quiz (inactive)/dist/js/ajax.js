$(function(){

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

});

function searchSuccess(data, textStatus, jqXHR)
{
    $('#search-results').html(data);
}
