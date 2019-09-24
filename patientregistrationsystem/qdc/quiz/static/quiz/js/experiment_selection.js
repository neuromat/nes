/**
 * Created by mruizo on 08/12/16.
 */


$(document).ready(function () {
    var select_research_project = $("#id_research_projects");
    var select_experiments = $("#id_experiments");
    var select_groups = $("#group_selected");
    var select_experiment_participants = $("#multiselect_2");
    // var values = $('#id_research_projects').val();
    select_groups.prop('disabled', true);

    select_research_project.change(function () {
        var study_id = $(this).val();
        if (study_id == "") {
            study_id = "0";
        }

        var url = "/export/get_experiments_by_study/" + study_id;
        
        $.getJSON(url, function(experiments_list) {
            var options = '<option value="" selected="selected">---------</option>';
            for (var i = 0; i < experiments_list.length; i++) {
                options += '<option value="' + experiments_list[i].pk + '">' + experiments_list[i].fields['title'] + '</option>';
            }
            select_experiments.html(options);
            select_experiments.change();
        });
        
    });

    select_experiments.change(function () {
        var experiment_id = $(this).val();

        if (experiment_id == "") {
            experiment_id = "0";
        }

        // Get groups
        var url = "/export/get_groups_by_experiment/" + experiment_id;
        $.getJSON(url, function (group_list) {
           var options = "";
           for (var i = 0; i < group_list.length; i++) {
                options += '<option value="' + group_list[i].pk + '">' + group_list[i].fields['title'] + '</option>';
           }

            select_groups.html(options);
            select_groups.prop('disabled', false);
        });

        // Get participants for RandomForests Plugin
        if (experiment_id == 0) {
            select_experiment_participants.html('<option></option>');
        }
        var url = "/plugin/get_participants_by_experiment/" + experiment_id;
        $.getJSON(url, function (participants) {
            var options = "";
            for (var i = 0; i < participants.length; i++) {
                options += '<option value="' + participants[i].subject_of_group_id + '">' + participants[i].participant_name + ' - ' + participants[i].group_name + '</option>';
            }

            select_experiment_participants.html(options);
            select_experiment_participants.prop('disabled', false);
        });
    });

});
