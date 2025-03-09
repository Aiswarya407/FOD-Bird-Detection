// Alert logic for detected objects
function showAlert(message) {
    const alertBox = document.getElementById('alert-box');
    alertBox.textContent = message;
    alertBox.style.display = 'block';

    // Auto-hide alert after 5 seconds
    setTimeout(() => {
        alertBox.style.display = 'none';
    }, 5000);
}

// Example usage for alerts (you can modify it for real-time alerts from Flask)
window.onload = function() {
    // Simulating an alert from the Flask app
    const detectedObjects = ["Plastic", "Metal", "Concrete"];
    detectedObjects.forEach(obj => {
        showAlert(`🚨 ALERT: ${obj} detected on the runway!`);
    });
}
