'use strict';
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js"

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyDylLZKAHEWCpGZCWidG2RxuS7eOFMlaF8",
    authDomain: "project-1-cdb5c.firebaseapp.com",
    projectId: "project-1-cdb5c",
    storageBucket: "project-1-cdb5c.firebasestorage.app",
    messagingSenderId: "1050411454241",
    appId: "1:1050411454241:web:e9acf4022e957be675b860",
    measurementId: "G-12Y7HXC9ZR"
};

window.addEventListener("load", function() {
    const app = initializeApp(firebaseConfig);
    const auth = getAuth(app);
    updateUI(document.cookie); 
    console.log("hello world load");
    document.getElementById("sign-up").addEventListener('click', function() {
        const email = document.getElementById("email").value
        const password = document.getElementById("password").value

        createUserWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            const user = userCredential.user;

            user.getIdToken().then((token) => {
                document.cookie = "token=" + token + "; path=/; SameSite=Strict";
                window.location = "/";
            });

        })
        .catch((error) => {
            console.log(error.code + error.message);
        })
    });

    // login of a user to firebase
    document.getElementById("login").addEventListener('click', function() {
        const email = document.getElementById("email").value
        const password = document.getElementById("password").value
        signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            const user = userCredential.user;
            console.log("logged in");

            user.getIdToken().then((token) => {
                document.cookie = "token=" + token + "; path=/;SameSite=Strict";
                window.location = "/";
            });
        })
        .catch((error) => {
            console.log(error.code + error.message);
        })
    });

    // signout from firebase
    document.getElementById("sign-out").addEventListener('click', function() {
        signOut(auth)
        .then((output) => {
            document.cookie = "token=; path=/; SameSite=Strict";
            window.location = "/";
        })
    });
});

function updateUI(cookie) {
    var token = parseCookieToken(cookie); // Fix here
    if (token.length > 0) {
        document.getElementById("login-box").hidden = true;
        document.getElementById("sign-out").hidden = false;
    } else {
        document.getElementById("login-box").hidden = false;
        document.getElementById("sign-out").hidden = true;
    }
};

// function that will take the cookie and will return the value associated with it to the caller
function parseCookieToken(cookie) {
    var strings = cookie.split(';');
    for (let i = 0; i < strings.length; i++) { 
        var temp = strings[i].split('='); 
        if (temp[0] == "token") 
            return temp[1];
    }
    return "";
}
