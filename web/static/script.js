// Empty means "same origin as this page"
const BACKEND_URL = "";

const webcam = document.getElementById('webcam');
const canvas = document.getElementById('frameCanvas');
const ctx = canvas.getContext('2d');
const stateText = document.getElementById("stateText");
const registerButton = document.getElementById("registerButton");
const registerProgress = document.getElementById("register-progress");
const driverNameBox = document.getElementById("driverName");

let prevState = "";

// Start webcam
async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        webcam.srcObject = stream;
        webcam.style.display = 'block';
        captureAndSendFrame();
    } catch (err) {
        alert('Could not access webcam: ' + err);
    }
}

// Capture and send frames to backend
function captureAndSendFrame() {
    ctx.drawImage(webcam, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(async function(blob) {
        if (blob) {
            const formData = new FormData();
            formData.append('frame', blob, 'frame.jpg');
            try {
                await fetch(`/upload_frame`, {
                    method: 'POST',
                    body: formData
                });
            } catch (e) {
                console.error("Frame upload error:", e);
            }
        }
        setTimeout(captureAndSendFrame, 200); // every 200ms
    }, 'image/jpeg', 0.8);
}

// Listen for driver state from server
const eventSource = new EventSource(`/state_feed`);
eventSource.onmessage = function(event) {
    const newState = event.data.trim();
    if (newState !== prevState && newState !== "") {
        stateText.textContent += newState + "\n";
        stateText.scrollTop = stateText.scrollHeight;
        prevState = newState;
    }
};
eventSource.onerror = function(error) {
    console.error("EventSource failed:", error);
    eventSource.close();
};

// Update driver name from backend
function updateDriverName() {
    fetch(`/get_driver_name`)
        .then(res => res.json())
        .then(data => {
            if (data.driverName) {
                driverNameBox.textContent = "Driver's Name: " + data.driverName;
            } else {
                driverNameBox.textContent = "Unknown Driver";
            }
        })
        .catch(err => {
            console.error("Driver name error:", err);
        });
}
setInterval(updateDriverName, 5000); // refresh every 5s

// Handle registration
registerButton.addEventListener('click', () => {
    const name = prompt("Enter your name:");
    if (!name) return;

    registerProgress.textContent = "Starting registration...";

    fetch(`/register_driver`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            registerProgress.textContent = "Registration complete!";
            updateDriverName();
        } else {
            registerProgress.textContent = "Failed to register driver.";
        }
    })
    .catch(err => {
        registerProgress.textContent = "Error during registration.";
        console.error("Registration error:", err);
    });

    // Poll registration progress
    const interval = setInterval(() => {
        fetch(`/register_progress`)
            .then(res => res.json())
            .then(data => {
                if (data.clicks_left > 0) {
                    registerProgress.textContent = `Images left: ${data.clicks_left} / 50`;
                } else {
                    clearInterval(interval);
                }
            });
    }, 500);
});

// Start everything
window.onload = startWebcam;
