/**
 * Created by mruizo on 27/01/17.
 */

$(document).ready(function () {

    $('#get_diagnosis').on("keyup", function () {
        var get_diagnosis = $('#get_diagnosis');

        fetch_post(
            "/export/get_diagnosis/",
            {
                'search_text': (get_diagnosis.val().length >= 3 ? get_diagnosis.val() : ''),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),
            },
            searchSuccessDiagnoses,
        );

        // $.ajax({
        //     type: "POST",
        //     url: "/export/get_diagnosis/",
        //     data: {
        //         'search_text': (get_diagnosis.val().length >= 3 ? get_diagnosis.val() : ''),
        //         'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),
        //     },
        //     success: searchSuccessDiagnoses,
        //     dataType: 'html'

        // });
    });

    function searchSuccessDiagnoses(data, textStatus, jqXHR) {
        $('#search-results-diagnosis').html(data);
    }

    const auto_diagnosis = new autoComplete({
        selector: "#get_diseases",
        data: {
            src: async (query) => {
                try {
                    console.log(query)
                    // Fetch Data from external Source
                    const source = await fetch('/experiment/group_diseases/cid-10/?term='+query);
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
        threshold: 3,
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

    // $('#get_diseases').autocomplete({
    //     source: "/experiment/group_diseases/cid-10/",
    //     minLength: 3,
    // });

});