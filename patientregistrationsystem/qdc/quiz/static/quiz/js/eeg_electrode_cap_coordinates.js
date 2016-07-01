/**
 * Created by mruizo on 23/06/16.
 */

document.addEventListener("DOMContentLoaded", init, false);
var dots = [];
var i = 57;
function init(){
    var canvas = document.getElementById("electrodeMapCanvas");
    var ctx = canvas.getContext("2d");
    var imageObj = new Image();

    imageObj.onload = function(){
        ctx.drawImage(imageObj, 0,0,700,500);
        paint();
    };
    var map_file = document.getElementById("map_file");
    imageObj.src = map_file.value;

    canvas.addEventListener("mousedown", getPosition, false);
    //canvas.addEventListener('mousedown',ev_canvas, false);
    //canvas.addEventListener('mouseup',ev_canvas, false);
    //canvas.addEventListener('contextmenu', function(ev) {
    //      ev.preventDefault();
    //      return false;
    //}, false);

}

function paint(){
    if(dots.length > 0){
        i =0;
        for ( var i in dots) {
	        var dot = dots[i];
            context.beginPath();
            context.arc(dot.x, dot.y, 5, 0, 2 * Math.PI);
            context.fillStyle = "red";
            context.fill();
            context.stroke();
            //addRow(dots.length,x,y);
        }
    }
}

function addRow(id,label,posx, posy){
    label = parseInt(label)+49;
    var posTable = document.getElementById("cap_positions").getElementsByTagName('tbody')[0];

    var row = posTable.insertRow(posTable.rows.length);
    var cell1 = row.insertCell(0);

    var textnode1=document.createTextNode("("+ id + "," + label + "," + posx + "," + posy + "," + "1" + ")" );

    cell1.appendChild(textnode1);

    row.appendChild(cell1);

    posTable.appendChild(row);

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

    context.beginPath();
    context.arc(x, y, 5, 0, 2 * Math.PI);
    context.fillStyle = "red";
    context.fill();
    context.stroke();

    if (confirm("x: " + x + "  y: " + y) == true) {
        dots.push({
            x: x,
            y: y,
            r: 4,
            rXr: 16,
            color: "red"
        });
        i = i+1;
        addRow(i,dots.length,x,y);
    } else {
        context.clearRect(0, 0, canvas.width,canvas.height);
        init();

    }

};