console.log("-Group page-")
console.log(group)
console.log(user)
console.log(admin)
console.log(extended)
console.log(users)
console.log(group_users)



const GROUP_FIELD = {
  "id": 0,
  "name": 1,
  "description": 2,
  "creator": 3,
  "users": 4,
  "usersNum": 5,
  "permLink": 6,
  "invited": 7,
  "public": 8,
}

add_information()
if (admin) { // only admin can invite users
  activate_invite_users()
  activate_remove_users()
}
activate_join_leave_button()


function activate_join_leave_button()
{
  if (extended)
    activate_leave_button()
  else
  {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/check-requested', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({'id': user[0], 'group': group[0]}));
    xhr.onreadystatechange = function() {
      if (xhr.readyState === 4 && xhr.status === 200) {
        var response = JSON.parse(xhr.responseText);
        if (response.message == true)
          activate_request_button()
        else 
          activate_join_button()
      }
    };

  }
}

function activate_leave_button()
{
  button = document.getElementById("join-leave-button");
  button.style.background = "rgb(119, 34, 34)";
  button.innerHTML = "Leave group";
  button.style.color = "white";
  button.onclick = function() { leave_group(button.id); };
}

function activate_join_button()
{
  console.log("What")
  button = document.getElementById("join-leave-button");
  button.style.background = "rgb(17, 136, 85)";
  button.innerHTML = "Join Group";
  button.style.color = "white";
  button.onclick = function() { join_group(button.id); };
}

function activate_request_button()
{
  button = document.getElementById("join-leave-button");
  button.style.background = "#349";
  button.innerHTML = "Requested";
  button.style.color = "white";
}

function leave_group()
{
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/leave-group', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({'id': user[0], 'group': group[0]}));
  activate_join_button()
}

function join_group()
{
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/join-group', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({'id': user[0], 'group': group[0]}));
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
      var response = JSON.parse(xhr.responseText);
      console.log(response.message == "Requested")
      console.log(response.message == "Joined")
      if (response.message == "Requested")
        activate_request_button()
      if (response.message == "Joined")
        activate_leave_button()
        window.location.reload();
    }
  };
}

function add_information()
{
  const basicInfo = document.getElementById("basic-info");

  const name_button_wrapper = document.createElement("div");
  name_button_wrapper.id = "name-button-wrapper"
  basicInfo.appendChild(name_button_wrapper);
  
  
  let info = document.createElement("h1");
  info.innerHTML = `${group[GROUP_FIELD['name']]}`;
  name_button_wrapper.appendChild(info);
  
  const join_leave_button = document.createElement("button");
  join_leave_button.id = "join-leave-button";
  name_button_wrapper.appendChild(join_leave_button);
  
  info = document.createElement("h2");
  info.innerHTML = `${group[GROUP_FIELD['description']]}`;
  
  basicInfo.appendChild(info);
  
  if(extended)
  {
    info = document.createElement("h2");
    info.innerHTML = `${group[GROUP_FIELD['usersNum']]} members`;
    basicInfo.appendChild(info);
  
  }
}

function activate_invite_users()
{
  const container = document.createElement("div");
  container.style.display = "flex";
  container.style.alignItems = "center";

  const searchInput = document.createElement("input");
  searchInput.type = "text";
  searchInput.id = "searchInput";

  const submitButton = document.createElement("button");
  submitButton.innerHTML = "Invite";
  submitButton.id = "submitButton";

  container.appendChild(searchInput);

  const buttonsContainer = document.getElementById("buttonsContainer");

  inviteContainer = document.createElement("div");
  inviteContainer.className = "invite-container";
  buttonsContainer.appendChild(inviteContainer);

  inviteContainer.appendChild(container);

  for (let curr_user in users) {
    const button = document.createElement("button");
    button.textContent = users[curr_user];
    button.classList.add("button");
    button.addEventListener("click", function() {
      this.classList.toggle("invite-selected");
    });
    button.dataset.id = curr_user;
    inviteContainer.appendChild(button);
  }
  inviteContainer.appendChild(submitButton);


  searchInput.addEventListener("input", function() {
    const inputValue = this.value.toLowerCase();
    const buttons = inviteContainer.querySelectorAll(".button");
    for (const button of buttons) {
      const buttonText = button.textContent.toLowerCase();
      if (buttonText.includes(inputValue)) {
        button.style.display = "block";
      } else {
        button.style.display = "none";
      }
    }
  });

  submitButton.addEventListener("click", function() {
    // Get the list of selected buttons
    const selectedButtons = document.querySelectorAll(".invite-selected");
    const selectedIds = [];
    for (const button of selectedButtons) {
      selectedIds.push(button.dataset.id);
    }

    // Send the list of selected buttons to the Flask function
    const formData = JSON.stringify({ ids: selectedIds });

    fetch(`/process_group_invite/${group[GROUP_FIELD['id']]}`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json"
      },
      body: formData
    })
      .then(response => response.json())
      .then(data => {
        console.log(data.message);
        const selectedButtons = document.querySelectorAll(".invite-selected");
        for (const button of selectedButtons) {
          button.remove();
          window.location.reload();
        }
      });
  });
}

function activate_remove_users()
{
  const container = document.createElement("div");
  container.style.display = "flex";
  container.style.alignItems = "center";

  const searchInput = document.createElement("input");
  searchInput.type = "text";
  searchInput.id = "searchInput";

  const submitButton = document.createElement("button");
  submitButton.innerHTML = "Remove";
  submitButton.id = "submitButton";

  container.appendChild(searchInput);

  const buttonsContainer = document.getElementById("buttonsContainer");
  removeContainer = document.createElement("div");
  removeContainer.className = "remove-container";
  buttonsContainer.appendChild(removeContainer);

  removeContainer.appendChild(container);

  for (let curr_user in group_users) {
    console.log(`curr user is ${group_users[curr_user]} and user entered is ${user[0]}`)
    if (curr_user == user[0])
      continue;
    const button = document.createElement("button");
    button.textContent = group_users[curr_user];
    button.classList.add("button");
    button.addEventListener("click", function() {
      this.classList.toggle("remove-selected");
    });
    button.dataset.id = curr_user;
    removeContainer.appendChild(button);
  }

  removeContainer.appendChild(submitButton);

  searchInput.addEventListener("input", function() {
    const inputValue = this.value.toLowerCase();
    const buttons = removeContainer.querySelectorAll(".button");
    for (const button of buttons) {
      const buttonText = button.textContent.toLowerCase();
      if (buttonText.includes(inputValue)) {
        button.style.display = "block";
      } else {
        button.style.display = "none";
      }
    }
  });

  submitButton.addEventListener("click", function() {
    // Get the list of selected buttons
    const selectedButtons = document.querySelectorAll(".remove-selected");
    const selectedIds = [];
    for (const button of selectedButtons) {
      selectedIds.push(button.dataset.id);
    }

    // Send the list of selected buttons to the Flask function
    const formData = JSON.stringify({ ids: selectedIds });

    fetch(`/process_group_removal/${group[GROUP_FIELD['id']]}`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json"
      },
      body: formData
    })
      .then(response => response.json())
      .then(data => {
        console.log(data.message);
        const selectedButtons = document.querySelectorAll(".remove-selected");
        for (const button of selectedButtons) {
          button.remove();
          window.location.reload();
        }
      });
  });
}
