/**
 * Created by mruizo on 23/06/16.
 */

document.addEventListener("DOMContentLoaded", init, false);
var used_positions_counter = 0;
var positions = [];
var localization_system_id = 0;
radio = 25;
var can_update = false;
var point_update = 0;
var point_update_name = "";

function init(){
    var canvas = document.getElementById("electrodeMapCanvas");
    var ctx = canvas.getContext("2d");
    var eeg_positions = document.getElementById("eeg_electrode_position");
    positions = eval(eeg_positions.value);
    used_positions_counter = positions.length;
    var localization_system = document.getElementById("localization_system_id");
    localization_system_id = localization_system.value;
    addSetted();
    var imageObj = new Image();

    imageObj.onload = function(){
        ctx.drawImage(imageObj, 0,0,700,500);
        pintar();
    };
    var map_file = document.getElementById("map_file");
    imageObj.src = map_file.value;

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

            a = document.createElement('a');
            a.innerHTML = name;
            a.name = id;
            if(used){
                a.style.color = "#808080";
                a.onclick = function(){false;}
            }else a.onclick = function(){
                update(this.name);
            }

            var btn_node = document.createElement('BUTTON');
            btn_node.id = id;
            var t = document.createTextNode("delete");
            btn_node.appendChild(t);
            if(used) btn_node.setAttribute("disabled", "disabled");
            btn_node.onclick = function(event){
                var i = this.parentNode.parentNode.rowIndex;
                document.getElementById("cap_positions").deleteRow(i);
                setted(this.id);
            }

            var textnode=document.createTextNode(name);
            textnode.id = 'txt' + id;

            var checknode = document.createElement('input');
            checknode.type = 'checkbox';
            checknode.id = id;
            checknode.setAttribute("checked", "checked");
            if(used) checknode.setAttribute("disabled", "disabled");

            checknode.onclick = function(event){
            //if(document.getElementById("cap_positions").getElementsByTagName('td')[1].getElementsByTagName('input')[0].checked)
            if(!this.checked){ //checked estava true
                var i = this.parentNode.parentNode.rowIndex;
                document.getElementById("cap_positions").deleteRow(i);
                setted(this.id);
            }

        };

        cell1.appendChild(a);
        cell2.appendChild(btn_node);

        row.appendChild(cell1);
        row.appendChild(cell2);

        posTable.appendChild(row);

        }

    }

}

function update(positionId){

    can_update = true;
    point_update = positionId;
    var canvas = document.getElementById("electrodeMapCanvas");
    var context = canvas.getContext("2d");

    alert('Please click on a new position on the image to update this point');
    for(var i in positions){
        var position = positions[i];
        if(position.id == positionId){
            position.update = true;
            point_update_name = position.position;
            x = parseInt(position.x);
            y = parseInt(position.y);

            var gradient=context.createLinearGradient(0,0,0,170);
            gradient.addColorStop(0,"magenta");
            gradient.addColorStop(0.5,"blue");
            gradient.addColorStop(1.0,"red");

            context.beginPath();
            context.strokeStyle = gradient;
            //context.lineWidth = 2;
            context.arc(x, y, 10, 0, 2 * Math.PI);

            //context.fill();
            context.stroke();
        }
        //refresh_Screen();
    }
};

//Funcao que coloca delete = true para posteriormente ser deletado do banco de dados
function setted(positionId){
    var canvas = document.getElementById("electrodeMapCanvas");
    var ctx = canvas.getContext("2d");

    for(var i in positions) {
        var position = positions[i];

        if(position.id == positionId) {
            positions[i].delete = true; //this point is deleted
            used_positions_counter--;
            refresh_Screen();
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
            context.strokeStyle = "red";
            if(position.used){
                context.strokeStyle = "gray";
                context.fillStyle = "gray";
            } 
            else context.fillStyle = "red";
            context.arc(x, y, 5, 0, 2 * Math.PI);
            context.fill();
            context.stroke();
        }
        // if(can_update && position.update){
        //     x = parseInt(position.x);
        //     y = parseInt(position.y);
        //
        //     var gradient=context.createLinearGradient(0,0,0,170);
        //     gradient.addColorStop("0","magenta");
        //     gradient.addColorStop("0.5","blue");
        //     gradient.addColorStop("1.0","red");
        //
        //     context.beginPath();
        //     context.strokeStyle = gradient;
        //     //context.lineWidth = 2;
        //     context.arc(x, y, 10, 0, 2 * Math.PI);
        //
        //     //context.fill();
        //     context.stroke();
        // }
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

    a = document.createElement('a');
    a.innerHTML = name;
    a.name = id;
    a.onclick = function(){
        update(this.name);
    }

    var btn_node = document.createElement('BUTTON');
    btn_node.id = id;
    var t = document.createTextNode("delete");
    btn_node.appendChild(t);
    btn_node.onclick = function(event){
        var i = this.parentNode.parentNode.rowIndex;
        document.getElementById("cap_positions").deleteRow(i);
        setted(this.id);
    }

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
    cell1.appendChild(a);
    cell2.appendChild(btn_node);

    row.appendChild(cell1);
    row.appendChild(cell2);

    posTable.appendChild(row);
}

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

function validPosition(new_x, new_y){
    var x = parseInt(new_x);
    var y = parseInt(new_y);
    var dx,dy;
    var valid = false;

    for(var i in positions) {
        position = positions[i];
        if(!position.delete){
            dx = x - parseInt(position.x);
            dy = y - parseInt(position.y);

            dist = Math.sqrt(dx*dx + dy*dy);
            if(dist < radio){
                valid= true;
                if(position.used){
                    alert("This coodinates can't be modified because is being used by some EEG layout setting! ")
                }else{
                    btn = document.getElementById(position.id);
                    position.delete = true;
                    var i = btn.parentNode.parentNode.rowIndex;
                    document.getElementById("cap_positions").deleteRow(i);
                }
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

    if (event.layerX || event.layerX == 0) { // Firefox
        event._x = event.layerX;
        event._y = event.layerY;
    } else if (event.offsetX || event.offsetX == 0) { // Opera
        event._x = event.offsetX;
        event._y = event.offsetY;
    }

    var coords = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
    };

    // x = parseInt(event._x);
    // y = parseInt(event._y);

    x = parseInt(coords.x);
    y = parseInt(coords.y);

    if(!can_update){
        if(validPosition(x,y)) refresh_Screen();
        else{
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
                         delete: false, //this point was not deleted
                         update: false  //this point is not updated
                     });
                     used_positions_counter++;
                     var index = new Number();
                     index = positions.length;
                     addRow(index);
                 }

             }
        }
    }else{
        alert("Updating point " + point_update_name);
        can_update = false;
        if (confirm("Confirms the coordinates? x: " + x + " and  y: " + y) == true) {
            var name = prompt("Please enter the name of the point", point_update_name);
            if(name != null){
                for(var i in positions){
                    var position = positions[i];
                    if(position.id == point_update){
                        chkbox = document.getElementById(position.id);
                        chkbox.checked = true;
                        position.name = name,
                        position.x = x,
                        position.y = y,
                        position.update = true
                    }
                }
                refresh_Screen();
            }
        }
    }

};

function sendPositions(){
    var url = "/experiment/eeg_electrode_localization_system/get_positions/" + localization_system_id;

    $.getJSON(
        url,
        {positions : JSON.stringify(positions)},
        function(data){
            //alert(data[0].new + " positions saved! and " + data[0].delete + " positions deleted!")
        }
    );
};