const API_URL = "http://127.0.0.1:8000";


async function signup() {

    const username = document.getElementById("username").value;

    const email = document.getElementById("email").value;

    const password = document.getElementById("password").value;

    const message = document.getElementById("message");


    if (username === "" || email === "" || password === "") {

        message.style.color = "red";
        message.innerHTML = "Please fill all fields.";
        return;

    }


    try {

        const response = await fetch(

            API_URL + "/users/",

            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    username: username,
                    email: email,
                    password: password
                })
            }

        );


        const data = await response.json();


        if (response.ok) {

            message.style.color = "green";
            message.innerHTML = "Account created successfully! Redirecting to login...";

            setTimeout(() => {
                window.location.href = "login.html";
            }, 1200);

        }
        else {

            message.style.color = "red";
            message.innerHTML = data.detail || "Signup failed. Please try again.";

        }

    }

    catch (error) {

        console.error(error);
        message.style.color = "red";
        message.innerHTML = error.message;

    }

}
