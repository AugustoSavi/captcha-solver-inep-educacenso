function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function verificarEEnviar() {
  // Array para armazenar o conteúdo base64 das imagens
  const base64Images = [];

  for (let index = 0; index < 5; index++) {
    const imgElement = document.getElementById(`visualCaptcha-img-${index}`);

    // Cria um canvas temporário
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Define as dimensões do canvas iguais às dimensões da imagem
    canvas.width = 64;
    canvas.height = 64;

    // Desenha a imagem no canvas
    ctx.drawImage(imgElement, 0, 0);

    // Obtém o conteúdo base64 do canvas
    const base64Data = canvas.toDataURL('image/png'); // Pode ser 'image/jpeg' também, dependendo do formato da imagem

    // Adiciona o conteúdo base64 ao array
    base64Images.push(base64Data);
  }

  // Obtém o texto da tag <strong>
  const strongText = document
    .querySelector('.visualCaptcha-explanation strong')
    .textContent.trim();

  // Envia as informações para o backend
  const apiUrl = 'http://localhost:5000/predict'; // Substitua pelo URL da sua API
  const requestBody = {
    strongText: strongText,
    base64Images: base64Images,
  };

  fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  })
    .then((response) => {
      if (response.ok) {
        return response.json(); // Transforma o corpo da resposta em JSON
      } else {
        console.error('Falha na requisição:', response.status);
        throw new Error('Falha na requisição');
      }
    })
    .then((jsonResponse) => {
      console.log('Requisição bem-sucedida!');
      console.log('Resposta:', jsonResponse); // Imprime o corpo da resposta como JSON
      jsonResponse.forEach((item, index) => {
        console.log(item);
        if (item.finded) {
          alert('index: '+ index + ' class: ' + item.class + ' Confidence: ' + item.confidence_score);
        }
      });
    });
}

// Criar um novo botão
const newButton = document.createElement('button');
newButton.textContent = 'Resolução do captcha';
newButton.className = 'btn box-principal-bg btn-block btn-round';
newButton.addEventListener('click', verificarEEnviar);

// Selecionar o elemento onde o novo botão deve ser inserido
const footerElement = document.querySelector('.footer');

// Inserir o novo botão antes do botão existente
footerElement.insertBefore(newButton, footerElement.firstChild);