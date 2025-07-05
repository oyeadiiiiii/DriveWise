// Remove direct webcam access from browser and use server video feed

const eventSource = new EventSource("/state_feed");

let prevState = ""; // Variable to store the previous state

function updateDriverName() {
    fetch('/get_driver_name')
    .then(response => response.json())
    .then(data => {
        const driverName = document.getElementById("driverName");
        if (data.driverName) {
            driverName.textContent = "Driver's Name: " + data.driverName;
        } else {
            driverName.textContent = "Driver's Name: Unknown";
        }
    })
    .catch(error => {
        console.error('Error fetching driver name:', error);
    });
}

// Automatically poll for driver name every 5 seconds
setInterval(updateDriverName, 5000);

// Initial update when page loads
document.addEventListener('DOMContentLoaded', () => {
    updateDriverName();

    // Set up video feed from server
    const videoElement = document.getElementById('videoElement');
    if (videoElement) {
        videoElement.src = "/video_feed_act";
        videoElement.autoplay = true;
        videoElement.muted = true;
        videoElement.playsInline = true;
    }
});

eventSource.onmessage = function(event) {
    const stateText = document.getElementById("stateText");
    let newState = event.data.trim();

    if (newState !== prevState && newState !== "") {
        stateText.textContent += newState + "\n";
        stateBox.scrollTop = stateBox.scrollHeight;
        prevState = newState;
    }
};

registerButton.addEventListener('click', () => {
    const driverName = prompt("Please enter your name:", "");
    if (driverName !== null && driverName !== "") {
        document.getElementById('register-progress').innerText = "Starting registration...";
        fetch('/register_driver', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: driverName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('register-progress').innerText = 
                    `Registration complete!`;
                updateDriverName();
            } else {
                document.getElementById('register-progress').innerText = 
                    'Failed to register driver.';
            }
        })
        .catch(error => {
            document.getElementById('register-progress').innerText = 
                'Error registering driver.';
            console.error('Error registering driver:', error);
        });

        // Poll for progress every 0.5s
        let interval = setInterval(() => {
            fetch('/register_progress')
                .then(response => response.json())
                .then(data => {
                    if (data.clicks_left > 0) {
                        document.getElementById('register-progress').innerText =
                            `Images left: ${data.clicks_left} / 50`;
                    } else {
                        clearInterval(interval);
                    }
                });
        }, 500);
    }
});

eventSource.onerror = function(error) {
    console.error("EventSource failed:", error);
    eventSource.close();
};

// Remove browser-side webcam access code
// The video feed is now provided by the server via <img> or <video> tag with src="/video_feed_act"