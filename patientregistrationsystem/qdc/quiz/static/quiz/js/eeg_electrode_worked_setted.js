/**
 * Created by mruizo on 08/07/16.
 */

document.addEventListener("DOMContentLoaded", init, false);
positions = [];
radio = 25;

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

    canvas.addEventListener("mousedown", getPosition, false);
}

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

function refresh_Screen(){
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

function worked(){

    for(var i in positions) {
        var position = positions[i];
        chkboxname = "position_status_" + position.id;

        if(!document.getElementById(chkboxname).checked)
            position.worked = false;
        else
            position.worked = true;
    }
    refresh_Screen();

};

function validPosition(new_x, new_y){
    var x = parseInt(new_x);
    var y = parseInt(new_y);
    var dx,dy;
    var valid = false;

    for(var i in positions) {
        position = positions[i];
        dx = x - parseInt(position.x);
        dy = y - parseInt(position.y);

        dist = Math.sqrt(dx*dx + dy*dy);
        if(dist < radio){
            valid= true;
            chkboxname = "position_status_" + position.id;

            chkbox = document.getElementById(chkboxname);
            if(chkbox.checked) {
                chkbox.checked = false;
                position.worked = false;
            }else {
                position.worked = true;
                chkbox.checked = true;
            }
        }
    }
    return valid;
}

function getPosition(event){

    var x = new Number();
    var y = new Number();
    var canvas = document.getElementById("electrodeMapCanvas");
    context = canvas.getContext("2d");


    if (event.layerX || event.layerX == 0) { // Firefox
        event._x = event.layerX;
        event._y = event.layerY;
    } else if (event.offsetX || event.offsetX == 0) { // Opera
        event._x = event.offsetX;
        event._y = event.offsetY;
    }

    x = parseInt(event._x);
    y = parseInt(event._y);

    if(validPosition(x,y)) refresh_Screen();
};