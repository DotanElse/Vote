console.log("-Main page-")
group_dropdown(user)

function group_dropdown(user)
{
    var choices = user[4];
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
