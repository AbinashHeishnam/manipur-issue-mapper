// ================= MAP INITIALIZATION =================

// Initialize the map centered on Manipur
var map = L.map('map').setView([24.817, 93.9368], 8);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Add location input field dynamically above hidden lat/lng
var form = document.getElementById('issueForm');
var locationInput = document.createElement('input');
locationInput.type = 'text';
locationInput.id = 'location';
locationInput.placeholder = 'Click map or type address';
locationInput.required = true;
// Insert after category select
form.insertBefore(locationInput, document.getElementById('description'));

// ================= GEOLOCATION =================

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
        var lat = position.coords.latitude;
        var lng = position.coords.longitude;

        map.setView([lat, lng], 13);

        if (window.tempMarker) map.removeLayer(window.tempMarker);
        window.tempMarker = L.marker([lat, lng]).addTo(map)
            .bindPopup('You are here!')
            .openPopup();

        document.getElementById('lat').value = lat;
        document.getElementById('lng').value = lng;

        // Fill location input automatically
        reverseGeocode(lat, lng);
    }, function(error) {
        console.warn('ERROR(' + error.code + '): ' + error.message);
    });
} else {
    alert('Geolocation is not supported by your browser.');
}

// ================= GEOCODING FUNCTIONS =================

function reverseGeocode(lat, lng) {
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('location').value = data.display_name || '';
        });
}

function forwardGeocode(address) {
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`)
        .then(res => res.json())
        .then(results => {
            if (results && results.length > 0) {
                var lat = parseFloat(results[0].lat);
                var lng = parseFloat(results[0].lon);

                map.setView([lat, lng], 13);

                if (window.tempMarker) map.removeLayer(window.tempMarker);
                window.tempMarker = L.marker([lat, lng]).addTo(map)
                    .bindPopup('Selected location')
                    .openPopup();

                document.getElementById('lat').value = lat;
                document.getElementById('lng').value = lng;
            }
        });
}

// ================= MAP CLICK EVENT =================

map.on('click', function(e) {
    var lat = e.latlng.lat;
    var lng = e.latlng.lng;

    document.getElementById('lat').value = lat;
    document.getElementById('lng').value = lng;

    if (window.tempMarker) map.removeLayer(window.tempMarker);
    window.tempMarker = L.marker([lat, lng]).addTo(map)
        .bindPopup('Selected location')
        .openPopup();

    reverseGeocode(lat, lng);
});

// ================= LOCATION INPUT EVENT =================

document.getElementById('location').addEventListener('change', function() {
    var address = this.value;
    if (address) forwardGeocode(address);
});

// ================= FORM SUBMISSION =================

document.getElementById('issueForm').addEventListener('submit', function(e) {
    e.preventDefault();

    var title = document.getElementById('title').value;
    var category = document.getElementById('category').value;
    var description = document.getElementById('description').value;
    var lat = document.getElementById('lat').value;
    var lng = document.getElementById('lng').value;
    var location = document.getElementById('location').value;

    if (!title || !lat || !lng || !location) {
        alert('Please enter a title and select a location!');
        return;
    }

    // Include user_id if logged in
    var userId = window.currentUserId || 1; // fallback

    fetch('http://127.0.0.1:8000/api/issues/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: title,
            category: category,
            description: description,
            latitude: parseFloat(lat),
            longitude: parseFloat(lng),
            location: location,
            user_id: userId
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Issue submitted successfully!');
            this.reset();
            if (window.tempMarker) map.removeLayer(window.tempMarker);
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(err => {
        console.error('Submit Error:', err);
        alert('Error submitting issue. See console.');
    });
});
var aiCategory = window.aiCategory || category; // fallback to manual
var aiSeverity = parseInt(window.aiSeverity || 1);

fetch('http://127.0.0.1:8000/api/issues/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        title: title,
        category: category,
        description: description,
        latitude: parseFloat(lat),
        longitude: parseFloat(lng),
        user_id: userId,
        ai_category: aiCategory,
        ai_severity: aiSeverity
    })
})
