/**
 * Created by evandro on 4/11/16.
 */

$(document).ready(function () {

    var all_participants_radio = $("#id_type_of_selection_radio_0");
    var selected_participants_radio = $("#id_type_of_selection_radio_1");
    var participants_filter_div = $("#participants_filter_div");

    var gender_checkbox = $("#id_gender_checkbox");
    var gender_options = $("#id_gender");

    var marital_status_checkbox = $("#id_marital_status_checkbox");
    var marital_status_options = $("#id_marital_status");

    var age_checkbox = $("#id_age_checkbox");
    var min_age_field = $("#id_min_age");
    var max_age_field = $("#id_max_age");
    
    var location_checkbox = $("#id_location_checkbox");
    var diagnosis_checkbox = $("#id_diagnosis_checkbox");
    var all_countries_radio = $("#id_all_countries_radio");
    var brazil_radio = $("#id_brazil_radio");
    var choose_radio = $("#id_choose_radio");
    var get_location = $("#get_location");
    var get_diagnosis = $("#get_diagnosis");

    selected_participants_radio.click(function () {
        all_countries_radio.prop('disabled', true);
        brazil_radio.prop('disabled', true);
        choose_radio.prop('disabled', true);
        get_location.prop('disabled', true);
        get_diagnosis.prop('disabled', true);
        participants_filter_div.prop('disabled', false);
        participants_filter_div.css('visibility', 'visible');
        participants_filter_div.collapse('show')
    });

    all_participants_radio.click(function () {
        participants_filter_div.prop('disabled', true);

        if (gender_checkbox.is(":checked")) {gender_checkbox.click();}
        if (marital_status_checkbox.is(":checked")) {marital_status_checkbox.click();}
        if (age_checkbox.is(":checked")) {age_checkbox.click();}
        if (location_checkbox.is(":checked")) {location_checkbox.click();}

        participants_filter_div.css('visibility', 'hidden');
        participants_filter_div.collapse('hide');
    });

    gender_checkbox.click(function() {
        if (gender_checkbox.is(":checked")) {
            gender_options.prop('disabled', false);
        } else {
            gender_options.prop('disabled', true);
        }
    });

    marital_status_checkbox.click(function() {
        if (marital_status_checkbox.is(":checked")) {
            marital_status_options.prop('disabled', false);
        } else {
            marital_status_options.prop('disabled', true);
        }
    });

    age_checkbox.click(function() {
        if (age_checkbox.is(":checked")) {
            min_age_field.prop('disabled', false);
            max_age_field.prop('disabled', false);
        } else {
            min_age_field.prop('disabled', true);
            max_age_field.prop('disabled', true);
        }
    });

    location_checkbox.click(function () {
        if (location_checkbox.is(":checked")) {
            all_countries_radio.prop('disabled', false);
            all_countries_radio.prop('checked', true);
            brazil_radio.prop('disabled', false);
            choose_radio.prop('disabled', false);
        }else{
            all_countries_radio.prop('disabled', true);
            all_countries_radio.prop('checked', false);
            brazil_radio.prop('disabled', true);
            choose_radio.prop('disabled', true);
            all_countries_radio.prop('checked', false);
            brazil_radio.prop('checked', false);
            choose_radio.prop('checked', false);
        }
    })

    all_countries_radio.click(function () {
        brazil_radio.prop('checked', false);
        choose_radio.prop('checked', false);
        get_location.prop('disabled', true);
    })

    brazil_radio.click(function () {
        all_countries_radio.prop('checked', false);
        choose_radio.prop('checked', false);
        get_location.prop('disabled', true);
    })

    choose_radio.click(function () {
        all_countries_radio.prop('checked', false);
        brazil_radio.prop('checked', false);
        get_location.prop('disabled', false);
    })

    diagnosis_checkbox.click(function () {
        if (diagnosis_checkbox.is(":checked"))
            get_diagnosis.prop('disabled', false);
        else
            get_diagnosis.prop('disabled', true);
    })

    $('#get_location').keyup(function() {
        
        $.ajax({
            type: "POST",
            url: "/export/get_locations/",
            data: {
                'search_text': $('#get_location').val(),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: searchSuccessLocations,
            dataType: 'html'

        });
    });

    function searchSuccessLocations(data, textStatus, jqXHR) {
        $('#search-results-locations').html(data);
    }

    $('#get_diagnosis').keyup(function() {

        $.ajax({
            type: "POST",
            url: "/export/get_diagnoses/",
            data: {
                'search_text': $('#get_diagnosis').val(),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: searchSuccessDiagnoses,
            dataType: 'html'

        });
    });

    function searchSuccessDiagnoses(data, textStatus, jqXHR) {
        $('#search-results-diagnoses').html(data);
    }

});

//Cria os elementos html dinamicamente
function add_location(location) {
        //limpa a lista de resultados
        var ul_search_locations = document.getElementById('search-results-locations');
        var ul_location_list = document.getElementById('ul-location-list');
        ul_search_locations.removeChild(ul_location_list);

        //limpa o campo de entrada para a busca por cidade
        var input_location = document.getElementById("get_location");
        input_location.value = "";

        //checkbox
        var checknode = document.createElement('input');
        checknode.type = 'checkbox';
        checknode.name = 'selected_locals';
        checknode.value = location;
        checknode.setAttribute("checked", true);
        checknode.style.display = "none";
        //label
        var textnode=document.createTextNode(location);
        //botão
        var btn_node = document.createElement('BUTTON');
        btn_node.id = "btn" + location;
        btn_node.type = "button"
        btn_node.className = "btn btn-default unbuttonmize";
        btn_node.appendChild(checknode);
        btn_node.appendChild(textnode);
        // btn_node.onclick = null;

        //criar span element
        var spannode = document.createElement('span');
        spannode.className = "glyphicon glyphicon-remove";
        // spannode.data-toggle("tooltip");
        spannode.style.color = "indianred";
        spannode.style.verticalAlign = "-10%";
        spannode.title = "Remover";

        //criar a tag
        var tagnode = document.createElement('a');
        tagnode.id = location;
        tagnode.onclick = function (event) {
            alert("remove" + this.id);
            var localization_div = document.getElementById("localization_list");
            localization_div.removeChild("btn"+ this.id);
        }
        tagnode.appendChild(spannode);
        btn_node.appendChild(tagnode);

        //container
        var localization_div = document.getElementById("localization_list")
        localization_div.appendChild(btn_node);
}