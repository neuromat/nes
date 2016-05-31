/**
 * Created by mruizo on 31/05/16.
 */

window.onload = function() {
    var c = document.getElementById("electrodeMapCanvas");
    var ctx = c.getContext("2d");
    var imageObj = new Image();

    imageObj.onload = function(){
        ctx.drawImage(imageObj, 69,50);
    };
    //imageObj.src = 'http://www.html5canvastutorials.com/demos/assets/darth-vader.jpg';
    //imageObj.src = 'http://www.mdpi.com/sensors/sensors-14-18172/article_deploy/html/images/sensors-14-18172f1.png';
    //var img = document.getElementById("scream");
    //ctx.drawImage(img, 10, 10);
}