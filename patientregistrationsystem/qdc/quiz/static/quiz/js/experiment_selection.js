/**
 * Created by mruizo on 08/12/16.
 */


$(document).ready(function () {
    var select_research_project = $("#id_research_projects");
    var select_experiments = $("#id_experiments");
    var select_groups = $("#id_groups");
    // var values = $('#id_research_projects').val();

    select_research_project.click(function () {
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
            // select_experiments.change();
        });
        
    });

    $("button").click(function(){
        var values = $('#id_research_projects').val();
        var studies = String(values);
        // var studies = [];
        // for(var i in values){
        //     studies.push({
        //         study_id:values[i]
        //     })
        // }

        var url = "/export/get_experiment_by_study/" + studies;

        $.getJSON(url, function(experiments_list) {
            var options = '<option value="" selected="selected">---------</option>';
            for (var i = 0; i < experiments_list.length; i++) {
                options += '<option value="' + experiments_list[i].pk + '">' + experiments_list[i].fields['title'] + '</option>';
            }
            select_experiments.html(options);
            // select_experiments.change();
        });

    });
    
    // select_research_project.change(function () {
    //     var study_id = $(this).val();
    //
    //     if (study_id == "") {
    //         study_id = "0";
    //     }
    //
    //     var url = "/export/get_experiment_by_study/" + study_id;
    //    
    //     $.getJSON(url, function(experiments_list) {
    //         var options = '<option value="" selected="selected">---------</option>';
    //         for (var i = 0; i < experiments_list.length; i++) {
    //             options += '<option value="' + experiments_list[i].pk + '">' + experiments_list[i].fields['title'] + '</option>';
    //         }
    //         select_experiments.html(options);
    //         // select_experiments.change();
    //     });
    // });
    
    // select_experiments.change(function () {
    //    var experiment_id = $(this).val();
    //    
    //     if (experiment_id == "") {
    //         experiment_id = "0";
    //     }
    //
    //     var url = "/export/get_group_by_experiment/" + experiment_id;
    //    
    //     $.getJSON(url, function (group_list) {
    //        var options = '<option value="" selected="selected">---------</option>';
    //        for (var i = 0; i < group_list.length; i++) {
    //             options += '<option value="' + group_list[i].pk + '">' + group_list[i].fields['title'] + '</option>';
    //         }
    //
    //         select_groups.html(options);
    //         select_groups.change();
    //     });
    // });

});
    