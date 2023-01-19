console.log("-Main page-")
console.log(voted)
poll_view(polls)
submit_poll_option()

function poll_view(polls)
{
    // get the select element
    var select = document.getElementById('form_wrapper');
  
    // create forms
    for (var i = 0; i < polls.length; i++)
    {
        const formElement = document.createElement("form");
        formElement.classList.add("radar-form");

        formElement.setAttribute("method", "post");
        var poll_id = polls[i][0]
        formElement.id = `${poll_id}`
        formElement.setAttribute("action", `/process_poll_vote/${poll_id}`);

        var poll_name = polls[i][3]
        const titleElement = document.createElement("h1");
        titleElement.textContent = poll_name;
        formElement.appendChild(titleElement);

        const poll_description = polls[i][5]
        if (poll_description)
            var descriptionElement = document.createElement("p");
            descriptionElement.textContent = poll_description;
            formElement.appendChild(descriptionElement);

        // creating first div which will hold canvas and option div
        const formDiv = document.createElement("div");
        formDiv.id = `div_${poll_id}`
        //formDiv.setAttribute("position", "relative")
        formDiv.style.position = "relative";
        formElement.appendChild(formDiv);

        // creating second div which will hold options
        const optionDiv = document.createElement("div");
        optionDiv.id = `option_${poll_id}`;
        //optionDiv.style.position = "absolute";
        //optionDiv.style.width = "100%";
        //optionDiv.style.height = "100%";
        formDiv.appendChild(optionDiv);

        var poll_options = polls[i][6].split(',')
        option_num = 0
        for (const option of poll_options) 
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
            radioElement.value = `${option_num}`;
            radioElement.id = `${poll_id}_${option}`;
            console.log(`yo, option is: ${radioElement.id}`);
            optionElement.appendChild(radioElement);
        
            const labelElement = document.createElement("label");
            labelElement.htmlFor = `${poll_id}_${option}`;
            optionElement.appendChild(labelElement);
        
            optionDiv.appendChild(optionElement);
            option_num++;
        }
        var button = document.createElement("button");
        button.setAttribute("id", `button_${poll_id}`)
        button.className = "btn"
        button.setAttribute("type", "submit");
        button.innerHTML = "Submit";
        formElement.appendChild(button);
        select.appendChild(formElement)
        // TODO - start here
        // if(voted.includes(poll_id))
        // {
        //     var a = 1 
        //     //select option of radar with the voted option
        //     //call the voted_for_poll with form_id, optionValues, selected
        // }
    }
}

function createVotingCanvas(optionValues, selectedOption) 
{
    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext("2d");

    canvas.width = 650;
    canvas.height = optionValues.length * 51;
    var totalVotes = 0
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
            ctx.fillStyle = "#888E91"
        }
        else
        {
            ctx.fillStyle = "#CFD9DE"
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
    canvas.style.position = "absolute"
    canvas.style.zIndex = "-1"
    return canvas;
}

function voted_for_poll(form_id, optionValues, selectedOption)
{
    var button = document.getElementById(`button_${form_id}`);
    button.remove();
    console.log(`submit button removed for ${form_id}`)
    var curr_form = document.getElementById(form_id);
    var curr_form_div = document.getElementById(`div_${form_id}`);
    var curr_option_div = document.getElementById(`option_${form_id}`);
    var radios = curr_form.querySelectorAll('input[name="radar-option"]');
    radios.forEach(function(radio) 
    {
        radio.disabled = true;
    });
    curr_form_div.insertBefore(createVotingCanvas(optionValues, selectedOption), curr_option_div);
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