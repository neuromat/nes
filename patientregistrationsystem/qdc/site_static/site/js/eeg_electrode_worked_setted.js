/**
 * Created by mruizo on 08/07/16.
 */

document.addEventListener("DOMContentLoaded", init, false);
positions = [];
radio = 25;

function init(){
    var canvas = document.getElementById("electrodeMapCanvas");
    if(canvas) var ctx = canvas.getContext("2d");

    var eeg_positions = document.getElementById("eeg_electrode_position");
    if(eeg_positions) positions = eval(eeg_positions.value);

    var imageObj = new Image();

    imageObj.onload = function(){
        ctx.drawImage(imageObj, 0,0,700,500);
        pintar();
    };
    var map_file = document.getElementById("map_file");
    if(map_file) imageObj.src = map_file.value;

    var editing = document.getElementById("image_status");
    if(editing) if(editing.value == "True") canvas.addEventListener("mousedown", getPosition, false);
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
}; //End function pintar

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
        chkboxname = "position_worked_" + position.id;

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
            chkboxname = "position_worked_" + position.id;

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

    var rect = this.getBoundingClientRect();
    var coords = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
    };

    x = parseInt(coords.x);
    y = parseInt(coords.y);

    if(validPosition(x,y)) refresh_Screen();
};