document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('registerForm');
    const usernameInput = document.getElementById('id_username');
    const emailInput = document.getElementById('id_email');
    const password1Input = document.getElementById('id_password1');
    const password2Input = document.getElementById('id_password2');
    const usernameError = document.getElementById('id_username-error');
    const emailError = document.getElementById('id_email-error');
    const password1Error = document.getElementById('id_password1-error');
    const password2Error = document.getElementById('id_password2-error');
    const submitButton = document.getElementById('submitButton');

    if (!usernameInput) {
        console.error('Элемент с id="id_username" не найден');
        return;
    }
    if (!emailInput) {
        console.error('Элемент с id="id_email" не найден');
        return;
    }
    if (!password1Input) {
        console.error('Элемент с id="id_password1" не найден');
        return;
    }
    if (!password2Input) {
        console.error('Элемент с id="id_password2" не найден');
        return;
    }
    if (!usernameError || !emailError || !password1Error || !password2Error || !submitButton) {
        console.error('Один из элементов для ошибок или кнопка не найдены');
        return;
    }

    let isUsernameValid = false;
    let isEmailValid = false;
    let isPassword1Valid = false;
    let isPassword2Valid = false;

    function updateSubmitButton() {
        submitButton.disabled = !(isUsernameValid && isEmailValid && isPassword1Valid && isPassword2Valid);
    }

    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    usernameInput.addEventListener('input', debounce(function () {
        const username = usernameInput.value.trim();

        if (username.length < 3) {
            usernameError.textContent = 'Имя пользователя должно содержать минимум 3 символа';
            usernameError.classList.remove('validation-success');
            usernameError.classList.add('validation-error');
            isUsernameValid = false;
            updateSubmitButton();
            return;
        }

        fetch('/accounts/check-username/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ username: username })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.is_taken) {
                usernameError.textContent = 'Это имя пользователя уже занято';
                usernameError.classList.remove('validation-success');
                usernameError.classList.add('validation-error');
                isUsernameValid = false;
            } else {
                usernameError.textContent = 'Имя пользователя доступно';
                usernameError.classList.remove('validation-error');
                usernameError.classList.add('validation-success');
                isUsernameValid = true;
            }
            updateSubmitButton();
        })
        .catch(error => {
            console.error('Ошибка при проверке имени пользователя:', error);
            usernameError.textContent = 'Ошибка проверки имени пользователя';
            usernameError.classList.remove('validation-success');
            usernameError.classList.add('validation-error');
            isUsernameValid = false;
            updateSubmitButton();
        });
    }, 500));

    emailInput.addEventListener('input', debounce(function () {
        const email = emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(email)) {
            emailError.textContent = 'Введите корректный email';
            emailError.classList.remove('validation-success');
            emailError.classList.add('validation-error');
            isEmailValid = false;
            updateSubmitButton();
            return;
        }

        fetch('/accounts/check-email/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ email: email })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.is_taken) {
                emailError.textContent = 'Этот email уже зарегистрирован';
                emailError.classList.remove('validation-success');
                emailError.classList.add('validation-error');
                isEmailValid = false;
            } else {
                emailError.textContent = 'Email доступен';
                emailError.classList.remove('validation-error');
                emailError.classList.add('validation-success');
                isEmailValid = true;
            }
            updateSubmitButton();
        })
        .catch(error => {
            console.error('Ошибка при проверке email:', error);
            emailError.textContent = 'Ошибка проверки email';
            emailError.classList.remove('validation-success');
            emailError.classList.add('validation-error');
            isEmailValid = false;
            updateSubmitButton();
        });
    }, 500));

    password1Input.addEventListener('input', function () {
        const password = password1Input.value;
        const minLength = password.length >= 6;
        const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
        const hasLowerCase = /[a-z]/.test(password);
        const hasUpperCase = /[A-Z]/.test(password);

        if (!minLength) {
            password1Error.textContent = 'Пароль должен содержать минимум 6 символов';
            password1Error.classList.remove('validation-success');
            password1Error.classList.add('validation-error');
            isPassword1Valid = false;
        } else if (!hasSpecialChar) {
            password1Error.textContent = 'Пароль должен содержать минимум 1 спецсимвол';
            password1Error.classList.remove('validation-success');
            password1Error.classList.add('validation-error');
            isPassword1Valid = false;
        } else if (!hasLowerCase) {
            password1Error.textContent = 'Пароль должен содержать минимум 1 строчную букву';
            password1Error.classList.remove('validation-success');
            password1Error.classList.add('validation-error');
            isPassword1Valid = false;
        } else if (!hasUpperCase) {
            password1Error.textContent = 'Пароль должен содержать минимум 1 заглавную букву';
            password1Error.classList.remove('validation-success');
            password1Error.classList.add('validation-error');
            isPassword1Valid = false;
        } else {
            password1Error.textContent = 'Пароль соответствует требованиям';
            password1Error.classList.remove('validation-error');
            password1Error.classList.add('validation-success');
            isPassword1Valid = true;
        }

        const password2 = password2Input.value;
        if (password2 && password !== password2) {
            password2Error.textContent = 'Пароли не совпадают';
            password2Error.classList.remove('validation-success');
            password2Error.classList.add('validation-error');
            isPassword2Valid = false;
        } else if (password2) {
            password2Error.textContent = 'Пароли совпадают';
            password2Error.classList.remove('validation-error');
            password2Error.classList.add('validation-success');
            isPassword2Valid = true;
        }
        updateSubmitButton();
    });

    password2Input.addEventListener('input', function () {
        const password1 = password1Input.value;
        const password2 = password2Input.value;

        if (!password2) {
            password2Error.textContent = 'Подтвердите пароль';
            password2Error.classList.remove('validation-success');
            password2Error.classList.add('validation-error');
            isPassword2Valid = false;
        } else if (password1 !== password2) {
            password2Error.textContent = 'Пароли не совпадают';
            password2Error.classList.remove('validation-success');
            password2Error.classList.add('validation-error');
            isPassword2Valid = false;
        } else {
            password2Error.textContent = 'Пароли совпадают';
            password2Error.classList.remove('validation-error');
            password2Error.classList.add('validation-success');
            isPassword2Valid = true;
        }
        updateSubmitButton();
    });

    form.addEventListener('submit', function (event) {
        if (!isUsernameValid || !isEmailValid || !isPassword1Valid || !isPassword2Valid) {
            event.preventDefault();
            alert('Пожалуйста, исправьте ошибки в форме перед отправкой.');
        }
    });
});