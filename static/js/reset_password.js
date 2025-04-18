
      document.addEventListener("DOMContentLoaded", function () {
        // Password visibility toggle
        const showPasswordCheckbox = document.getElementById("show_password");
        const newPasswordField = document.getElementById("new_password");
        const confirmPasswordField =
          document.getElementById("confirm_password");

        if (showPasswordCheckbox && newPasswordField && confirmPasswordField) {
          showPasswordCheckbox.addEventListener("change", function () {
            const type = this.checked ? "text" : "password";
            newPasswordField.type = type;
            confirmPasswordField.type = type;
          });
        }
      });