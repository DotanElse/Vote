console.log("-User page-")
console.log(user)
console.log(is_owner)

const dateString = user[3]; // date string in "YYYY-MM-DD" format

// Split the string into an array using the (-) as a delimiter
const dateArray = dateString.split("-");

// Create a new date string in the "DD/MM/YYYY" format using template literals
const newDateString = `${dateArray[2]}-${dateArray[1]}-${dateArray[0]}`;

let birthday_paragraph = document.getElementById('profile-birthday');
birthday_paragraph.textContent = newDateString;
