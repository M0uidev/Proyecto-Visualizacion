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

  // Marca campo como inválido con mensaje de error
  function setInvalid(input, message) {
    input.classList.add('is-invalid');
    const feedback = input.parentElement.querySelector('.invalid-feedback') || input.nextElementSibling;
    if (feedback) {
      feedback.textContent = message;
    }
  }

  // Limpia validación inválida del campo
  function clearInvalid(input) {
    input.classList.remove('is-invalid');
  }

  // Muestra alerta con tipo y texto
  function showAlert(type, text) {
    alertBox.className = `alert alert-${type}`;
    alertBox.textContent = text;
    alertBox.classList.remove('d-none');
  }

  // Toggle visibilidad de contraseña
  if (togglePwd && pass) {
    togglePwd.addEventListener('click', () => {
      const isPassword = pass.type === 'password';
      pass.type = isPassword ? 'text' : 'password';
      togglePwd.innerHTML = isPassword ? '<i class="bi bi-eye-slash"></i>' : '<i class="bi bi-eye"></i>';
    });
  }

  // Manejo del envío del formulario
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

    // Simula envío y redirige
    setTimeout(() => {
      showAlert('success', 'Ingreso exitoso. ¡Bienvenido!');
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="bi bi-box-arrow-in-right me-1"></i> Ingresar';

      if (redirectUrl) {
        window.location.href = redirectUrl;
      }
    }, 600);
  });

  // Limpia errores al escribir
  form.addEventListener('input', ({ target }) => {
    if (target.classList.contains('form-control')) {
      clearInvalid(target);
    }
  });
})();
