async function handleLogin(event) {
    event.preventDefault();

    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginBtn = document.getElementById('login-btn');
    const errorMsg = document.getElementById('error-msg');

    // Reset state
    errorMsg.style.display = 'none';
    loginBtn.disabled = true;
    loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Memproses...';

    const username = usernameInput.value;
    const password = passwordInput.value;

    try {
        // Call backend login function
        const result = await eel.login(username, password)();

        if (result.success) {
            // Save user session
            localStorage.setItem('snapflux_user', JSON.stringify(result.user));
            localStorage.setItem('snapflux_token', 'valid'); // Simple token simulation

            // Redirect to dashboard
            window.location.href = 'index.html';
        } else {
            // Show error
            errorMsg.textContent = result.message;
            errorMsg.style.display = 'block';
            loginBtn.disabled = false;
            loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Masuk';
        }
    } catch (error) {
        console.error('Login error:', error);
        errorMsg.textContent = 'Terjadi kesalahan sistem. Coba lagi.';
        errorMsg.style.display = 'block';
        loginBtn.disabled = false;
        loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Masuk';
    }
}

// Check if already logged in
document.addEventListener('DOMContentLoaded', () => {
    const user = localStorage.getItem('snapflux_user');
    if (user) {
        window.location.href = 'index.html';
    }
});
