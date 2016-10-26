/**
 * Created by mruizo on 25/10/16.
 */

window.onload = function() {
    var select_localization_system = $("#id_localization_system_selection");
    var div_localization_system_image = $("#div-localization_system_image");
    var tms_position_localization_system_id = $("#tms_position_localization_system_id");
    var localization_system_selected_id = $("#localization_system_selected_id");

    if(localization_system_selected_id.val()){
        var canvas = document.getElementById("tmsMapCanvas");
        var ctx = canvas.getContext("2d");
        var imageObj = new Image();
        hotspot_x = $("#id_coordinate_x");
        hotspot_y = $("#id_coordinate_y");

        var x = parseInt(hotspot_x.val());
        var y = parseInt(hotspot_y.val());

        imageObj.onload = function(){
            ctx.drawImage(imageObj, 0,0,600,600);
            ctx.beginPath();
            ctx.arc(x, y, 5, 0, 2 * Math.PI);
            ctx.fillStyle = "red";
            ctx.fill();
            ctx.stroke();
        };
        imageObj.src = localization_system_selected_id.val();
    }

    select_localization_system.change(function () {
        var tms_localization_system = $(this).val();

        var split = tms_localization_system.split(",");
        tms_position_localization_system_id.value = parseInt(split[0]);
        var tms_localization_system_image = split[1];

        if(tms_localization_system_image==""){
            div_localization_system_image.hide();
            var canvas = document.getElementById("tmsMapCanvas");
            var ctx = canvas.getContext("2d");
            ctx.clearRect(0, 0, canvas.width,canvas.height);
        }else{
            div_localization_system_image.show();
            var canvas = document.getElementById("tmsMapCanvas");
            var ctx = canvas.getContext("2d");
            var imageObj = new Image();

            imageObj.onload = function(){
                ctx.drawImage(imageObj, 0,0,600,600);
            };
            imageObj.src = tms_localization_system_image;
            canvas.addEventListener("mousedown", getPosition, false);
        }

    });


};

// função que captura o evento 'click do mouse
function getPosition(event) {
    var x = new Number();
    var y = new Number();
    var canvas = document.getElementById("tmsMapCanvas");
    var hotspot_x = document.getElementById("id_coordinate_x");
    var hotspot_y = document.getElementById("id_coordinate_y");

    context = canvas.getContext("2d");

    var rect = this.getBoundingClientRect();

    var coords = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
    };

    x = parseInt(coords.x);
    y = parseInt(coords.y);

    if (confirm(gettext("Confirms the coordinates? x - y: ") + x + " - " + y) == true) {
        hotspot_x.value = x;
        hotspot_y.value = y;

        context.beginPath();
        context.arc(x, y, 5, 0, 2 * Math.PI);
        context.fillStyle = "red";
        context.fill();
        context.stroke();
        
        //var name = prompt(gettext("Please enter the name this point"), id);
        // if (name != null) {
        //     id = localization_system_id + "_" + id;
        //     context.beginPath();
        //     context.arc(x, y, 5, 0, 2 * Math.PI);
        //     context.fillStyle = "red";
        //     context.fill();
        //     context.stroke();
        //     positions.push({
        //         id: id,
        //         position: name,
        //         x: x,
        //         y: y,
        //         used: false, //this point is not used by some layout
        //         existInDB: false, //this point doesn't exist in the DB
        //         delete: false, //this point was not deleted
        //         update: false  //this point is not updated
        //     });
        //     used_positions_counter++;
        //     var index = new Number();
        //     index = positions.length;
        //     addRow(index);
        // }
    }


}

    // $(document).ready(function () {
    //         var div_localization_system_image = $("#id_localization_system_image");
    //         var select_localization_system = $("#id_localization_system_selection");
    //
    //         select_localization_system.change(function () {
    //             div_localization_system_image.visibility = "visible";
    //             var tms_localization_system_id = $(this).val();
    //
    //             if (tms_localization_system_id == "") {
    //                 div_localization_system_image.visibility = "hidden";
    //             }else{
    //                 var url = "/experiment/tms_data/get_json_tms_localization_image/" + tms_localization_system_id;
    //
    //                 $.getJSON(url, function (image_value) {
    //                      var map_file = image_value['tms_localization_system_image'];
    //                      document.addEventListener("DOMContentLoaded", init(map_file), false);
    //
    //                 })
    //             }
    //
    //         });
    //
    //         function init(image){
    //             var canvas = document.getElementById("tmsMapCanvas");
    //             var ctx = canvas.getContext("2d");
    //             var imageObj = new Image();
    //
    //             imageObj.onload = function(){
    //                 ctx.drawImage(imageObj, 0,0,700,500);
    //             };
    //             //var map_file = document.getElementById("map_file");
    //             imageObj.src = image;
    //         }
    //
    //     });