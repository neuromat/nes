/**
 * Created by mruizo on 23/06/16.
 */

document.addEventListener("DOMContentLoaded", init, false);
var used_positions_counter = 0;
var positions = [];
var localization_system_id = 0;

function init(){
    var canvas = document.getElementById("electrodeMapCanvas");
    var ctx = canvas.getContext("2d");
    var eeg_positions = document.getElementById("eeg_electrode_position");
    //var positions = eval(eeg_positions.value);
    positions = eval(eeg_positions.value);
    used_positions_counter = positions.length;
    var localization_system = document.getElementById("localization_system_id");
    localization_system_id = localization_system.value;
    addSetted();
    //used();
    var imageObj = new Image();

    imageObj.onload = function(){
        ctx.drawImage(imageObj, 0,0,700,500);
        pintar();
    };
    var map_file = document.getElementById("map_file");
    imageObj.src = map_file.value;
    //imageObj.src = "/media/eeg_electrode_system_files/1/system_10x20.png";

    canvas.addEventListener("mousedown", getPosition, false);
}

function compare(a,b) {
  if (a.position < b.position)
    return -1;
  if (a.position > b.position)
    return 1;
  return 0;
}

//objs.sort(compare);

//cria dinamicamente a tabela e os checkboxs
function  addSetted(){
    positions.sort(compare);
    for(var i in positions){
        var position = positions[i];
        if(!position.delete){
            id = position.id;
            name = position.position;
            x = parseInt(position.x);
            y = parseInt(position.y);
            used = position.used;

            var posTable = document.getElementById("cap_positions").getElementsByTagName('tbody')[0];

            var row = posTable.insertRow(posTable.rows.length);
            var cell1 = row.insertCell(0);
            var cell2 = row.insertCell(1);

            var textnode=document.createTextNode(name);
            textnode.id = 'txt' + id;
            var checknode = document.createElement('input');
            checknode.type = 'checkbox';
            checknode.id = id;
            checknode.setAttribute("checked", true);
            if(used) checknode.setAttribute("disabled", "disabled");

            checknode.onclick = function(event){
            //if(document.getElementById("cap_positions").getElementsByTagName('td')[1].getElementsByTagName('input')[0].checked)
            if(!this.checked){ //checked estava true
                var i = this.parentNode.parentNode.rowIndex;
                document.getElementById("cap_positions").deleteRow(i);
                setted(this.id);
            }

        };

        cell1.appendChild(textnode);
        cell2.appendChild(checknode);

        row.appendChild(cell1);
        row.appendChild(cell2);

        posTable.appendChild(row);

        }

    }

}

//Funcao que coloca delete = true para posteriormente ser deletado do banco de dados
function setted(positionId){
    var canvas = document.getElementById("electrodeMapCanvas");
    var ctx = canvas.getContext("2d");

    for(var i in positions) {
        var position = positions[i];

        if(position.id == positionId) {
            positions[i].delete = true; //this point is deleted
            used_positions_counter--;

            var imageObj = new Image();
            imageObj.onload = function(){
                ctx.drawImage(imageObj, 0,0,700,500);
                pintar();
            };
            var map_file = document.getElementById("map_file");
            imageObj.src = map_file.value;
        }
    }

};

function pintar(){
    var canvas = document.getElementById("electrodeMapCanvas");
    var context = canvas.getContext("2d");

    for(var i in positions){
        var position = positions[i];
        if(!position.delete){
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


function addRow(index){
    var position = positions[index-1];
    id = position.id;
    name = position.position;
    x = parseInt(position.x);
    y = parseInt(position.y);

    var posTable = document.getElementById("cap_positions").getElementsByTagName('tbody')[0];

    var row = posTable.insertRow(posTable.rows.length);
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);

    var textnode=document.createTextNode(name);
    textnode.id = 'txt_' + id;
    var checknode = document.createElement('input');
    checknode.type = 'checkbox';
    checknode.id = id;
    checknode.setAttribute("checked", true);
    checknode.onclick = function(event){
        //if(document.getElementById("cap_positions").getElementsByTagName('td')[1].getElementsByTagName('input')[0].checked)
        if(!this.checked){ //checked estava true
            var i = this.parentNode.parentNode.rowIndex;
            document.getElementById("cap_positions").deleteRow(i);
            setted(this.id);
        }

    };
    cell1.appendChild(textnode);
    cell2.appendChild(checknode);

    row.appendChild(cell1);
    row.appendChild(cell2);

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

    if (confirm("Confirms the coordinates? x: " + x + " and  y: " + y) == true) {
        var id = positions.length + 1;
        var name = prompt("Please enter the name this point", id);
        if(name != null){
            id = localization_system_id + "_" + id;
            context.beginPath();
            context.arc(x, y, 5, 0, 2 * Math.PI);
            context.fillStyle = "red";
            context.fill();
            context.stroke();
            positions.push({
                id : id,
                position: name,
                x: x,
                y: y,
                used: false, //this point is not used by some layout
                existInDB: false, //this point doesn't exist in the DB
                delete: false //this point was not deleted
            });
            used_positions_counter++;
            var index = new Number();
            index = positions.length;
            addRow(index);
        }
    }

};

function sendPositions(){
    var url = "/experiment/eeg_electrode_localization_system/get_positions/" + localization_system_id;

    $.getJSON(
        url,
        {positions : JSON.stringify(positions)},
        function(data){
            alert(data[0].new + " positions saved! and " + data[0].delete + " positions deleted!")
        }
    );
};