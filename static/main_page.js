console.log("-Main page-")
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
        
            formElement.appendChild(optionElement);
            option_num++;
        }
        var button = document.createElement("button");
        button.setAttribute("id", `button_${poll_id}`)
        button.className = "btn"
        button.setAttribute("type", "submit");
        button.innerHTML = "Submit";
        formElement.appendChild(button);

        select.appendChild(formElement)
    }
}

function createVotingCanvas(form_id, optionValues, selectedOption) 
{
    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext("2d");

    canvas.width = 500;
    canvas.height = optionValues.length * 50 - 10;
    var totalVotes = 0
    console.log(`optionsVal are ${optionValues}`)
    for (const option of optionValues)
    {
        totalVotes+=parseInt(option);
    }
    console.log(`total votes are ${totalVotes}`)

    // Set the bar width and spacing
    var barHeight = 40;
    var barSpacing = 10;

    for(var i = 0; i < optionValues.length; i++) {
        // Calculate the width of the bar as a proportion of the maximum value
        var barWidth = (optionValues[i] / totalVotes) * canvas.width;
    
        // Set the x position of the bar
        var x = 0;
    
        // Set the y position of the bar
        var y = i * (barHeight + barSpacing);
        
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
        ctx.fillText(percentage + "%", 500, y + barHeight/1.5);
    }
    return canvas;
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
                console.log(data.message)
                var button = document.getElementById(`button_${form.id}`);
                button.remove();
                console.log(`submit button removed for ${form.id}`)
                var curr_form = document.getElementById(form.id);
                var radios = curr_form.querySelectorAll('input[name="radar-option"]');
                radios.forEach(function(radio) {
                  radio.disabled = true;
                });
                console.log(data.optionValues)
                console.log(data.selectedOption)
                curr_form.appendChild(createVotingCanvas(form.id, data.optionValues, data.selectedOption))
                // TODO - decide on design and make sure the conversion between poll vote view to discussion view is good
            });

    });
});

}