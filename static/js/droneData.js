// Function to create or update a data box for each drone
function updateDroneData(data) {
    const container = document.getElementById('drone-data-container');
    container.innerHTML = ''; // Clear the container before adding new data

    if (Array.isArray(data)) {
        data.forEach(drone => {
            const box = document.createElement('div');
            box.classList.add('drone-data-box');
            box.innerHTML = `
                <h3 class="drone-title">${drone.call_sign}</h3>
                <div class="drone-info">
                    <p><strong>Latitude:</strong> ${drone.latitude.toFixed(4)}</p>
                    <p><strong>Longitude:</strong> ${drone.longitude.toFixed(4)}</p>
                    <p><strong>Status:</strong> ${drone.status || 'Unknown'}</p>
                    <p><strong>Altitude:</strong> ${drone.altitude || 'N/A'}</p>
                </div>
            `;

            // Hover effect to highlight the box when hovered
            box.addEventListener('mouseover', () => {
                box.classList.add('hovered');
            });
            box.addEventListener('mouseout', () => {
                box.classList.remove('hovered');
            });

            // Add click event to navigate to the specific drone's page
            box.addEventListener('click', () => {
                const dronePage = getDronePage(drone.call_sign); // Get the page based on the call_sign
                window.location.href = `/${dronePage}`; // Navigate to the drone's specific page
            });

            // Append the new drone box to the container
            container.appendChild(box);
        });
    }
}

// Function to map drone call_sign to the URL page (droneA, droneB, etc.)
function getDronePage(callSign) {
    const dronePages = {
        'alpha': 'droneA',
        'bravo': 'droneB',
        'charlie': 'droneC',
        'juliet': 'droneJ' // Add more drones if needed
    };
    return dronePages[callSign.toLowerCase()] || ''; // Default to empty if not found
}

// Fetch drone data and update the boxes
function fetchDroneDataForBoxes() {
    fetch('/drone-data')
        .then(res => res.json())
        .then(data => {
            updateDroneData(data); // Update the drone boxes
        })
        .catch(err => console.error("Error fetching drone data for boxes:", err));
}

// Call the function to fetch and update drone data every 4 seconds
setInterval(fetchDroneDataForBoxes, 4000);
fetchDroneDataForBoxes(); // Initial fetch
