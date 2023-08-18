/**
 * Created by erocha on 16/03/17.
 */


$(document).ready(function () {
    var select_research_project = $("#id_research_projects");
    var select_experiments = $("#id_experiments");

    select_research_project.change(function () {
        var research_project_id = $(this).val();
        if (research_project_id == "") {
            research_project_id = "0";
        }

        var url = "/experiment/get_experiments_by_research_project/" + research_project_id;
        
        $.getJSON(url, function(list_of_experiments) {
            var options = '<option value="" selected="selected">---------</option>';
            for (var i = 0; i < list_of_experiments.length; i++) {
                options += '<option value="' + list_of_experiments[i].pk + '">' + list_of_experiments[i].fields['title'] + '</option>';
            }
            select_experiments.html(options);
            select_experiments.change();
        });
        
    });

});
    