/**
 * Created by mruizo on 08/12/16.
 */

"use strict";
document.addEventListener("DOMContentLoaded", () => {
    var select_research_project = $("#id_research_projects");
    var select_experiments = $("#id_experiments");
    var select_groups = $("#group_selected");
    var select_experiment_participants_from = $("#multiselect_2");
    var select_experiment_participants_to = $("#multiselect_2_to");

    select_groups.prop('disabled', true);

    select_research_project.on("change", async function () {
        var study_id = $(this).val();
        if (study_id == "") {
            study_id = "0";
        }

        const url = "/export/get_experiments_by_study/" + study_id;
        const response = await fetch(url);
        const experiments_list = await response.json();

        var options = '<option value="" selected="selected">---------</option>';
        for (var i = 0; i < experiments_list.length; i++) {
            options += '<option value="' + experiments_list[i].pk + '">' + experiments_list[i].fields['title'] + '</option>';
        }
        select_experiments.html(options);
        select_experiments.on("change");

        // $.getJSON(url, function (experiments_list) {
        //     var options = '<option value="" selected="selected">---------</option>';
        //     for (var i = 0; i < experiments_list.length; i++) {
        //         options += '<option value="' + experiments_list[i].pk + '">' + experiments_list[i].fields['title'] + '</option>';
        //     }
        //     select_experiments.html(options);
        //     select_experiments.on("change");
        // });

    });

    select_experiments.on("change", async function () {
        var experiment_id = $(this).val();

        // Clean up the "to" multiselect when loading, to avoid mixing participants
        // from different experiments when sending
        select_experiment_participants_to.empty();

        if (experiment_id == "") {
            experiment_id = "0";
        }

        // Get groups
        const url = "/export/get_groups_by_experiment/" + experiment_id;
        const response = await fetch(url);
        const group_list = await response.json();

        var options = "";
        for (var i = 0; i < group_list.length; i++) {
            options += '<option value="' + group_list[i].pk + '">' + group_list[i].fields['title'] + '</option>';
        }
        select_groups.html(options);
        select_groups.prop('disabled', false);

        // $.getJSON(url, function (group_list) {
        //     var options = "";
        //     for (var i = 0; i < group_list.length; i++) {
        //         options += '<option value="' + group_list[i].pk + '">' + group_list[i].fields['title'] + '</option>';
        //     }
        //     select_groups.html(options);
        //     select_groups.prop('disabled', false);
        // });

        // Get participants for RandomForests Plugin
        // Test for undefined as in plugin template for selecting
        // participants select_research_project is not defined. Otherwise
        // url bellow is called and causes a silent error.
        if (select_research_project.val() === undefined) {
            select_experiment_participants_from.html('<option></option>');
            if (experiment_id != 0) {
                // Fill multiselect "from" with a suitable ajax loading gif
                select_experiment_participants_from.html('<option></option>');
                $('#loading_box').css('display', 'flex');
                select_experiment_participants_from.prop('disabled', true);
            }

            const url = "/plugin/get_participants_by_experiment/" + experiment_id;
            const response = await fetch(url);
            const participants = await response.json();

            $('#loading_box').css('display', 'none');
            var options = "";
            for (var i = 0; i < participants.length; i++) {
                options += '<option value="' + participants[i].subject_of_group_id + '">' + participants[i].participant_name + ' - ' + participants[i].group_name + '</option>';
            }
            select_experiment_participants_from.html(options);
            select_experiment_participants_from.prop('disabled', false);

            // $.getJSON(url, function (participants) {
            //     $('#loading_box').css('display', 'none');
            //     var options = "";
            //     for (var i = 0; i < participants.length; i++) {
            //         options += '<option value="' + participants[i].subject_of_group_id + '">' + participants[i].participant_name + ' - ' + participants[i].group_name + '</option>';
            //     }
            //     select_experiment_participants_from.html(options);
            //     select_experiment_participants_from.prop('disabled', false);
            // });
        }
    });

});
