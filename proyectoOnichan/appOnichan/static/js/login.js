(function () {
  const form = document.getElementById('loginForm');
  if (!form) {
    return;
  }

  const user = document.getElementById('username');
  const pass = document.getElementById('password');
  const alertBox = document.getElementById('alertBox');
  const togglePwd = document.getElementById('togglePwd');
  const submitBtn = document.getElementById('submitBtn');
  const redirectUrl = form.getAttribute('data-redirect-url');

  function setInvalid(input, message) {
    input.classList.add('is-invalid');
    const feedback = input.parentElement.querySelector('.invalid-feedback') || input.nextElementSibling;
    if (feedback) {
      feedback.textContent = message;
    }
  }

  function clearInvalid(input) {
    input.classList.remove('is-invalid');
  }

  function showAlert(type, text) {
    alertBox.className = `alert alert-${type}`;
    alertBox.textContent = text;
    alertBox.classList.remove('d-none');
  }

  if (togglePwd && pass) {
    togglePwd.addEventListener('click', () => {
      const isPassword = pass.type === 'password';
      pass.type = isPassword ? 'text' : 'password';
      togglePwd.innerHTML = isPassword ? '<i class="bi bi-eye-slash"></i>' : '<i class="bi bi-eye"></i>';
    });
  }

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    alertBox.classList.add('d-none');

    const usernameValue = user.value.trim();
    const passwordValue = pass.value.trim();

    clearInvalid(user);
    clearInvalid(pass);

    let isValid = true;
    if (!usernameValue) {
      setInvalid(user, 'Ingresa tu usuario.');
      isValid = false;
    }
    if (!passwordValue) {
      setInvalid(pass, 'Ingresa tu contraseña.');
      isValid = false;
    }

    if (!isValid) {
      showAlert('danger', 'Revisa los campos resaltados.');
      return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Ingresando...';

    setTimeout(() => {
      showAlert('success', 'Ingreso exitoso. ¡Bienvenido!');
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="bi bi-box-arrow-in-right me-1"></i> Ingresar';

      if (redirectUrl) {
        window.location.href = redirectUrl;
      }
    }, 600);
  });

  form.addEventListener('input', ({ target }) => {
    if (target.classList.contains('form-control')) {
      clearInvalid(target);
    }
  });
})();
