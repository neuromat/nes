/**
 * Created by mruizo on 08/07/16.
 */

document.addEventListener("DOMContentLoaded", init, false);
positions = [];

function init(){
    var canvas = document.getElementById("electrodeMapCanvas");
    var ctx = canvas.getContext("2d");

    var eeg_positions = document.getElementById("eeg_electrode_position");
    positions = eval(eeg_positions.value);
    //positions.sort(compare);

    var imageObj = new Image();

    imageObj.onload = function(){
        ctx.drawImage(imageObj, 0,0,700,500);
        pintar();
    };
    var map_file = document.getElementById("map_file");
    imageObj.src = map_file.value;

    //canvas.addEventListener("mousedown", getPosition, false);
}

//function compare(a,b) {
//  if (a.position < b.position)
//    return -1;
//  if (a.position > b.position)
//    return 1;
//  return 0;
//}

function pintar(){
    var canvas = document.getElementById("electrodeMapCanvas");
    var context = canvas.getContext("2d");

    for(var i in positions){
        var position = positions[i];
        if(position.worked){
            x = parseInt(position.x);
            y = parseInt(position.y);

            context.beginPath();
            context.arc(x, y, 5, 0, 2 * Math.PI);
            context.fillStyle = "red";
            context.fill();
            context.stroke();
        }
    }
}; //fim function pintar

function worked(){

    for(var i in positions) {
        var position = positions[i];
        chkboxname = "position_status_" + position.id;

        if(!document.getElementById(chkboxname).checked)
            position.worked = false;
        else
            position.worked = true;
    }

    var canvas = document.getElementById("electrodeMapCanvas");
    var ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width,canvas.height);

    var imageObj = new Image();

    imageObj.onload = function() {
        ctx.drawImage(imageObj, 0, 0, 700, 500);
        pintar();
    };
    var map_file = document.getElementById("map_file");
    imageObj.src = map_file.value;
};

function sendWorkedPositions(){
    var url = "/experiment/eeg_data/edit_image/set_worked_positions/";

    $.getJSON(
        url,
        {positions : JSON.stringify(positions)},
        function(data){
            alert(" positions updated!")
        }
    );
};