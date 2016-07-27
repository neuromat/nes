/**
 * Created by mruizo on 27/07/16.
 */

/*
   * A cada refresh (F5) da página, o método "montarFigura()"
   * é executado.
   * */
  window.onload=function(){
         montarFigura();
  };

  function montarFigura() {

             /*
              * Capturamos o objeto/container canvas através do seu ID.
              * Você também pode optar por utilizar jQuery, a lógica é a mesma, só
              * muda a sintaxe.
              * */
               canvas = document.getElementById("canvasQuadrado");

               canvas.addEventListener('click', function(e) {

                    var rect = this.getBoundingClientRect();

                    //Criamos uma estrutura contendo as coordenadas atuais do mouse
                    var coords = {
                        x : e.clientX - rect.left,
                        y : e.clientY - rect.top
                    };
                    console.log("Coordenada Atual: " + coords.x + ", " + coords.y);

                    //Capturamos o contexto 2d do canvas
                    ctx = this.getContext('2d');

                    //Preenchemos a cor em hexadecimal
                    ctx.fillStyle = "#FFDEAD";

                    //Criamos o retangulo na tela
                    ctx.fillRect(0, 0, 150, 75);

                    //pintando o ponto clickado
                    ctx.beginPath();
                    var gradient = ctx.createLinearGradient(0, 0, 170, 0);
                    gradient.addColorStop("0", "magenta");
                    gradient.addColorStop("0.5", "red");
                    gradient.addColorStop("1.0", "blue");

                    // Fill with gradient
                    ctx.strokeStyle = gradient;
                    ctx.arc(coords.x, coords.y, 10, 0, 2 * Math.PI);
                    //ctx.fillStyle = "red";
                    //ctx.fill();
                    ctx.stroke();

               }, false);

               console.log("Capturando canvasQuadrado em formato 2D");
               ctx = canvas.getContext('2d');

               console.log("Colorindo canvas no plano x,y");

               //setamos a cor como preta para depois criar o retangulo
               ctx.fillStyle="black";

               //criamos o retangulo no plano passando os 4 vertices que o mesmo possui
               ctx.fillRect(0,0,150,75);

  }