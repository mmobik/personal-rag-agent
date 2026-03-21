document.addEventListener('DOMContentLoaded', function() {
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const showRegisterLink = document.getElementById('showRegister');
  const showLoginLink = document.getElementById('showLogin');
  const loginContainer = document.querySelector('.login-form');
  const registerContainer = document.querySelector('.register-form');
  const messageDiv = document.getElementById('message');
  const regMessageDiv = document.getElementById('regMessage');

  // Переключение между формами
  showRegisterLink.addEventListener('click', function(e) {
    e.preventDefault();
    loginContainer.classList.add('hidden');
    registerContainer.classList.remove('hidden');
    clearMessages();
  });

  showLoginLink.addEventListener('click', function(e) {
    e.preventDefault();
    registerContainer.classList.add('hidden');
    loginContainer.classList.remove('hidden');
    clearMessages();
  });

  // Очистка сообщений
  function clearMessages() {
    messageDiv.className = 'message';
    messageDiv.textContent = '';
    regMessageDiv.className = 'message';
    regMessageDiv.textContent = '';
  }

  // Отображение сообщения
  function showMessage(element, message, isError = false) {
    element.textContent = message;
    element.className = 'message ' + (isError ? 'error' : 'success');
  }

  // Обработка входа
  loginForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    clearMessages();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Сохраняем токен в localStorage
        localStorage.setItem('user', JSON.stringify(data));
        showMessage(messageDiv, 'Успешный вход! Перенаправление...', false);
        setTimeout(() => {
          window.location.href = '/ui/chat-history';
        }, 1000);
      } else {
        showMessage(messageDiv, data.detail || 'Ошибка входа', true);
      }
    } catch (error) {
      showMessage(messageDiv, 'Ошибка сети: ' + error.message, true);
    }
  });

  // Обработка регистрации
  registerForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    clearMessages();
    
    const email = document.getElementById('regEmail').value;
    const username = document.getElementById('regUsername').value;
    const password = document.getElementById('regPassword').value;
    
    try {
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, username, password })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        showMessage(regMessageDiv, 'Регистрация успешна! Теперь вы можете войти.', false);
        // Очищаем форму
        registerForm.reset();
        // Переключаемся на форму входа
        setTimeout(() => {
          registerContainer.classList.add('hidden');
          loginContainer.classList.remove('hidden');
        }, 2000);
      } else {
        showMessage(regMessageDiv, data.detail || 'Ошибка регистрации', true);
      }
    } catch (error) {
      showMessage(regMessageDiv, 'Ошибка сети: ' + error.message, true);
    }
  });
});
