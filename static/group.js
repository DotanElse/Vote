console.log("-Group page-")
console.log(group)
console.log(user)
console.log(admin)
console.log(extended)
console.log(users)

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
  const extendedInfo = document.getElementById("extended-info");
  info = document.createElement("h2");
  info.innerHTML = `This group have ${group[GROUP_FIELD['usersNum']]} members`;
  extendedInfo.appendChild(info);
}

if (admin) { // only admin can invite users
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
  container.appendChild(submitButton);

  const buttonsContainer = document.getElementById("buttonsContainer");
  buttonsContainer.appendChild(container);

  for (let user in users) {
    const button = document.createElement("button");
    button.textContent = users[user];
    button.classList.add("button");
    button.addEventListener("click", function() {
      this.classList.toggle("selected");
    });
    button.dataset.id = user;
    buttonsContainer.appendChild(button);
  }

  searchInput.addEventListener("input", function() {
    const inputValue = this.value.toLowerCase();
    const buttons = buttonsContainer.querySelectorAll(".button");
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
    const selectedButtons = document.querySelectorAll(".selected");
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
        const selectedButtons = document.querySelectorAll(".selected");
        for (const button of selectedButtons) {
          button.remove();
        }
      });
  });
}
