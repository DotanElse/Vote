console.log("-Create poll-")
group_dropdown(groups)

function group_dropdown(groups)
{
    var choices = groups
    choices = choices.split(",");

    // get the select element
    var select = document.getElementById('group');
  
    // create options
    for (var i = 0; i < choices.length; i++) {
      var option = document.createElement('option');
      option.value = choices[i].toLowerCase();
      option.text = choices[i];
      select.appendChild(option);
    }
}
