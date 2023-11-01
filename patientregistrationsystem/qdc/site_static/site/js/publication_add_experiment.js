/**
 * Created by erocha on 16/03/17.
 */

"use strict";
document.addEventListener("DOMContentLoaded", () => {
    var select_research_project = $("#id_research_projects");
    var select_experiments = $("#id_experiments");

    select_research_project.on("change", async function () {
        var research_project_id = $(this).val();
        if (research_project_id == "") {
            research_project_id = "0";
        }

        const url = "/experiment/get_experiments_by_research_project/" + research_project_id;
        const response = await fetch(url);

        const list_of_experiments = await response.json();
        let options = '<option value="" selected="selected">---------</option>';
        for (var i = 0; i < list_of_experiments.length; i++) {
            options += '<option value="' + list_of_experiments[i].pk + '">' + list_of_experiments[i].fields['title'] + '</option>';
        }
        select_experiments.html(options);
        select_experiments.on("change");

        // $.getJSON(url, function (list_of_experiments) {
        //     var options = '<option value="" selected="selected">---------</option>';
        //     for (var i = 0; i < list_of_experiments.length; i++) {
        //         options += '<option value="' + list_of_experiments[i].pk + '">' + list_of_experiments[i].fields['title'] + '</option>';
        //     }
        //     select_experiments.html(options);
        //     select_experiments.on("change");
        // });

    });

});
