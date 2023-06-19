fetch('data.json')
  .then(response => response.json())
  .then(data => {
    displayJSON(data);
  })
  .catch(error => {
    console.error('Error:', error);
  });

console.log();