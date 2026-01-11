// live.js
window.addEventListener('DOMContentLoaded', () => {
    const map = L.map('map').setView([24.8170, 93.9368], 12);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    const categoryFilter = document.getElementById('categoryFilter'); // optional dropdown

    // Fetch all issues
    function loadIssues(filterCategory = '') {
        fetch('http://127.0.0.1:8000/api/issues/')
            .then(res => res.json())
            .then(result => {
                if(result.status !== 'success') {
                    alert('Failed to load issues');
                    return;
                }

                // Clear existing markers
                if(window.issueMarkers){
                    window.issueMarkers.forEach(m => map.removeLayer(m));
                }
                window.issueMarkers = [];

                result.data.forEach(issue => {
                    // Filter by category if selected
                    if(filterCategory && issue.category !== filterCategory) return;

                    // Decide marker color based on severity
                    let color = 'green';
                    if(issue.severity >= 3) color = 'red';
                    else if(issue.severity === 2) color = 'yellow';

                    const marker = L.circleMarker([issue.latitude, issue.longitude], {
                        radius: 8,
                        fillColor: color,
                        color: '#000',
                        weight: 1,
                        opacity: 1,
                        fillOpacity: 0.8
                    }).addTo(map);

                    marker.bindPopup(
                        `<b>${issue.title}</b><br>
                        ${issue.description}<br>
                        <b>Category:</b> ${issue.category}<br>
                        <b>Severity:</b> ${issue.severity}<br>
                        <b>Status:</b> ${issue.status}`
                    );

                    window.issueMarkers.push(marker);
                });
            })
            .catch(err => {
                console.error(err);
                alert('Failed to fetch issues from server.');
            });
    }

    // Initial load
    loadIssues();

    // Optional: Category filter dropdown
    if(categoryFilter){
        categoryFilter.addEventListener('change', () => {
            loadIssues(categoryFilter.value);
        });
    }
});
