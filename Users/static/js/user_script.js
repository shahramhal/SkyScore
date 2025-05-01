// Combined script for user role, department and team selection
document.addEventListener('DOMContentLoaded', function () {
  // Role selection dropdown handling
  const roleSelect = document.getElementById('role-select');
  const selectedRoleText = document.getElementById('selected-role');
  const deptSelectionRow = document.getElementById('dept-selection-row');
  const teamSelectionRow = document.getElementById('team-selection-row');
  const departmentSelect = document.getElementById('department-select');
  const teamSelect = document.getElementById('team-select');
  const selectedDepartment = document.getElementById('selected-department');
  const selectedTeam = document.getElementById('selected-team');

  // Role-based field display settings
  const roleSettings = {
    'Engineer': { showDept: true, showTeam: true, deptRequired: true, teamRequired: true },
    'team_lead': { showDept: true, showTeam: true, deptRequired: true, teamRequired: true },
    'dept_lead': { showDept: true, showTeam: false, deptRequired: true, teamRequired: false },
    'Sen-man': { showDept: false, showTeam: false, deptRequired: false, teamRequired: false },
    'admin': { showDept: false, showTeam: false, deptRequired: false, teamRequired: false }
  };

  // Store all original team options on page load
  const originalTeamOptions = [];
  if (teamSelect) {
    Array.from(teamSelect.options).forEach(option => {
      if (option.value) {
        originalTeamOptions.push({
          value: option.value,
          text: option.textContent,
          departmentId: option.getAttribute('data-department')
        });
      }
    });
    console.log("Original team options saved:", originalTeamOptions);
  }

  // Function to update form fields based on selected role
  function updateFormFields(role) {
    if (!role || !roleSettings[role]) {
      // Default to showing both if role is not set or not recognized
      deptSelectionRow.style.display = 'flex';
      teamSelectionRow.style.display = 'flex';
      departmentSelect.required = false;
      teamSelect.required = false;
      return;
    }

    const settings = roleSettings[role];

    // Update department row visibility
    deptSelectionRow.style.display = settings.showDept ? 'flex' : 'none';
    departmentSelect.required = settings.deptRequired;

    // Update team row visibility
    teamSelectionRow.style.display = settings.showTeam ? 'flex' : 'none';
    teamSelect.required = settings.teamRequired;

    // If department is hidden, clear its selection
    if (!settings.showDept) {
      departmentSelect.value = '';
      if (selectedDepartment) {
        selectedDepartment.textContent = 'Choose a department';
      }
    }

    // If team is hidden, clear its selection
    if (!settings.showTeam) {
      teamSelect.value = '';
      if (selectedTeam) {
        selectedTeam.textContent = 'Choose a team';
      }
    }

    // Update team options if dept visibility changes
    updateTeamOptions();
  }

  if (roleSelect && selectedRoleText) {
    // Set initial value if there's a selection
    if (roleSelect.selectedIndex > 0) {
      const selectedOption = roleSelect.options[roleSelect.selectedIndex];
      selectedRoleText.textContent = selectedOption.text;
      updateFormFields(roleSelect.value);
    }

    // Update on change
    roleSelect.addEventListener('change', function () {
      const selectedOption = roleSelect.options[roleSelect.selectedIndex];
      selectedRoleText.textContent = selectedOption.text || 'Choose the role';
      updateFormFields(roleSelect.value);
    });
  }

  // Password visibility toggle
  const showPasswordCheckbox = document.getElementById('show_password');
  const passwordField = document.querySelector('input[name="password"]');
  const confirmPasswordField = document.querySelector('input[name="confirm_password"]');

  if (showPasswordCheckbox && passwordField && confirmPasswordField) {
    // Set up the change event listener
    showPasswordCheckbox.addEventListener('change', function () {
      togglePasswordVisibility();
    });

    // Function to toggle password visibility
    function togglePasswordVisibility() {
      const type = showPasswordCheckbox.checked ? 'text' : 'password';
      passwordField.type = type;
      confirmPasswordField.type = type;
    }
  }

  // Function to update teams dropdown based on selected department
  function updateTeamOptions() {
    if (!departmentSelect || !teamSelect) {
      console.error("Department or team select elements not found");
      return;
    }

    // If team selection is hidden, don't update
    if (teamSelectionRow.style.display === 'none') {
      return;
    }

    const deptId = departmentSelect.value;
    console.log("Selected department ID:", deptId);

    // Clear existing options except the first one
    while (teamSelect.options.length > 1) {
      teamSelect.options.remove(1);
    }

    // Reset selected team text
    if (selectedTeam) {
      selectedTeam.textContent = 'Choose a team';
    }

    // If no department selected, just leave the dropdown empty
    if (!deptId) return;

    // Add teams for the selected department from our original stored options
    const teamsForDepartment = originalTeamOptions.filter(team => team.departmentId === deptId);
    console.log(`Adding ${teamsForDepartment.length} teams for department ${deptId}`);

    teamsForDepartment.forEach(team => {
      const option = document.createElement('option');
      option.value = team.value;
      option.textContent = team.text;
      option.setAttribute('data-department', team.departmentId);
      teamSelect.appendChild(option);
    });

    // If a previously selected team is available for this department, select it
    const previouslySelectedTeam = teamSelect.getAttribute('data-selected-team');
    if (previouslySelectedTeam) {
      for (let i = 0; i < teamSelect.options.length; i++) {
        if (teamSelect.options[i].value === previouslySelectedTeam) {
          teamSelect.selectedIndex = i;
          if (selectedTeam) {
            selectedTeam.textContent = teamSelect.options[i].textContent;
          }
          break;
        }
      }
    }
  }

  // Handle department selection change
  if (departmentSelect) {
    // Set initial value if there's a selection
    if (departmentSelect.selectedIndex > 0 && selectedDepartment) {
      const selectedOption = departmentSelect.options[departmentSelect.selectedIndex];
      selectedDepartment.textContent = selectedOption.textContent;

      // Also update team options based on initial department
      updateTeamOptions();
    }

    departmentSelect.addEventListener('change', function () {
      // Update the displayed text
      if (selectedDepartment) {
        const selectedOption = departmentSelect.options[departmentSelect.selectedIndex];
        selectedDepartment.textContent = selectedOption.textContent !== '-- Select Department --'
          ? selectedOption.textContent
          : 'Choose a department';
      }

      // Update team options based on selected department
      updateTeamOptions();
    });
  } else {
    console.error("Department select element not found!");
  }

  // Handle team selection change
  if (teamSelect) {
    // Set initial value if there's a selection
    if (teamSelect.selectedIndex > 0 && selectedTeam) {
      const selectedOption = teamSelect.options[teamSelect.selectedIndex];
      selectedTeam.textContent = selectedOption.textContent;
      // Save the selected team value as a data attribute for restoration
      teamSelect.setAttribute('data-selected-team', selectedOption.value);
    }

    teamSelect.addEventListener('change', function () {
      if (selectedTeam) {
        const selectedOption = teamSelect.options[teamSelect.selectedIndex];
        selectedTeam.textContent = selectedOption.textContent !== '-- Select Team --'
          ? selectedOption.textContent
          : 'Choose a team';

        // Save the selected team value as a data attribute
        if (selectedOption.value) {
          teamSelect.setAttribute('data-selected-team', selectedOption.value);
        } else {
          teamSelect.removeAttribute('data-selected-team');
        }
      }
    });
  }

  // Run initial field update based on role
  if (roleSelect && roleSelect.value) {
    updateFormFields(roleSelect.value);
  }

  // Run initial team update in case department is pre-selected (e.g., form redisplay after validation error)
  if (departmentSelect && departmentSelect.value) {
    updateTeamOptions();
  }
});