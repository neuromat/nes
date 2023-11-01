/**
 * Created by evandro on 4/11/16.
 */

"use strict";
document.addEventListener("DOMContentLoaded", () => {

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
    var diseases_checkbox = $("#id_diseases_checkbox");
    var get_location = $("#get_location");
    var get_diagnosis = $("#get_diagnosis");
    var get_diseases = $("#get_diseases");

    selected_participants_radio.on("click", function () {
        // choose_radio.prop('disabled', true);
        get_location.prop('disabled', true);
        get_diagnosis.prop('disabled', true);
        get_diseases.prop('disabled', true);
        participants_filter_div.prop('disabled', false);
        participants_filter_div.css('visibility', 'visible');
        participants_filter_div.collapse('show')
        max_age_field.prop('required', false);
        min_age_field.prop('required', false);
        marital_status_options.prop('required', false);
        gender_options.prop('required', false);
        $('#get_diagnosis').prop('required', false);
        $('#get_location').prop('required', false);
    });

    all_participants_radio.on("click", function () {
        participants_filter_div.prop('disabled', true);

        if (gender_checkbox.is(":checked")) { gender_checkbox.on("click",); }
        if (marital_status_checkbox.is(":checked")) { marital_status_checkbox.on("click",); }
        if (age_checkbox.is(":checked")) { age_checkbox.on("click",); }
        if (location_checkbox.is(":checked")) { location_checkbox.on("click",); }

        participants_filter_div.css('visibility', 'hidden');
        participants_filter_div.collapse('hide');
    });

    gender_checkbox.on("click", function () {
        if (gender_checkbox.is(":checked")) {
            gender_options.prop('disabled', false);
            gender_options.prop('required', true);
        } else {
            gender_options.prop('required', false);
            gender_options.prop('disabled', true);
        }
    });

    marital_status_checkbox.on("click", function () {
        if (marital_status_checkbox.is(":checked")) {
            marital_status_options.prop('disabled', false);
            marital_status_options.prop('required', true);
        } else {
            marital_status_options.prop('disabled', true);
            marital_status_options.prop('required', false);
        }
    });

    age_checkbox.on("click", function () {
        if (age_checkbox.is(":checked")) {
            min_age_field.prop('disabled', false);
            min_age_field.prop('required', true);
            max_age_field.prop('disabled', false);
            max_age_field.prop('required', true);
        } else {
            min_age_field.prop('disabled', true);
            min_age_field.prop('required', false);
            max_age_field.prop('disabled', true);
            max_age_field.prop('required', false);
        }
    });

    location_checkbox.on("click", function () {
        if (location_checkbox.is(":checked")) {
            $('#get_location').prop('disabled', false);
            $('#get_location').prop('required', true);
        } else {
            $('#get_location').val("");
            $('#get_location').prop('disabled', true);
            $('#get_location').prop('required', false);
            var ul_location_list = $('#ul-location-list');
            ul_location_list.hide();
            var div_location_list = $('#localization_list');
            div_location_list.hide();
        }
    });

    diagnosis_checkbox.on("click", function () {
        if (diagnosis_checkbox.is(":checked")) {
            $('#get_diagnosis').prop('disabled', false);
            $('#get_diagnosis').prop('required', true);
        } else {
            $('#get_diagnosis').val("");
            $('#get_diagnosis').prop('disabled', true);
            $('#get_diagnosis').prop('required', false);
            var ul_diagnosis_list = $('#ul-diagnosis-list');
            ul_diagnosis_list.hide();
            var div_diagnosis_list = $('#diagnosis_list');
            div_diagnosis_list.hide();
        }

    });

    diseases_checkbox.on("click", function () {
        if (diseases_checkbox.is(":checked")) {
            $('#get_diseases').prop('disabled', false);
            $('#get_diseases').prop('required', true);
        } else {
            $('#get_diseases').val("");
            $('#get_diseases').prop('disabled', true);
            $('#get_diseases').prop('required', false);
            var ul_diagnosis_list = $('#ul-diagnosis-list');
            ul_diagnosis_list.hide();
            var div_diagnosis_list = $('#diagnosis_list');
            div_diagnosis_list.hide();
        }

    });

    const auto_location = new autoComplete({
        selector: "#get_location",
        data: {
            src: async (query) => {
                try {
                    // Fetch Data from external Source
                    const source = await fetch('/export/get_locations/?term='+query);
                    // Data should be an array of `Objects` or `Strings`
                    const data = await source.json();

                    return data;
                } catch (error) {
                    return error;
                }
            },
            keys: ["value"]
        },
        threshold: 2,
        debounce: 300,
        resultItem: {
            highlight: true
        },
        resultsList: {
            destination: "#search-results-locations",
            element: (list, data) => {
                //console.log(list)
                console.log(data)
                if (!data.results.length) {
                    // Create "No Results" message element
                    const message = document.createElement("div");
                    // Add class to the created element
                    message.setAttribute("class", "no_result");
                    // Add message text content
                    message.innerHTML = `<span>Found No Results for "${data.query}"</span>`;
                    // Append message element to the results list
                    list.prepend(message);
                }
            },
            noResults: true,
        },
        events: {
            input: {
                selection: (event) => {
                    const selection = event.detail.selection.value.value;
                    console.log(event)
                    auto_location.input.value = selection;
                }
            }
        },
    });

    const auto_diagnosis = new autoComplete({
        selector: "#get_diagnosis",
        data: {
            src: async (query) => {
                try {
                    console.log(query)
                    // Fetch Data from external Source
                    const source = await fetch('/export/get_diagnosis/?term='+query);
                    // Data should be an array of `Objects` or `Strings`
                    const data = await source.json();
                    console.log(data)
                    return data;
                } catch (error) {
                    return error;
                }
            },
            keys: ["value"]
        },
        threshold: 2,
        debounce: 300,
        resultItem: {
            highlight: true
        },
        resultsList: {
            destination: "#search-results-diagnosis",
            element: (list, data) => {
                //console.log(list)
                console.log(data)
                if (!data.results.length) {
                    // Create "No Results" message element
                    const message = document.createElement("div");
                    // Add class to the created element
                    message.setAttribute("class", "no_result");
                    // Add message text content
                    message.innerHTML = `<span>Found No Results for "${data.query}"</span>`;
                    // Append message element to the results list
                    list.prepend(message);
                }
            },
            noResults: true,
        },
        events: {
            input: {
                selection: (event) => {
                    const selection = event.detail.selection.value.value;
                    console.log(event)
                    auto_diagnosis.input.value = selection;
                }
            }
        },
    });

    // $('#get_location').autocomplete({
    //     serviceUrl: "/export/get_locations",
    //     onSelect: function (event, ui) {
    //         add_location(ui.item.value);
    //         $('ui-id-1').empty();
    //     },
    //     close: function () {
    //         $("#get_location").val("");
    //         $("#get_location").attr('placeholder', 'Enter a city');
    //     }
    // });

    // $("#get_diagnosis").autocomplete({
    //     serviceUrl: "/export/get_diagnosis",
    //     minLength: 2,
    //     onSelect: function (event, ui) {
    //         add_disease(ui.item.id, ui.item.value);
    //         $('ui-id-2').empty();
    //     },
    //     close: function () {
    //         $("#get_diagnosis").val("");
    //         $("#get_diagnosis").attr('placeholder', 'Enter a diagnosis');
    //     },
    // });


    $('#get_diseases').on("keyup", function () {
        var get_diseases = $('#get_diseases');
        fetch_post(
            "/experiment/group_diseases/cid-10/",
            {
                'search_text': (get_diseases.val().length >= 3 ? get_diseases.val() : ''),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),
                'group_id': ''
            },
            searchSuccessDiseases
        );

        // $.ajax({
        //     type: "POST",
        //     url: "/experiment/group_diseases/cid-10/",
        //     data: {
        //         'search_text': (get_diseases.val().length >= 3 ? get_diseases.val() : ''),
        //         'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),
        //         'group_id': ''
        //     },
        //     success: searchSuccessDiseases,
        //     dataType: 'html'
        // });
    });

    function searchSuccessDiseases(data, textStatus, jqXHR) {
        $('#search-results-diagnosis').html(data);
    }


});

function show_modal_remove(subject_id) {
    var modal_remove = document.getElementById('remove-participant');
    modal_remove.removeAttribute("disabled");
    modal_remove.setAttribute("value", 'remove-' + subject_id);
    $('#modalRemove').modal('show');
}

function disable_remove_button() {
    var modal_remove = document.getElementById('remove-participant');
    modal_remove.setAttribute("disabled", "disabled");
    modal_remove.setAttribute("value", 'remove');
}

//Cria os elementos html dinamicamente
function add_location(location) {
    //remove um item ds lista de resultados
    var ul_search_locations = document.getElementById('search-results-locations');
    var ul_location_list = document.getElementById('ul-location-list');
    if (ul_location_list != null) ul_search_locations.removeChild(ul_location_list);

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
    var textnode = document.createTextNode(location);
    //botão
    var btn_node = document.createElement('BUTTON');
    btn_node.id = "btn" + location;
    btn_node.type = "button";
    btn_node.className = "btn btn-default unbuttonmize";
    btn_node.appendChild(checknode);
    btn_node.appendChild(textnode);
    // btn_node.onclick = null;

    //criar span element
    var spannode = document.createElement('span');
    spannode.className = "fa-fw fa fa-remove";
    // spannode.data-toggle("tooltip");
    spannode.style.color = "indianred";
    spannode.style.verticalAlign = "-10%";
    spannode.title = "Remover";

    //criar a tag
    var tagnode = document.createElement('a');
    tagnode.id = location;
    tagnode.onclick = function (event) {
        // alert("remove " + this.id);
        var localization_div = document.getElementById("localization_list");
        var node = document.getElementById("btn" + this.id);
        localization_div.removeChild(node);
    };
    tagnode.appendChild(spannode);
    btn_node.appendChild(tagnode);

    //container
    var localization_div = document.getElementById("localization_list")
    localization_div.appendChild(btn_node);
}

function add_disease(id, disease) {
    // alert("id: " + id + "class of diseases: " + disease);
    //remove um item da lista de resultados
    var ul_search_diagnosis = document.getElementById('search-results-diagnosis');
    var ul_diagnosis_list = document.getElementById('ul-diagnosis-list');
    if (ul_diagnosis_list != null) ul_search_diagnosis.removeChild(ul_diagnosis_list);

    //checkbox
    var checknode = document.createElement('input');
    checknode.type = 'checkbox';
    checknode.name = 'selected_diagnosis';
    checknode.value = id;
    checknode.setAttribute("checked", true);
    checknode.style.display = "none";
    //label
    var textnode = document.createTextNode(disease);
    // textnode.name = 'selected_classification_of_diseases';
    textnode.value = disease;
    //botão
    var btn_node = document.createElement('BUTTON');
    btn_node.id = "btn" + disease;
    btn_node.type = "button"
    btn_node.className = "btn btn-default unbuttonmize";
    btn_node.appendChild(checknode);
    btn_node.appendChild(textnode);
    // btn_node.onclick = null;

    //criar span element
    var spannode = document.createElement('span');
    spannode.className = "fa-fw fa fa-remove";
    // spannode.data-toggle("tooltip");
    spannode.style.color = "indianred";
    spannode.style.verticalAlign = "-10%";
    spannode.title = "Remover";

    //limpa o campo de entrada para a busca por diagnostico
    var input_diagnosis = document.getElementById("get_diagnosis");
    if (input_diagnosis == null)
        input_diagnosis = document.getElementById("get_diseases");
    input_diagnosis.value = "";
    input_diagnosis.placeholder = "";

    //criar a tag
    var tagnode = document.createElement('a');
    tagnode.id = disease;
    tagnode.onclick = function (event) {
        // alert("remove " + this.id);
        var diagnosis_div = document.getElementById("diagnosis_list");
        var node = document.getElementById("btn" + this.id);
        diagnosis_div.removeChild(node);
        input_diagnosis.value = "";
    };
    tagnode.appendChild(spannode);
    btn_node.appendChild(tagnode);

    //container
    var diagnosis_div = document.getElementById("diagnosis_list")
    diagnosis_div.appendChild(btn_node);

}