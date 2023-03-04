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
const basicInfo = document.getElementById("basic-info");
let info = document.createElement("h1");
info.innerHTML = `${group[GROUP_FIELD['name']]}`;
basicInfo.appendChild(info);
info = document.createElement("h2");
info.innerHTML = `${group[GROUP_FIELD['description']]}`;
basicInfo.appendChild(info);

if(extended)
{
  info = document.createElement("h2");
  info.innerHTML = `${group[GROUP_FIELD['usersNum']]} members`;
  basicInfo.appendChild(info);
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

if (admin) { // only admin can invite users
  activate_invite_users()
  activate_remove_users()
}
