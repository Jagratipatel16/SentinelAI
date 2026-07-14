const API_URL = "http://127.0.0.1:8000";


async function login() {

    const email = document.getElementById("email").value;

    const password = document.getElementById("password").value;

    const message = document.getElementById("message");


    if (email === "" || password === "") {

        message.innerHTML = "Please fill all fields.";

        return;

    }


    const formData = new URLSearchParams();

    formData.append("username", email);

    formData.append("password", password);


    try {

        const response = await fetch(

            API_URL + "/auth/login",

            {

                method: "POST",

                headers: {

                    "Content-Type": "application/x-www-form-urlencoded"

                },

                body: formData

            }

        );


        const data = await response.json();


        if (response.ok) {

            localStorage.setItem(

                "access_token",

                data.access_token

            );

            message.style.color = "green";

            message.innerHTML = "Login Successful...";

            setTimeout(() => {

                window.location.href = "dashboard.html";

            }, 1000);

        }

        else {

            message.style.color = "red";

            message.innerHTML = data.detail;

        }

    }

catch (error) {

    console.error(error);

    message.style.color = "red";

    message.innerHTML = error.message;

}

}