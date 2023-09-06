/**
 * Created by mruizo on 31/05/16.
 */


window.onload = function() {
    var eeg_positions = document.getElementById("eeg_electrode_position");
    var positions = eval(eeg_positions.value);
    
    used();
    pintar(positions);
};

document.addEventListener("DOMContentLoaded", init, false);

function init(){
    var canvas = document.getElementById("electrodeMapCanvas");
    var ctx = canvas.getContext("2d");
    var imageObj = new Image();

    imageObj.onload = function(){
        ctx.drawImage(imageObj, 0,0,700,500);
    };
    var map_file = document.getElementById("map_file");
    imageObj.src = map_file.value;
}

function used(){
    var canvas = document.getElementById("electrodeMapCanvas");
    var context = canvas.getContext("2d");
    var eeg_positions = document.getElementById("eeg_electrode_position");
    var used_positions_field = document.getElementById("used_positions");

    var used_positions_counter = 0;

    positions = eval(eeg_positions.value);

    for(var i in positions) {
        var position = positions[i];

        if(document.getElementById(position.id).checked == false) {
            delete positions[i];
        }else{
            used_positions_counter++;
            positions.push({
                id:"position.id",
            });
        }
    }

    used_positions_field.value = used_positions_counter;

    var canvas = document.getElementById("electrodeMapCanvas");
    var ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width,canvas.height);

    var imageObj = new Image();

    imageObj.onload = function() {
        ctx.drawImage(imageObj, 0, 0, 700, 500);
        pintar(positions);
    };
    var map_file = document.getElementById("map_file");
    imageObj.src = map_file.value;

}


function ev_canvas(ev) {
    var dots = [];
    if (ev.layerX || ev.layerX == 0) { // Firefox
        ev._x = ev.layerX;
        ev._y = ev.layerY;
    } else if (ev.offsetX || ev.offsetX == 0) { // Opera
        ev._x = ev.offsetX;
        ev._y = ev.offsetY;
    }
    func(ev,dots);
}

                //show tooltip when mouse hovers over dot
                function func(ev,dots) {
                    var canvas = document.getElementById("electrodeMapCanvas");
                    context = canvas.getContext("2d");

                    if(ev.which == 1){
                        mouseX = parseInt(ev._x);
                        mouseY = parseInt(ev._y);

                        dots.push({
                            x: mouseX,
                            y: mouseY,
                            r: 4,
                            rXr: 16,
                            color: "red",
                            nome: mouseX + "," + mouseY
                        });

                        context.fillStyle = 'red';

                        context.beginPath();
                        context.arc(mouseX, mouseY, 5, 0, 2 * Math.PI);
                        context.fill();
                        context.stroke();

                        context.font = '10pt Calibri';
                        context.fillStyle = 'black';
                        context.fillText(mouseX + "," + mouseY, mouseX - 20, mouseY + 21);

                    }//fim if ev.which == 1

                    if(ev.which == 3){
                        // alert("Right click done!");
                        mouseX = parseInt(ev._x);
                        mouseY = parseInt(ev._y);

                        for ( var i in dots) {
                            var dot = dots[i];
                            var dx = mouseX - dot.x;
                            var dy = mouseY - dot.y;

                            var dist = (dx * dx) + (dy * dy);
                            if (compara(dist,dot.rXr)) {
                                context.clearRect(0, 0, canvas.width, canvas.height);
                                delete dots[i];
                                init();
                            }
                        }
                    }//fim if ev.which == 3
                }//fim func(ev)

function pintar(positions){
    var canvas = document.getElementById("electrodeMapCanvas");
    var context = canvas.getContext("2d");
    
    for(var i in positions){
        var position = positions[i];
        x = parseInt(position.x);
        y = parseInt(position.y);
        context.beginPath();
        context.arc(x, y, 5, 0, 2 * Math.PI);
        context.fillStyle = "red";
        context.fill();
        context.stroke();

    }
} //fim function pintar
