console.log("-Main page-")
console.log(id)
console.log(username)
console.log(groups)
console.log(voted)
console.log(notifications)

POLL_FIELD = {
    "id": 0,
    "startTime": 1,
    "creator": 2,
    "title": 3,
    "group": 4,
    "description": 5,
    "optionNames": 6,
    "optionValues": 7,
    "idVoted": 8,
    "duration": 9,
}

NOTIFICATIONS_FIELD = {
    "id": 0,
    "time": 1,
    "category": 2,
    "initiator": 3,
    "group": 4,
    "initiator_name": 5,
    "group_name": 6,
}

poll_view(polls)
submit_poll_option()
show_groups()
show_notifications()
activate_search_button()

function poll_view(polls)
{
    // get the select element
    var select = document.getElementById('votes-wrapper');
  
    // create forms
    for (var i = 0; i < polls.length; i++)
    {
        const formElement = document.createElement("form");
        formElement.classList.add("radar-form");

        formElement.setAttribute("method", "post");
        var poll_id = polls[i][0]
        formElement.id = `${poll_id}`
        formElement.setAttribute("action", `/process_poll_vote/${poll_id}`);

        var pollName = polls[i][3]
        const titleElement = document.createElement("h1");
        titleElement.textContent = pollName;
        formElement.appendChild(titleElement);

        const poll_description = polls[i][5]
        if (poll_description)
            var descriptionElement = document.createElement("p");
            descriptionElement.textContent = poll_description;
            formElement.appendChild(descriptionElement);

        // creating first div which will hold canvas and option div
        const formDiv = document.createElement("div");
        formDiv.id = `div_${poll_id}`
        formDiv.style.position = "relative";
        formElement.appendChild(formDiv);

        const optionDiv = document.createElement("div");
        optionDiv.id = `option_${poll_id}`;
        formDiv.appendChild(optionDiv);

        var pollOptions = polls[i][6].split(',');
        optionNum = 0;
        for (const option of pollOptions) 
        {
            const optionElement = document.createElement("div");
            optionElement.classList.add("option"); 
        
            const optionDescriptionElement = document.createElement("p");
            optionDescriptionElement.classList.add("option-description");
            optionDescriptionElement.textContent = option;
            optionElement.appendChild(optionDescriptionElement);
        
            const radioElement = document.createElement("input");
            radioElement.type = "radio";
            radioElement.name = "radar-option";
            radioElement.value = `${optionNum}`;
            radioElement.id = `${poll_id}_${option}`;
            console.log(`yo, option is: ${radioElement.id}`);
            optionElement.appendChild(radioElement);
        
            const labelElement = document.createElement("label");
            labelElement.htmlFor = `${poll_id}_${option}`;
            optionElement.appendChild(labelElement);
        
            optionDiv.appendChild(optionElement);
            optionNum++;
        }
        var button = document.createElement("button");
        button.setAttribute("id", `button_${poll_id}`);
        button.className = "btn";
        button.setAttribute("type", "submit");
        button.innerHTML = "Vote";
        formElement.appendChild(button);
        select.appendChild(formElement);
        console.log(`${poll_id}`);
        if (`${poll_id}` in voted)
        {
            var optionValues = polls[i][7].split(',');
            console.log(`values are ${pollOptions} and ${typeof(optionValues)}`);

            voted_for_poll(poll_id, optionValues, voted[`${poll_id}`]);
        }
    }
}

function create_voting_canvas(optionValues, selectedOption) 
{
    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext("2d");

    canvas.width = 650;
    canvas.height = optionValues.length * 51;
    var totalVotes = 0;
    console.log(`optionsVal are ${optionValues}`)
    for (const option of optionValues)
    {
        totalVotes+=parseInt(option);
    }
    console.log(`total votes are ${totalVotes}`)

    // Set the bar width and spacing
    var barHeight = 41;
    var barSpacing = 10;

    for(var i = 0; i < optionValues.length; i++) {
        // Calculate the width of the bar as a proportion of the maximum value
        var barWidth = (optionValues[i] / totalVotes) * canvas.width;
    
        // Set the x position of the bar
        var x = 30;
    
        // Set the y position of the bar
        var y = i * (barHeight + barSpacing + 0.1) + 5;
        
        // Draw the bar on the canvas
        
        if(i == parseInt(selectedOption))
        {
            ctx.fillStyle = "#888E91";
        }
        else
        {
            ctx.fillStyle = "#CFD9DE";
        }
        ctx.fillRect(x, y, barWidth, barHeight);
        
        // Calculate the percentage
        var percentage = ((optionValues[i] / totalVotes) * 100).toFixed(2);
        
        // Set the font style and size for the text
        ctx.font = "20px Arial";
        
        // Draw the text next to the bar
        ctx.fillStyle = "black";
        ctx.textAlign = "right";
        ctx.fillText(percentage + "%", 650, y + barHeight/1.5);
    }
    canvas.style.position = "absolute";
    canvas.style.zIndex = "-1";
    return canvas;
}

function voted_for_poll(form_id, optionValues, selectedOption)
{
    var button = document.getElementById(`button_${form_id}`);
    button.remove();
    console.log(`submit button removed for ${form_id}`);
    var currForm = document.getElementById(form_id);
    var currFormDiv = document.getElementById(`div_${form_id}`);
    var currOptionDiv = document.getElementById(`option_${form_id}`);
    var radios = currForm.querySelectorAll('input[name="radar-option"]');
    var radioIndex = 0;
    radios.forEach(function(radio) 
    {
        radio.disabled = true;
        if(radioIndex == selectedOption)
            radio.checked = true;
        radioIndex++;
    });
    currFormDiv.insertBefore(create_voting_canvas(optionValues, selectedOption), currOptionDiv);
}

function submit_poll_option()
{
    var cookies = document.cookie.split(';');
    console.log(cookies)
    const forms = document.querySelectorAll("form")
    forms.forEach(form => {
        console.log(`form loop id is ${form.id}`)
        form.addEventListener("submit", function(event){
            event.preventDefault();
            var formData = new FormData(this);
            fetch(`/process_poll_vote/${form.id}`, {
                method: 'POST',
                credentials: 'include',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                voted_for_poll(form.id, data.optionValues, data.selectedOption); 
            });
        });
    });
}

function show_all_groups()
{
    for (var i in polls){
        const curr_poll_id = polls[i][POLL_FIELD['id']]
        const curr_poll_element = document.getElementById(curr_poll_id);
        curr_poll_element.style.display = "block";
    }
}

function filter_groups(id)
{
    console.log(id)
    for (var i in polls){
        const curr_poll_id = polls[i][POLL_FIELD['id']]
        const curr_poll_element = document.getElementById(curr_poll_id);
        if(polls[i][POLL_FIELD['group']] == id)
        {
            curr_poll_element.style.display = "block";
        }
        else 
        {
            curr_poll_element.style.display = "none";
        }
    }
}


function show_groups()
{
    // get the select element
    var select = document.getElementById('groups-wrapper');

    // create the "explore" button, which shows all polls
    const all_groups_button = document.createElement("button");
    all_groups_button.innerHTML = "Explore";
    all_groups_button.id = "explore-button"
    all_groups_button.className = "group-button";
    all_groups_button.onclick = function() { show_all_groups(); };
    select.appendChild(all_groups_button)

    // create group buttons
    for (var id in groups){
        console.log(id, groups[id]);

        const button = document.createElement("button");
        button.innerHTML = groups[id];
        button.id = id
        button.className = "group-button";
        button.onclick = function() { filter_groups(button.id); };
        select.appendChild(button);
    }

    // create "add new group" button
    const new_group_button = document.createElement("button");
    new_group_button.innerHTML = "+";
    new_group_button.id = "new-group-button"
    new_group_button.className = "group-button";
    new_group_button.onclick = function () {
    location.href = create_poll_url;
    };
    select.appendChild(new_group_button)
}

function create_link(id, name, type) {
    // Create a new anchor element
    const link = document.createElement("a");
  
    // Set the href attribute to the Flask route with the given ID
    link.href = `/${type}/${id}`;
  
    // Set the text content of the anchor element
    link.textContent = `${name}`;
  
    // Return the anchor element
    return link;
  }

function create_notification_msg_element(notification)
{
    group_link = create_link(notification[NOTIFICATIONS_FIELD['group']], notification[NOTIFICATIONS_FIELD["group_name"]], "group")
    user_link = create_link(notification[NOTIFICATIONS_FIELD['initiator']], notification[NOTIFICATIONS_FIELD["initiator_name"]], "user")
    // Combine the elements into a single string
    var combinedString = ""
    console.log(notification[NOTIFICATIONS_FIELD['category']])
    if(notification[NOTIFICATIONS_FIELD['category']] == "invitation")
        combinedString = `${user_link.outerHTML} has invited you to join “${group_link.outerHTML}” group`;
    // Create a new h3 element
    const notification_msg_element = document.createElement('h3');
    notification_msg_element.innerHTML = combinedString;
    
    return notification_msg_element

}

function notification_handler(user_id, group_id, choice, notification_element)
{
    notification_element.remove()
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/handle-invite-notification', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({'id': user_id, 'group': group_id, 'choice': choice}));
    window.location.reload();
}

function get_notification_element(notification)
{
    console.log(notification);
    console.log("notif");
    
    const notification_element = document.createElement("div");
    notification_element.className = "notification"
    const accept_button = document.createElement("button");
    accept_button.innerHTML = "Accept"
    accept_button.className = "accept-button";
    accept_button.onclick = function() { notification_handler(notification[NOTIFICATIONS_FIELD['id']], notification[NOTIFICATIONS_FIELD['group']], true, notification_element); };

    const decline_button = document.createElement("button");
    decline_button.className = "decline-button";
    decline_button.innerHTML = "Decline"
    decline_button.onclick = function() { notification_handler(notification[NOTIFICATIONS_FIELD['id']], notification[NOTIFICATIONS_FIELD['group']], false, notification_element); };

    const notification_msg = create_notification_msg_element(notification);

    notification_element.appendChild(notification_msg);
    notification_element.appendChild(accept_button);
    notification_element.appendChild(decline_button);
    return notification_element;
}

function show_notifications()
{
    // get the select element
    const select = document.getElementById('notifications-wrapper');
    for (i in notifications)
    {
        const notification_element = get_notification_element(notifications[i])
        select.appendChild(notification_element)
    }
}

function search_handler(text)
{
    console.log("start search handler")
    for (var i in polls){
        const curr_poll_id = polls[i][POLL_FIELD['id']]
        const curr_poll_element = document.getElementById(curr_poll_id);
        if(text == "")
        {
            curr_poll_element.style.display = "block";
            continue;
        }
        console.log(curr_poll_element.style.display)
        if (curr_poll_element.style.display == "block" || curr_poll_element.style.display == "")
        {
            console.log(i)
            var poll_title = polls[i][POLL_FIELD['title']]
            if (poll_title.includes(text))
                continue;
            curr_poll_element.style.display = "none";
        }


        // curr_poll_element.style.display = "block";
    }    
    
    
    // var xhr = new XMLHttpRequest();
    // xhr.open('POST', '/search', true);
    // xhr.setRequestHeader('Content-Type', 'application/json');
    // xhr.send(JSON.stringify({'text': text}));
}

function activate_search_button()
{
    const search_button = document.getElementById('search-bar-icon');
    const search_content = document.getElementById('search-bar');
    document.addEventListener("keypress", function(event) {
      if (event.key === "Enter") {
        event.preventDefault();
        search_handler(search_content.value)
    }
    });
    search_button.onclick = function() { search_handler(search_content.value); };
}