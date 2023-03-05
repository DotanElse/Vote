console.log("-Poll page-")
console.log(id)
console.log(poll)
console.log(voted)
single_poll_view(poll)
submit_poll_option()

function isEmpty(obj) {
    return Object.keys(obj).length === 0;
}

function single_poll_view(poll)
{
    // get the select element
    var select = document.getElementById('form_wrapper');
  
    // create form
    const formElement = document.createElement("form");
    formElement.classList.add("radar-form");

    formElement.setAttribute("method", "post");
    var poll_id = poll[0]
    formElement.id = `${poll_id}`
    formElement.setAttribute("action", `/process_poll_vote/${poll_id}`);

    var pollName = poll[3]
    const titleElement = document.createElement("h1");
    titleElement.textContent = pollName;
    formElement.appendChild(titleElement);

    const poll_description = poll[5];
    if (poll_description)
        console.log(poll_description);
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

    var pollOptions = poll[6].split(',');
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
    button.innerHTML = "Submit";
    formElement.appendChild(button);
    select.appendChild(formElement);
    console.log(`${poll_id}`);
    console.log(`voted is ${voted}`)
    console.log(id)
    if (!isEmpty(voted) || id==null)
    {
        var optionValues = poll[7].split(',');
        console.log(`values are ${pollOptions} and ${typeof(optionValues)}`);

        voted_for_poll(poll_id, optionValues, voted[`${poll_id}`]);
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