/**
 * Created by carlosribas on 03/05/2018.
 */

// function to select all collaborators
$(document).ready(function(){
    $("#select_all_collaborators").change(function(){
      $(".checkbox_collaborators").prop('checked', $(this).prop("checked"));
    });
});