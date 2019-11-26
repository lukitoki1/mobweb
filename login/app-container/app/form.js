const GET = "GET";
const POST = "POST";

const POL_VALID_REGEX = /^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$/;

// var approved = Array(9).fill(false)
var approved = {};
let form_elements = null

const init = function (event) {
    form_elements = document.getElementById("registration-form").elements
    Array.from(form_elements).forEach(function (obj) {
        id = obj.id;
        if (id != "button-reg-form") {
            approved[id] = false;
        }
    });

    document.getElementById("registration-form").addEventListener("submit", checkSubmitted);

    document.getElementById("firstname").addEventListener("change", checkName);
    document.getElementById("lastname").addEventListener("change", checkName);
    document.getElementById("birthdate").addEventListener("change", checkBirthDate);
    document.getElementById("pesel").addEventListener("change", checkPesel);
    document.getElementsByName("sex").forEach(function (obj) {
        obj.addEventListener("change", checkSex);
    })
    document.getElementById("login").addEventListener("change", checkLogin);
    document.getElementById("password").addEventListener("change", checkPassword);
    document.getElementById("repeat-password").addEventListener("change", checkRepeatPassword);
    document.getElementById("photo").addEventListener("change", checkPhoto);
};

function checkSubmitted(event) {
    event.preventDefault();

    Array.from(form_elements).forEach(function (obj) {
        checkFieldEmpty(obj);
    });

    if (!Object.values(approved).includes(false)) {
        document.getElementById("registration-form").submit();
    }
}

function checkFieldEmpty(name) {
    if (name.value == "") {
        showOrHideError(name, 'Pole nie może być puste.')
        return true;
    }
    if (name.type == "radio") {
        let buttons = document.querySelectorAll("input[type=radio]");
        if (!(buttons[0].checked || buttons[1].checked)) {
            approved[buttons[0].id] = false;
            approved[buttons[1].id] = false;
            buttons[0].parentElement.classList.add('error');
            buttons[0].parentElement.setAttribute('data-errormsg', 'Pole nie może być puste.');
            return true;
        }
    }
    return false;
}

function showOrHideError(name, error) {
    if (error == null) {
        approved[name.id] = true;
        name.parentElement.classList.remove('error');
    }
    else {
        approved[name.id] = false;
        name.parentElement.classList.add('error');
        name.parentElement.setAttribute('data-errormsg', error);
    }
}

function checkName() {
    let name = document.getElementById(event.target.id);
    if (POL_VALID_REGEX.test(name.value)) {
        showOrHideError(name)
    }
    else if (!checkFieldEmpty(name)) {
        showOrHideError(name, 'Pole musi zaczynać się dużą literą i kończyć małymi.')
    }
}

function checkBirthDate() {
    let name = document.getElementById(event.target.id);
    lowest_date = new Date("1900-01-01").getTime()
    date = new Date(name.value).getTime()

    if (date >= lowest_date) {
        showOrHideError(name)
    }
    else if (!checkFieldEmpty(name)) {
        showOrHideError(name, 'Minimalna data to: 01.01.1900.')
    }
}

function checkPesel() {
    let name = document.getElementById(event.target.id);

    if (countPeselChecksum(name.value)) {
        showOrHideError(name)
    }
    else if (!checkFieldEmpty(name)) {
        showOrHideError(name, 'Niepoprawny numer PESEL.')
    }
}

function countPeselChecksum(pesel) {
    let weight = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3];
    let sum = 0;
    let controlNumber = parseInt(pesel.substring(10, 11));
    for (let i = 0; i < weight.length; i++) {
        sum += (parseInt(pesel.substring(i, i + 1)) * weight[i]);
    }
    sum = sum % 10;
    return 10 - sum === controlNumber
}

function checkSex() {
    approved["sex-m"] = true;
    approved["sex-f"] = true;
    document.getElementById("sex-m").parentElement.classList.remove('error');
}

function checkLogin() {
    let name = document.getElementById(event.target.id);

    let loginInput = document.getElementById("login");
    let baseUrl = "https://pi.iem.pw.edu.pl/user/";
    let userUrl = baseUrl + loginInput.value;

    if (checkFieldEmpty(name)) {
        return;
    }
    if (!(/^[a-z]+$/.test(name.value))) {
        showOrHideError(name, 'Dozwolone są wyłącznie małe litery a-z.')
    }
    else if (name.value.length > 12) {
        showOrHideError(name, 'Login może mieć maksymalnie 12 znaków.')
    }
    else {
        fetch(userUrl, { method: GET }).then(function (resp) {
            checkLoginAsync(name, resp.status);
        }).catch(function (err) {
        });
    }
}

function checkLoginAsync(name, status) {
    if (status == '200') {
        showOrHideError(name, 'Nazwa jest już zajęta.')
    }
    else {
        showOrHideError(name)
    }
}

function checkPassword() {
    let name = document.getElementById(event.target.id);
    checkPasswordSyntax(name)

}

function checkPasswordSyntax(name) {
    if (checkFieldEmpty(name)) {
        return;
    }
    else if (!(/^[A-Za-z]+$/.test(name.value))) {
        showOrHideError(name, 'Dozwolone są wyłącznie małe i duże litery z zakresu a-z.')
    }
    else if (name.value.length < 8) {
        showOrHideError(name, 'Hasło musi mieć minimalnie 8 znaków.')
    }
    else {
        showOrHideError(name)
    }
}

function checkRepeatPassword() {
    let name = document.getElementById(event.target.id);
    if (name.value != document.getElementById("password").value) {
        showOrHideError(name, 'Hasła nie są zgodne.')
    }
    else {
        checkPasswordSyntax(name)
    }
}

function checkPhoto() {
    let name = document.getElementById(event.target.id);
    if (!checkFieldEmpty(name.value)) {
        showOrHideError(name)
    }
}

document.addEventListener('DOMContentLoaded', init);