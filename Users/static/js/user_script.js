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
    showPasswordCheckbox.addEventListener('change', function () {
      const type = this.checked ? 'text' : 'password';
      passwordField.type = type;
      confirmPasswordField.type = type;
    });
  }

  // Store the original teams data
  let teamsData = {};

  // Initialize teams data from the options
  if (teamSelect) {
    const teamOptions = Array.from(teamSelect.querySelectorAll('option')).filter(opt => opt.value);

    // Check if there are any teams
    if (teamOptions.length === 0) {
      console.warn("No team options found in the dropdown!");
    }

    teamOptions.forEach(option => {
      const deptId = option.getAttribute('data-department');
      if (deptId) {
        if (!teamsData[deptId]) {
          teamsData[deptId] = [];
        }
        teamsData[deptId].push({
          id: option.value,
          name: option.textContent
        });
      } else {
        console.warn(`Team option "${option.textContent}" has no department ID attribute`);
      }
    });

    // Debug log
    console.log("Teams data initialized:", teamsData);
  } else {
    console.error("Team select element not found!");
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

    // Add teams for the selected department
    if (deptId && teamsData[deptId]) {
      console.log(`Adding ${teamsData[deptId].length} teams for department ${deptId}`);
      teamsData[deptId].forEach(team => {
        const option = document.createElement('option');
        option.value = team.id;
        option.textContent = team.name;
        option.setAttribute('data-department', deptId);
        teamSelect.appendChild(option);
      });
    } else if (deptId) {
      console.warn(`No teams found for department ID ${deptId}`);
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
    }

    teamSelect.addEventListener('change', function () {
      if (selectedTeam) {
        const selectedOption = teamSelect.options[teamSelect.selectedIndex];
        selectedTeam.textContent = selectedOption.textContent !== '-- Select Team --'
          ? selectedOption.textContent
          : 'Choose a team';
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