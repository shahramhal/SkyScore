document.addEventListener('DOMContentLoaded', function() {
    // Password visibility toggle
    const showPasswordCheckbox = document.getElementById('show_password');
    if (showPasswordCheckbox) {
      const newPasswordField = document.getElementById('new_password');
      const confirmPasswordField = document.getElementById('confirm_password');
      
      showPasswordCheckbox.addEventListener('change', function() {
        const type = this.checked ? 'text' : 'password';
        if (newPasswordField) newPasswordField.type = type;
        if (confirmPasswordField) confirmPasswordField.type = type;
      });
    }
    
    // Password strength meter
    const newPasswordField = document.getElementById('new_password');
    if (newPasswordField) {
      const strengthIndicator = document.createElement('div');
      strengthIndicator.className = 'password-strength';
      
      const strengthMeter = document.createElement('div');
      strengthMeter.className = 'strength-weak';
      
      const strengthText = document.createElement('div');
      strengthText.className = 'strength-text';
      strengthText.textContent = 'Password strength: Weak';
      
      strengthIndicator.appendChild(strengthMeter);
      newPasswordField.parentNode.insertBefore(strengthIndicator, newPasswordField.nextSibling);
      newPasswordField.parentNode.insertBefore(strengthText, strengthIndicator.nextSibling);
      
      newPasswordField.addEventListener('input', function() {
        const password = this.value;
        let strength = 0;
        
        // Length check
        if (password.length >= 8) strength += 1;
        
        // Complexity checks
        if (/[A-Z]/.test(password)) strength += 1;
        if (/[a-z]/.test(password)) strength += 1;
        if (/[0-9]/.test(password)) strength += 1;
        if (/[^A-Za-z0-9]/.test(password)) strength += 1;
        
        // Update visual indicator
        if (strength <= 2) {
          strengthMeter.className = 'strength-weak';
          strengthText.textContent = 'Password strength: Weak';
        } else if (strength <= 4) {
          strengthMeter.className = 'strength-medium';
          strengthText.textContent = 'Password strength: Medium';
        } else {
          strengthMeter.className = 'strength-strong';
          strengthText.textContent = 'Password strength: Strong';
        }
      });
    }
    
    // Form validation
    const resetForm = document.querySelector('form');
    if (resetForm) {
      resetForm.addEventListener('submit', function(event) {
        const newPassword = document.getElementById('new_password');
        const confirmPassword = document.getElementById('confirm_password');
        
        if (newPassword && confirmPassword) {
          if (newPassword.value !== confirmPassword.value) {
            event.preventDefault();
            alert('Passwords do not match!');
          } else if (newPassword.value.length < 8) {
            event.preventDefault();
            alert('Password must be at least 8 characters long!');
          }
        }
      });
    }
  });