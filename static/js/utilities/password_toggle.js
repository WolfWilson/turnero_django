/**
 static/js/utilities/password_toggle.js
 * Gestiona la funcionalidad de mostrar/ocultar contraseña.
 */
document.addEventListener('DOMContentLoaded', function() {
    const passwordField = document.querySelector('#password-field');
    const togglePasswordButton = document.querySelector('#toggle-password');
    const eyeIcon = document.querySelector('#eye-icon');

    // Solo se ejecuta si los 3 elementos existen en la página.
    if (passwordField && togglePasswordButton && eyeIcon) {
        togglePasswordButton.addEventListener('click', function() {
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
            eyeIcon.textContent = type === 'text' ? 'visibility_off' : 'visibility';
        });
    }
});