// Get the issue ID from the URL query string
const params = new URLSearchParams(window.location.search);
const issueId = params.get('id');

if (!issueId) {
    document.body.innerHTML = "<h2>No issue selected</h2>";
} else {
    fetch(`http://127.0.0.1:8000/api/issues/${issueId}`)
        .then(res => res.json())
        .then(async data => {
            if (data.status !== 'success') {
                document.body.innerHTML = `<h2>${data.message}</h2>`;
                return;
            }

            const issue = data.data;

            // Fill issue details
            document.getElementById('issueTitle').textContent = issue.title;
            document.getElementById('issueCategory').textContent = issue.category;
            document.getElementById('issueDescription').textContent = issue.description;
            // Status styling
            const statusEl = document.getElementById('issueStatus');
            statusEl.textContent = issue.status;
            statusEl.className = ''; // Reset

            const statusLower = (issue.status || "").toLowerCase();
            if (statusLower === 'resolved') {
                statusEl.style.color = 'green';
                statusEl.style.fontWeight = 'bold';
            } else if (statusLower === 'rejected') {
                statusEl.style.color = 'red';
                statusEl.style.fontWeight = 'bold';
            } else if (statusLower === 'in progress') {
                statusEl.style.color = 'blue';
                statusEl.style.fontWeight = 'bold';
            } else if (issue.approved_by_admin === 1) {
                statusEl.textContent = "Approved & Assigned";
                statusEl.style.color = 'green';
                statusEl.style.fontWeight = 'bold';
            } else {
                statusEl.style.color = 'orange'; // Pending
            }
            document.getElementById('issueSeverity').textContent = issue.severity;
            document.getElementById('issueTimestamp').textContent = new Date(issue.timestamp).toLocaleString();

            // Reverse geocode to get human-readable location
            let locationName = '';
            try {
                const geoRes = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${issue.latitude}&lon=${issue.longitude}`);
                const geoData = await geoRes.json();
                locationName = geoData.display_name || '';
            } catch (err) {
                console.warn('Reverse geocoding failed', err);
            }
            document.getElementById('issueLocation').textContent = locationName;

            // Initialize map centered on issue
            const map = L.map('map').setView([issue.latitude, issue.longitude], 15);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);

            L.marker([issue.latitude, issue.longitude])
                .addTo(map)
                .bindPopup(`<b>${issue.title}</b><br>${locationName}`)
                .openPopup();
        })
        .catch(err => {
            console.error(err);
            document.body.innerHTML = "<h2>Failed to load issue details.</h2>";
        });
}
