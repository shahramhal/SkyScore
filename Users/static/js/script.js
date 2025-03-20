document.addEventListener('DOMContentLoaded', function () {
  // Role selection dropdown code from your existing script
  const select = document.getElementById('role-select');
  const selectedRoleText = document.getElementById('selected-role');

  // Set initial value
  const selectedOption = select.options[select.selectedIndex];
  selectedRoleText.textContent = selectedOption.text;

  // Update on change
  select.addEventListener('change', function () {
    const selectedOption = select.options[select.selectedIndex];
    selectedRoleText.textContent = selectedOption.text;
  });

  // Password visibility toggle
  const showPasswordCheckbox = document.getElementById('show_password');
  const passwordField = document.querySelector('input[name="password"]');
  const confirmPasswordField = document.querySelector('input[name="confirm_password"]');
  
  showPasswordCheckbox.addEventListener('change', function() {
    const type = this.checked ? 'text' : 'password';
    passwordField.type = type;
    confirmPasswordField.type = type;
  });
});