/**
 * Created by mruizo on 31/05/16.
 */

//window.onload = function() {
//    var c = document.getElementById("electrodeMapCanvas");
//    var ctx = c.getContext("2d");
//    var imageObj = new Image();
//
//    imageObj.onload = function(){
//        ctx.drawImage(imageObj, 0,0,700,500);
//   };
////    //imageObj.src = 'http://www.html5canvastutorials.com/demos/assets/darth-vader.jpg';
//    imageObj.src = 'https://www.ant-neuro.com/sites/default/files/images/waveguard_layout_024ch.png';
////    //imageObj.src = document.getElementById("scream");
////
//}

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
        //pintar();
    };
    var map_file = document.getElementById("map_file");
    //imageObj.src = "/media/eeg_electrode_system_files/3/10-20_system_for_EEG.png;
    imageObj.src = map_file.value;
    //imageObj.src = 'https://www.ant-neuro.com/sites/default/files/images/waveguard_layout_024ch.png';
    //canvas.addEventListener("mousedown", getPosition, false);
    //canvas.addEventListener('mousedown',ev_canvas, false);
    //canvas.addEventListener('mouseup',ev_canvas, false);

}

function used(){
    var canvas = document.getElementById("electrodeMapCanvas");
    var context = canvas.getContext("2d");
    var eeg_positions = document.getElementById("eeg_electrode_position");

    positions = eval(eeg_positions.value);

    for(var i in positions) {
        var position = positions[i];

        if(document.getElementById(position.id).checked == false) {
        // if(document.getElementById(position.id).checked == false) {
            //context.clearRect(0, 0, canvas.width,canvas.height);
            delete positions[i];
            //init();
        }else{
            positions.push({
                id:"position.id",

            });
        }
    }

    var canvas = document.getElementById("electrodeMapCanvas");
    var ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width,canvas.height);
    var imageObj = new Image();

    imageObj.onload = function(){
        ctx.drawImage(imageObj, 0,0,700,500);
        pintar(positions);
    };
    // imageObj.src = 'https://www.ant-neuro.com/sites/default/files/images/waveguard_layout_024ch.png';
    var map_file = document.getElementById("map_file");
    imageObj.src = map_file.value;


}

//function getPosition(event){
//    var x = new Number();
//    var y = new Number();
//    var canvas = document.getElementById("electrodeMapCanvas");
//    context = canvas.getContext("2d");
//
//    if(event.x != undefined && event.y != undefined){
//        x=event.x;
//        y=event.y;
//    }else{
//        x = event.clientX + document.body.scrollLeft +
//              document.documentElement.scrollLeft;
//          y = event.clientY + document.body.scrollTop +
//              document.documentElement.scrollTop;
//    }
//    x -= canvas.offsetLeft;
//    y -= canvas.offsetTop;
//
//    pintar(context, x, y);
//    alert("x: " + x + "  y: " + y);
//
//};

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

                        context.beginPath()
                        context.arc(mouseX, mouseY, 5, 0, 2 * Math.PI);
                        context.fill();
                        context.stroke();

                        context.font = '10pt Calibri';
                        context.fillStyle = 'black';
                        context.fillText(mouseX + "," + mouseY, mouseX - 20, mouseY + 21);

                    }//fim if ev.which == 1

                    if(ev.which == 3){
                        //alert("Right click done!");
                        mouseX = parseInt(ev._x);
                        mouseY = parseInt(ev._y);

                        for ( var i in dots) {
                            var dot = dots[i];
                            var dx = mouseX - dot.x;
                            var dy = mouseY - dot.y;

                            var dist = (dx * dx) + (dy * dy);
                            if (compara(dist,dot.rXr)) {
                                context.clearRect(0, 0, canvas.width,
														canvas.height);
                                delete dots[i];
                                init();
                            }
                        }
                    }//fim if ev.which == 3

                }//fim func(ev)

function pintar(positions){
    var canvas = document.getElementById("electrodeMapCanvas");
    var context = canvas.getContext("2d");
    //context.clearRect(0, 0, canvas.width,canvas.height);
    //init();
    //var eeg_positions = document.getElementById("eeg_electrode_position");
    //positions = eval(eeg_positions.value);
    for(var i in positions){
        var position = positions[i];
        x = parseInt(position.x);
        y = parseInt(position.y);

        context.beginPath()
        context.arc(x, y, 5,0,2 * Math.PI);
        context.fillStyle = "red";
        context.fill();
        context.stroke();

        //context.font = '10pt Calibri';
        //context.fillStyle = 'black';
        //context.fillText(x + "," + y, x - 20, y + 21);
        //context.arc(mouseX, mouseY, 5, 0, 2 * Math.PI);
    }


} //fim function pintar

//if(window.addEventListener){
//        window.addEventListener(
//            'load',
//            function () {
//                var canvas, context;
//                var dots = [];
//
//                function init(){
//                    canvas = document.getElementById('electrodeMapCanvas');
//                    //context = canvas.getContext("2d")
//                    if(!canvas){
//                        alert('Error: I cannot find the canvas element!');
//                        return;
//                    }
//
//                    if(!canvas.getContext){
//                        alert('Error:no canvas context!');
//                        return;
//                    }
//
//                    //Get the 2D canvas context
//                    context = canvas.getContext("2d");
//
//                    if(!context){
//                        alert('Error:failed context!');
//                        return;
//                    }
//
//                    context.clearRect(0,0,canvas.width, canvas.height);
//
//                    //Upload image to canvas
//                    var img = new Image();
//                    img.onload = function(){
//                        canvas.width = img.width;
//                        canvas.height =  img.height;
//
//                        context.drawImage(img,0,0);
//                        pintar(context);
//                    };
//                    img.src = 'https://www.ant-neuro.com/sites/default/files/images/waveguard_layout_024ch.png';
//
//                    // Attach the mousedown, mousemove and mouseup event listeners.
//                    canvas.addEventListener('mousedown',ev_canvas, false);
//                    canvas.addEventListener('mousemove',ev_canvas, false);
//                    canvas.addEventListener('mouseup',ev_canvas, false);
//                    canvas.addEventListener('contextmenu', function(ev) {
//                        ev.preventDefault();
//                        return false;
//                    }, false);
//
//                } //fim function init
//
//                function ev_canvas(ev) {
//
//                    if (ev.layerX || ev.layerX == 0) { // Firefox
//                        ev._x = ev.layerX;
//                        ev._y = ev.layerY;
//                    } else if (ev.offsetX || ev.offsetX == 0) { // Opera
//                        ev._x = ev.offsetX;
//                        ev._y = ev.offsetY;
//                    }
//
//                    func(ev);
//                }
//
//                //show tooltip when mouse hovers over dot
//                function func(ev) {
//
//                    if(ev.which == 1){
//                        mouseX = parseInt(ev._x);
//                        mouseY = parseInt(ev._y);
//
//                        dots.push({
//                            x: mouseX,
//                            y: mouseY,
//                            r: 4,
//                            rXr: 16,
//                            color: "red",
//                            nome: mouseX + "," + mouseY
//                        });
//
//                        context.fillStyle = 'red';
//
//                        context.beginPath()
//                        context.arc(mouseX, mouseY, 5, 0, 2 * Math.PI);
//                        context.fill();
//                        context.stroke();
//
//                        context.font = '10pt Calibri';
//                        context.fillStyle = 'black';
//                        context.fillText(mouseX + "," + mouseY, mouseX - 20, mouseY + 21);
//
//                    }//fim if ev.which == 1
//
//                    if(ev.which == 3){
//                        //alert("Right click done!");
//                        mouseX = parseInt(ev._x);
//                        mouseY = parseInt(ev._y);
//
//                        for ( var i in dots) {
//                            var dot = dots[i];
//                            var dx = mouseX - dot.x;
//                            var dy = mouseY - dot.y;
//
//                            var dist = (dx * dx) + (dy * dy);
//                            if (compara(dist,dot.rXr)) {
//                                context.clearRect(0, 0, canvas.width,
//														canvas.height);
//                                delete dots[i];
//                                init();
//                            }
//                        }
//                    }//fim if ev.which == 3
//
//                }//fim func(ev)
//
//                function pintar(context){
//                    for(var i in dots){
//                        var dot = dots[i];
//                        if(dot != undefined){
//                            context.fillStyle = 'red';
//
//                            context.beginPath()
//                            context.arc(dot.x, dot.y, 5,0,2 * Math.PI);
//                            context.fill;
//                            context.stroke();
//
//                            context.font = '10pt Calibri';
//                            context.fillStyle = 'black';
//                            context.fillText(dot.x + "," + dot.y, dot.x - 20, dot.y + 21);
//                        }
//                    }
//                }; //fim function pintar
//
//            }
//        )
//    }