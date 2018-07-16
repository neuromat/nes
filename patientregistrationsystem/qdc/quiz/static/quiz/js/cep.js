//Busca CEP utilizando o sistema ViaCEP. Ref: https://viacep.com.br/exemplo/javascript/

function limpa_formulário_cep() {
        //Limpa valores do formulário de cep.
        document.getElementById('id_street').value=("");
        document.getElementById('id_district').value=("");
        document.getElementById('get_location').value=("");
        // document.getElementById('state').value=("");
}

function meu_callback(conteudo) {
    // TODO: Add value to the state field
    if (!("erro" in conteudo)) {
        //Atualiza os campos com os valores.
        document.getElementById('id_street').value=(conteudo.logradouro);
        document.getElementById('id_district').value=(conteudo.bairro);
        document.getElementById('get_location').value=(conteudo.localidade);
        // document.getElementById('state').value=(conteudo.uf);
    } //end if.
    else {
        //CEP não Encontrado.
        limpa_formulário_cep();
        alert("CEP não encontrado.");
    }
}

function pesquisacep(valor) {

    //Nova variável "cep" somente com dígitos.
    var cep = valor.replace(/\D/g, '');

    //Verifica se campo cep possui valor informado.
    if (cep != "") {

        //Expressão regular para validar o CEP.
        var validacep = /^[0-9]{8}$/;

        //Valida o formato do CEP.
        if(validacep.test(cep)) {

            //Preenche os campos com "..." enquanto consulta webservice.
            document.getElementById('id_street').value="...";
            document.getElementById('id_district').value="...";
            document.getElementById('get_location').value="...";
            // document.getElementById('id_state').value="...";

            //Cria um elemento javascript.
            var script = document.createElement('script');

            //Sincroniza com o callback.
            script.src = '//viacep.com.br/ws/'+ cep + '/json/?callback=meu_callback';

            //Insere script no documento e carrega o conteúdo.
            document.body.appendChild(script);

        } //end if.
        else {
            //cep é inválido.
            limpa_formulário_cep();
            alert("Formato de CEP inválido.");
        }
    } //end if.
    else {
        //cep sem valor, limpa formulário.
        limpa_formulário_cep();
    }
}