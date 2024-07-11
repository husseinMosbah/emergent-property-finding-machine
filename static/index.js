
const inButton = document.querySelector('#in-button');
const outButton = document.querySelector('#out-button');
const inTerminal = document.querySelector('#in-terminal');
const outTerminal = document.querySelector('#out-terminal');

inButton.addEventListener('click', () => {
  inButton.classList.add('active');
  outButton.classList.remove('active');
  inTerminal.classList.add('active');
  outTerminal.classList.remove('active');
});

outButton.addEventListener('click', () => {
  inButton.classList.remove('active');
  outButton.classList.add('active');
  inTerminal.classList.remove('active');
  outTerminal.classList.add('active');
});

const inForm = document.querySelector('#in-form');

inForm.addEventListener('submit', (event) => {
    event.preventDefault();
    
    const itr = document.querySelector('#itr').value;
    const message = document.querySelector('#message').value;
    const hesitations = document.querySelector('#hesitations').value;
    
    const data = {itr: itr, message: message, hesitations: hesitations};

    fetch('/in_terminal', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data);
    })
    .catch((error) => {
      console.error('Error:', error);
    });
    
    inForm.reset();
});

const outForm = document.querySelector('#out-form');
const outputBox = document.querySelector('#output');
const downloadButton = document.querySelector('#download-button');

outForm.addEventListener('submit', (event) => {
  event.preventDefault();
  
  const itr = document.querySelector('#itr-out').value;
  const message = document.querySelector('#message-out').value;
  const confidence = document.querySelector('#confidence').value;
  
  // Send data to the backend
  fetch('/receive', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ itr, message, confidence }),
  })
  .then(response => response.json())
  .then(data => {
      // Display the result in the output box
      outputBox.value = data.result;

      downloadButton.style.display = 'block'; // Show the download button
  })
  .catch((error) => {
      console.error('Error:', error);
  });
    
    outForm.reset();
});

downloadButton.addEventListener('click', () => {
  // Create a timestamp string in the format yyyyMMddHHmmss
  const timestamp = new Date().toISOString().replace(/[^0-9]/g, '');

  // Create a filename with the timestamp
  const filename = `result_${timestamp}.txt`;

  // Trigger the download with the updated filename
  const blob = new Blob([outputBox.value], { type: 'text/plain' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
});


const resetDataButton = document.querySelector('#reset-data-button');
const resetModelButton = document.querySelector('#reset-model-button');

resetDataButton.addEventListener('click', () => {
    // Send a request to reset data route (/reset_data)
    fetch('/reset_data', { method: 'POST' })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
});

resetModelButton.addEventListener('click', () => {
    // Send a request to reset model route (/reset_model)
    fetch('/reset_model', { method: 'POST' })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
});