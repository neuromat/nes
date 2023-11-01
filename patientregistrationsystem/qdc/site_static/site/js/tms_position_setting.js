/**
 * Created by mruizo on 25/10/16.
 */

window.onload = function() {
    var select_localization_system = $("#id_localization_system_selection");
    var div_localization_system_image = $("#div-localization_system_image");
    var tms_position_localization_system_id = $("#tms_position_localization_system_id");
    var localization_system_selected_id = $("#localization_system_selected_id");
    var localization_system_selected = localization_system_selected_id.val();
    var editing_id = $("#editing_id");
    map_file="";

    if(localization_system_selected == "") {
        div_localization_system_image.hide();
    }else{
        var canvas = document.getElementById("tmsMapCanvas");
        if(canvas != null){
            var b64;
            var ctx = canvas.getContext("2d");
            var imageObj = new Image();
            hotspot_x = $("#id_coordinate_x");
            hotspot_y = $("#id_coordinate_y");
            tms_name = $("#id_name");

            var x = parseInt(hotspot_x.val());
            var y = parseInt(hotspot_y.val());
            var name = tms_name.val();
            imageObj.crossOrigin = "Anonymous";
            imageObj.onload = function(){
                ctx.drawImage(imageObj, 0,0,600,600);
                pintar(x,y,name);
                b64 = canvas.toDataURL("image/png");
                // document.getElementById('b-pre').innerText = b64;
                document.getElementById('id_spot_image').value = b64;
                // document.getElementById('id_spot_map').src = b64;
            };
            imageObj.src = localization_system_selected_id.val();
            map_file = imageObj.src;
            if(editing_id.val() == "True")
                canvas.addEventListener("mousedown", getPosition, false);

        }
        
    }

    select_localization_system.on("change", function () {
        var tms_localization_system = $(this).val();

        if(tms_localization_system == ""){
            div_localization_system_image.hide();
        }else{
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
                imageObj.crossOrigin = "Anonymous";
                imageObj.onload = function(){
                    ctx.drawImage(imageObj, 0,0,600,600);
                };
                imageObj.src = tms_localization_system_image;
                map_file = tms_localization_system_image;
                canvas.addEventListener("mousedown", getPosition, false);
            }
        }
    });

};

function pintar(x,y,name)
{
    var canvas = document.getElementById("tmsMapCanvas");
    var ctx = canvas.getContext("2d");
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, 2 * Math.PI);
    ctx.fillStyle = "red";
    ctx.fill();
    ctx.stroke();
    ctx.font="18px sans-serif";
    ctx.fillText(name, x+5, y-5);
};

// função que recarrega a imagem no canvas
function refresh_Screen(x,y,name){
    var canvas = document.getElementById("tmsMapCanvas");
    var ctx = canvas.getContext("2d");
    var b64;
    ctx.clearRect(0, 0, canvas.width,canvas.height);

    var imageObj = new Image();
    imageObj.crossOrigin = "Anonymous";
    imageObj.onload = function() {
        ctx.drawImage(imageObj, 0, 0, 600, 600);
        pintar(x,y,name);
        b64 = canvas.toDataURL("image/png");
        // document.getElementById('b-pre').innerText = b64;
        document.getElementById('id_spot_image').value = b64;
        // document.getElementById('id_spot_map').src = b64;

    };

    imageObj.src = map_file;

};

// função que captura o evento 'click do mouse'
function getPosition(event) {
    var x = new Number();
    var y = new Number();
    var canvas = document.getElementById("tmsMapCanvas");
    var hotspot_x = document.getElementById("id_coordinate_x");
    var hotspot_y = document.getElementById("id_coordinate_y");
    var tms_position = document.getElementById("id_name");

    context = canvas.getContext("2d");

    var rect = this.getBoundingClientRect();

    var coords = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
    };

    x = parseInt(coords.x);
    y = parseInt(coords.y);

    if (confirm(gettext("Confirms the coordinates? x - y: ") + x + " - " + y) == true) {
        var name = prompt(gettext("Please enter the name of the position"));
        if(name != null){
            hotspot_x.value = x;
            hotspot_y.value = y;
            tms_position.value = name;
            refresh_Screen(x,y,name);

        }

    }

}

