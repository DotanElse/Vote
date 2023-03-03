console.log("-Create poll-")
group_dropdown(groups)
activate_option_button()

function group_dropdown(groups)
{
    var choices = groups
    choices = choices.split(",");

    // get the select element
    var select = document.getElementById('group');
  
    // create options
    for (var i = 0; i < choices.length; i++) {
      var option = document.createElement('option');
      option.value = choices[i];
      option.text = choices[i];
      select.appendChild(option);
    }
}

function activate_option_button()
{
  const form = document.querySelector('#myForm');
  const optionsContainer = document.querySelector('#options-container');
  const addButton = document.querySelector('.add-option');
  
  let optionCount = 2;
  
  addButton.addEventListener('click', () => {
    if (optionCount >= 10) {
      return;
    }
  
    optionCount++;
  
    const newOption = document.createElement('input');
    newOption.type = 'text';
    newOption.name = 'option';
    newOption.classList.add('option');
  
    const newButton = document.createElement('button');
    newButton.type = 'button';
    newButton.classList.add('remove-option');
    newButton.textContent = '-';
  
    const newDiv = document.createElement('div');
    newDiv.appendChild(newOption);
    newDiv.appendChild(newButton);
  
    optionsContainer.insertBefore(newDiv, addButton);
  });
  
  optionsContainer.addEventListener('click', (event) => {
    if (event.target.matches('.remove-option')) {
      event.target.parentNode.remove();
      optionCount--;
    }
  });
}
