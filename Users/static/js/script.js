
      document.addEventListener("DOMContentLoaded", function () {
        const showPasswordCheckbox = document.getElementById("show_password");
        const passwordFields = document.querySelectorAll(
          'input[type="password"]'
        );

        showPasswordCheckbox.addEventListener("change", function () {
          passwordFields.forEach((field) => {
            field.type = this.checked ? "text" : "password";
          });
        });
      });
    