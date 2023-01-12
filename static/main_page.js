console.log("-Main page-")
poll_view(polls)

function poll_view(polls)
{
    console.log(polls)
    // get the select element
    var select = document.getElementById('form_wrapper');
  
    // create forms
    for (var i = 0; i < polls.length; i++) 
    {
        const formElement = document.createElement("form");
        formElement.classList.add("radar-form");

        formElement.setAttribute("method", "post");
        var poll_id = polls[i][0]
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
            radioElement.value = `${poll_id}${option}`;
            radioElement.id = `${poll_id}${option}`;
            console.log(`yo, option is: ${radioElement.id}`);
            optionElement.appendChild(radioElement);
        
            const labelElement = document.createElement("label");
            labelElement.htmlFor = `${poll_id}${option}`;
            optionElement.appendChild(labelElement);
        
            formElement.appendChild(optionElement);
        }
        var button = document.createElement("button");
        button.setAttribute("type", "submit");
        button.innerHTML = "Submit";
        formElement.appendChild(button);

        select.appendChild(formElement)
    }
}

function submit_pool_option()
{
    console.log("yosi")
}