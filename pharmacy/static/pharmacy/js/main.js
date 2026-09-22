/* =========================================================
   MEDICARE - MAIN JAVASCRIPT
   No browser alert() popups.
   Messages are shown inside the page.
========================================================= */


/* =========================================================
   CSRF COOKIE
========================================================= */

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }

    return cookieValue;
}


/* =========================================================
   PAGE MESSAGE
========================================================= */

function showPageMessage(message, type = "error", elementId = "message") {

    const messageElement = document.getElementById(elementId);

    if (!messageElement) {
        console.log(message);
        return;
    }

    messageElement.textContent = message;
    messageElement.className = "page-message " + type;

    messageElement.style.display = "block";

    clearTimeout(messageElement.messageTimer);

    messageElement.messageTimer = setTimeout(function () {
        messageElement.style.display = "none";
    }, 4000);
}


/* =========================================================
   LOGIN
========================================================= */

const loginButton = document.getElementById("loginButton");

if (loginButton) {

    loginButton.addEventListener("click", function () {

        const usernameElement =
            document.getElementById("username");

        const passwordElement =
            document.getElementById("password");

        const message =
            document.getElementById("message");

        const buttonText =
            document.getElementById("loginButtonText");

        const username =
            usernameElement
                ? usernameElement.value.trim()
                : "";

        const password =
            passwordElement
                ? passwordElement.value
                : "";


        if (message) {
            message.textContent = "";
            message.className = "page-message";
            message.style.display = "none";
        }


        if (username === "") {

            showPageMessage(
                "Please enter your username.",
                "error"
            );

            return;
        }


        if (password === "") {

            showPageMessage(
                "Please enter your password.",
                "error"
            );

            return;
        }


        loginButton.disabled = true;

        if (buttonText) {
            buttonText.textContent = "Signing In...";
        }


        fetch("/login-user/", {

            method: "POST",

            headers: {
                "Content-Type":
                    "application/x-www-form-urlencoded",

                "X-CSRFToken":
                    getCookie("csrftoken")
            },

            body: new URLSearchParams({
                username: username,
                password: password
            })
        })

        .then(function (response) {

            if (!response.ok) {
                throw new Error(
                    "Server returned " + response.status
                );
            }

            return response.json();
        })

        .then(function (data) {

            if (data.success) {

                showPageMessage(
                    data.message || "Login successful.",
                    "success"
                );

                if (buttonText) {
                    buttonText.textContent =
                        "Login Successful";
                }


                setTimeout(function () {

                    window.location.href =
                        data.redirect;

                }, 500);


            } else {

                showPageMessage(
                    data.message ||
                    "Invalid username or password.",
                    "error"
                );

                loginButton.disabled = false;

                if (buttonText) {
                    buttonText.textContent =
                        "Sign In";
                }
            }
        })

        .catch(function (error) {

            console.error(
                "Login error:",
                error
            );

            showPageMessage(
                "Unable to connect to the server. Please try again.",
                "error"
            );

            loginButton.disabled = false;

            if (buttonText) {
                buttonText.textContent =
                    "Sign In";
            }
        });

    });
}


/* =========================================================
   ADD MEDICINE
========================================================= */

const saveMedicineButton =
    document.getElementById("saveMedicineButton");

const addMedicineButton =
    document.getElementById("addMedicineButton");


const activeAddButton =
    saveMedicineButton ||
    addMedicineButton;


if (activeAddButton) {

    activeAddButton.addEventListener(
        "click",
        function () {

            const nameElement =
                document.getElementById("addName") ||
                document.getElementById("name");

            const categoryElement =
                document.getElementById("addCategory") ||
                document.getElementById("category");

            const manufactureDateElement =
                document.getElementById("addManufactureDate") ||
                document.getElementById("manufacture_date");

            const expiryDateElement =
                document.getElementById("addExpiryDate") ||
                document.getElementById("expiry_date");

            const priceElement =
                document.getElementById("addPrice") ||
                document.getElementById("price");

            const countElement =
                document.getElementById("addCount") ||
                document.getElementById("count");


            const message =
                document.getElementById(
                    "addMedicineMessage"
                ) ||
                document.getElementById("message");


            const name =
                nameElement
                    ? nameElement.value.trim()
                    : "";

            const category =
                categoryElement
                    ? categoryElement.value.trim()
                    : "";

            const manufactureDate =
                manufactureDateElement
                    ? manufactureDateElement.value
                    : "";

            const expiryDate =
                expiryDateElement
                    ? expiryDateElement.value
                    : "";

            const price =
                priceElement
                    ? priceElement.value
                    : "";

            const count =
                countElement
                    ? countElement.value
                    : "";


            if (
                name === "" ||
                category === "" ||
                manufactureDate === "" ||
                expiryDate === "" ||
                price === "" ||
                count === ""
            ) {

                showPageMessage(
                    "Please fill all fields.",
                    "error",
                    message
                        ? message.id
                        : "message"
                );

                return;
            }


            if (
                expiryDate <=
                manufactureDate
            ) {

                showPageMessage(
                    "Expiry date must be after manufacture date.",
                    "error",
                    message
                        ? message.id
                        : "message"
                );

                return;
            }


            if (
                parseFloat(price) < 0
            ) {

                showPageMessage(
                    "Price cannot be negative.",
                    "error",
                    message
                        ? message.id
                        : "message"
                );

                return;
            }


            if (
                parseInt(count) < 0
            ) {

                showPageMessage(
                    "Count cannot be negative.",
                    "error",
                    message
                        ? message.id
                        : "message"
                );

                return;
            }


            activeAddButton.disabled = true;

            activeAddButton.innerHTML =
                "Adding...";


            fetch("/add-medicine/", {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/x-www-form-urlencoded",

                    "X-CSRFToken":
                        getCookie("csrftoken")
                },

                body: new URLSearchParams({

                    name: name,

                    category: category,

                    manufacture_date:
                        manufactureDate,

                    expiry_date:
                        expiryDate,

                    price: price,

                    count: count
                })
            })

            .then(function (response) {

                if (!response.ok) {
                    throw new Error(
                        "Server returned " +
                        response.status
                    );
                }

                return response.json();
            })

            .then(function (data) {

                if (data.success) {

                    showPageMessage(
                        data.message ||
                        "Medicine added successfully!",
                        "success",
                        message
                            ? message.id
                            : "message"
                    );


                    if (nameElement) {
                        nameElement.value = "";
                    }

                    if (categoryElement) {
                        categoryElement.value = "";
                    }

                    if (manufactureDateElement) {
                        manufactureDateElement.value = "";
                    }

                    if (expiryDateElement) {
                        expiryDateElement.value = "";
                    }

                    if (priceElement) {
                        priceElement.value = "";
                    }

                    if (countElement) {
                        countElement.value = "";
                    }


                    setTimeout(function () {

                        window.location.reload();

                    }, 900);


                } else {

                    showPageMessage(
                        data.message ||
                        "Unable to add medicine.",
                        "error",
                        message
                            ? message.id
                            : "message"
                    );

                    activeAddButton.disabled =
                        false;

                    activeAddButton.innerHTML =
                        "Add Medicine";
                }
            })

            .catch(function (error) {

                console.error(
                    "Add medicine error:",
                    error
                );

                showPageMessage(
                    "Something went wrong while adding the medicine.",
                    "error",
                    message
                        ? message.id
                        : "message"
                );

                activeAddButton.disabled =
                    false;

                activeAddButton.innerHTML =
                    "Add Medicine";
            });

        }
    );
}


/* =========================================================
   DELETE MEDICINE
========================================================= */

document
    .querySelectorAll(".delete-medicine")
    .forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                const medicineId =
                    this.dataset.id;


                /*
                   IMPORTANT:
                   No browser confirm() popup.

                   Delete happens directly after
                   clicking Delete.
                */


                const messageElement =
                    document.getElementById(
                        "medicineMessage"
                    ) ||
                    document.getElementById(
                        "message"
                    );


                button.disabled = true;

                button.dataset.originalText =
                    button.innerHTML;

                button.innerHTML =
                    "Deleting...";


                fetch(
                    `/delete-medicine/${medicineId}/`,
                    {
                        method: "POST",

                        headers: {
                            "X-CSRFToken":
                                getCookie("csrftoken")
                        }
                    }
                )

                .then(function (response) {

                    if (!response.ok) {
                        throw new Error(
                            "Server error: " +
                            response.status
                        );
                    }

                    return response.json();
                })

                .then(function (data) {

                    if (data.success) {

                        showPageMessage(
                            data.message ||
                            "Medicine deleted successfully.",
                            "success",
                            messageElement
                                ? messageElement.id
                                : "message"
                        );


                        setTimeout(function () {

                            window.location.reload();

                        }, 700);


                    } else {

                        showPageMessage(
                            data.message ||
                            "Unable to delete medicine.",
                            "error",
                            messageElement
                                ? messageElement.id
                                : "message"
                        );

                        button.disabled =
                            false;

                        button.innerHTML =
                            button.dataset.originalText;
                    }

                })

                .catch(function (error) {

                    console.error(
                        "Delete error:",
                        error
                    );

                    showPageMessage(
                        "Something went wrong while deleting the medicine.",
                        "error",
                        messageElement
                            ? messageElement.id
                            : "message"
                    );

                    button.disabled =
                        false;

                    button.innerHTML =
                        button.dataset.originalText;
                });

            }
        );

    });


/* =========================================================
   UPDATE MEDICINE
========================================================= */

const updateMedicineButton =
    document.getElementById(
        "updateMedicineButton"
    );


if (updateMedicineButton) {

    updateMedicineButton.addEventListener(
        "click",
        function () {

            const medicineId =
                this.dataset.id;


            const nameElement =
                document.getElementById("name");

            const categoryElement =
                document.getElementById("category");

            const manufactureDateElement =
                document.getElementById(
                    "manufacture_date"
                );

            const expiryDateElement =
                document.getElementById(
                    "expiry_date"
                );

            const priceElement =
                document.getElementById("price");

            const countElement =
                document.getElementById("count");

            const message =
                document.getElementById("message");


            const name =
                nameElement.value.trim();

            const category =
                categoryElement.value.trim();

            const manufactureDate =
                manufactureDateElement.value;

            const expiryDate =
                expiryDateElement.value;

            const price =
                priceElement.value;

            const count =
                countElement.value;


            if (
                name === "" ||
                category === "" ||
                manufactureDate === "" ||
                expiryDate === "" ||
                price === "" ||
                count === ""
            ) {

                showPageMessage(
                    "Please fill all fields.",
                    "error"
                );

                return;
            }


            if (
                expiryDate <=
                manufactureDate
            ) {

                showPageMessage(
                    "Expiry date must be after manufacture date.",
                    "error"
                );

                return;
            }


            if (
                parseFloat(price) < 0
            ) {

                showPageMessage(
                    "Price cannot be negative.",
                    "error"
                );

                return;
            }


            if (
                parseInt(count) < 0
            ) {

                showPageMessage(
                    "Count cannot be negative.",
                    "error"
                );

                return;
            }


            updateMedicineButton.disabled =
                true;

            updateMedicineButton.innerHTML =
                "Updating...";


            fetch(
                `/edit-medicine/${medicineId}/`,
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/x-www-form-urlencoded",

                        "X-CSRFToken":
                            getCookie("csrftoken")
                    },

                    body: new URLSearchParams({

                        name: name,

                        category: category,

                        manufacture_date:
                            manufactureDate,

                        expiry_date:
                            expiryDate,

                        price: price,

                        count: count
                    })
                }
            )

            .then(function (response) {

                if (!response.ok) {
                    throw new Error(
                        "Server returned " +
                        response.status
                    );
                }

                return response.json();
            })

            .then(function (data) {

                if (data.success) {

                    showPageMessage(
                        data.message ||
                        "Medicine updated successfully!",
                        "success"
                    );


                    setTimeout(function () {

                        window.location.href =
                            "/admin-dashboard/";

                    }, 900);


                } else {

                    showPageMessage(
                        data.message ||
                        "Unable to update medicine.",
                        "error"
                    );

                    updateMedicineButton.disabled =
                        false;

                    updateMedicineButton.innerHTML =
                        "Update Medicine";
                }

            })

            .catch(function (error) {

                console.error(
                    "Update medicine error:",
                    error
                );

                showPageMessage(
                    "Something went wrong while updating the medicine.",
                    "error"
                );

                updateMedicineButton.disabled =
                    false;

                updateMedicineButton.innerHTML =
                    "Update Medicine";
            });

        }
    );
}