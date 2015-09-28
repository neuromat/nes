$(document).ready(function(){
    $(document).on("change", ".zip-field", function() {
        var arr;
        // validates CEP
        var regex = /^([0-9]{5})[-. ]?([0-9]{3})$/;
        if (regex.test($(".zip-field").val()))
        {
            $.get('/cep/'+$(".zip-field").val()+'/', function(data,status)
            {
                eval("var arr = "+data);
                $("#"+address.street).val(arr.street);
                $("#"+address.district).val(arr.district);
                $("#"+address.city).val(arr.city);
                $("#"+address.state).val(arr.state);
            });
        }
    });
});
