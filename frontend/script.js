const API = "https://YOUR-RENDER-BACKEND.onrender.com";

let token = "";


// ================= TOGGLE PASSWORD =================

function togglePassword(id) {

  let input = document.getElementById(id);

  if (input.type === "password") {

    input.type = "text";

  } else {

    input.type = "password";
  }
}


// ================= AUTH UI =================

function showRegister() {

  document.getElementById(
    "loginSection"
  ).style.display = "none";

  document.getElementById(
    "registerSection"
  ).style.display = "block";
}


function showLogin() {

  document.getElementById(
    "registerSection"
  ).style.display = "none";

  document.getElementById(
    "loginSection"
  ).style.display = "block";
}


// ================= REGISTER =================

function register() {

  let fullName =
    document.getElementById(
      "fullName"
    ).value;

  let username =
    document.getElementById(
      "registerUsername"
    ).value;

  let email =
    document.getElementById(
      "registerEmail"
    ).value;

  let password =
    document.getElementById(
      "registerPassword"
    ).value;

  let confirmPassword =
    document.getElementById(
      "confirmPassword"
    ).value;


  // ================= VALIDATIONS =================

  if (
    !email.includes("@")
  ) {

    alert(
      "Email must contain @"
    );

    return;
  }


  if (
    !email.includes(".com")
  ) {

    alert(
      "Email must contain .com"
    );

    return;
  }


  if (
    !email.includes("gmail") &&
    !email.includes("yahoo")
  ) {

    alert(
      "Use gmail.com or yahoo.com email"
    );

    return;
  }


  if (
    password !== confirmPassword
  ) {

    alert(
      "Password and Confirm Password do not match"
    );

    return;
  }


  fetch(API + "/register", {

    method: "POST",

    headers: {
      "Content-Type": "application/json"
    },

    body: JSON.stringify({

      full_name: fullName,

      username: username,

      email: email,

      password: password,

      confirm_password:
      confirmPassword
    })

  })

  .then(res => res.json())

  .then(data => {

    if (data.error) {

      alert(data.error);

      return;
    }

    alert(
      "Registration successful"
    );

    showLogin();

  })

  .catch(err => {

    console.error(err);

    alert(
      "Registration failed"
    );

  });
}


// ================= LOGIN =================

function login() {

  let username =
    document.getElementById(
      "loginUsername"
    ).value;

  let password =
    document.getElementById(
      "loginPassword"
    ).value;


  fetch(API + "/login", {

    method: "POST",

    headers: {
      "Content-Type": "application/json"
    },

    body: JSON.stringify({

      username: username,

      password: password
    })

  })

  .then(res => res.json())

  .then(data => {

    console.log(data);

    if (data.error) {

      alert(data.error);

      return;
    }

    token = data.token;

    localStorage.setItem(
      "token",
      token
    );

    localStorage.setItem(
      "full_name",
      data.full_name
    );

    document.getElementById(
      "authContainer"
    ).style.display = "none";

    document.getElementById(
      "mainApp"
    ).style.display = "block";

    document.getElementById(
      "welcomeText"
    ).innerText =
      "Welcome " + data.full_name;

    loadRoles();

    loadDashboard();

  })

  .catch(err => {

    console.error(err);

    alert("Login failed");

  });
}


// ================= LOGOUT =================

function logout() {

  localStorage.clear();

  location.reload();
}


// ================= LOAD ROLES =================

function loadRoles() {

  fetch(API + "/roles")

    .then(res => res.json())

    .then(data => {

      let roleSelect =
        document.getElementById(
          "role"
        );

      roleSelect.innerHTML = "";

      data.forEach(role => {

        let option =
          document.createElement(
            "option"
          );

        option.value = role;

        option.textContent = role;

        roleSelect.appendChild(
          option
        );

      });

    });
}


// ================= ANALYZE RESUME =================

function analyzeResume() {

  let role =
    document.getElementById(
      "role"
    ).value;

  let fileInput =
    document.getElementById(
      "resumeFile"
    );


  if (
    fileInput.files.length === 0
  ) {

    alert("Upload resume");

    return;
  }


  let formData = new FormData();

  formData.append(
    "resume",
    fileInput.files[0]
  );

  formData.append(
    "role",
    role
  );


  fetch(API + "/analyze", {

    method: "POST",

    headers: {

      "Authorization":
      "Bearer " + token
    },

    body: formData

  })

  .then(res => res.json())

  .then(data => {

    if (data.error) {

      alert(data.error);

      return;
    }

    document.getElementById(
      "analysisResult"
    ).innerHTML = `

      <div class="score-box">
        ATS Score:
        ${data.score}%
      </div>

      <pre style="white-space: pre-wrap;">
${data.feedback}
      </pre>
    `;

    loadDashboard();

  });
}


// ================= DASHBOARD =================

function loadDashboard() {

  fetch(API + "/dashboard", {

    headers: {

      "Authorization":
      "Bearer " + token
    }

  })

  .then(res => res.json())

  .then(data => {

    let html =
      "<h3>Resume History</h3>";

    data.resumes.forEach(r => {

      html += `

        <div>

          <b>Role:</b>
          ${r.role}<br>

          <b>Score:</b>
          ${r.score}%<br>

          <b>File:</b>
          ${r.filename}

          <hr>

        </div>
      `;
    });

    html +=
      "<h3>Interview History</h3>";

    data.interviews.forEach(i => {

      html += `

        <div>

          <b>Role:</b>
          ${i.role}<br>

          <b>Score:</b>
          ${i.score}<br>

          <hr>

        </div>
      `;
    });

    document.getElementById(
      "dashboard"
    ).innerHTML = html;

  });
}


// ================= START INTERVIEW =================

function startInterview() {

  let role =
    document.getElementById(
      "role"
    ).value;


  fetch(API + "/start", {

    method: "POST",

    headers: {

      "Content-Type":
      "application/json",

      "Authorization":
      "Bearer " + token
    },

    body: JSON.stringify({

      role: role,

      duration: 5
    })

  })

  .then(res => res.json())

  .then(data => {

    document.getElementById(
      "chat"
    ).innerHTML = `

      <p>
        <b>Interviewer:</b>
        ${data.question}
      </p>
    `;

  });
}


// ================= SEND ANSWER =================

function sendAnswer() {

  let answer =
    document.getElementById(
      "answer"
    ).value;


  fetch(API + "/next", {

    method: "POST",

    headers: {

      "Content-Type":
      "application/json",

      "Authorization":
      "Bearer " + token
    },

    body: JSON.stringify({

      answer: answer
    })

  })

  .then(res => res.json())

  .then(data => {

    let chat =
      document.getElementById(
        "chat"
      );

    chat.innerHTML += `

      <p>
        <b>You:</b>
        ${answer}
      </p>

      <p>
        <b>Feedback:</b>
        ${data.evaluation}
      </p>
    `;


    // ================= INTERVIEW END =================

    if (data.end) {

      chat.innerHTML += `

        <p>
          <b>Final Score:</b>
          ${data.result.final_score}
        </p>
      `;

      loadDashboard();

      return;
    }


    // ================= NEXT QUESTION =================

    chat.innerHTML += `

      <p>
        <b>Interviewer:</b>
        ${data.question}
      </p>
    `;

    loadDashboard();

  });

  document.getElementById(
    "answer"
  ).value = "";
}


// ================= END INTERVIEW =================

function endInterview() {

  fetch(API + "/end", {

    method: "POST",

    headers: {

      "Authorization":
      "Bearer " + token
    }

  })

  .then(res => res.json())

  .then(data => {

    let chat =
      document.getElementById(
        "chat"
      );

    chat.innerHTML += `

      <p>
        <b>Interview Finished</b>
      </p>

      <p>
        <b>Final Score:</b>
        ${data.final_score}
      </p>
    `;

    loadDashboard();

  });
}


// ================= AUTO LOGIN =================

window.onload = () => {

  token = localStorage.getItem(
    "token"
  );

  let fullName =
    localStorage.getItem(
      "full_name"
    );

  if (token) {

    document.getElementById(
      "authContainer"
    ).style.display = "none";

    document.getElementById(
      "mainApp"
    ).style.display = "block";

    document.getElementById(
      "welcomeText"
    ).innerText =
      "Welcome " + fullName;

    loadRoles();

    loadDashboard();
  }
};