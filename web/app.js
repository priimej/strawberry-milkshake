// Initializes the map, sets up the elements, event listeners, and readys the map.
const map = new maplibregl.Map({
    container: 'map',
    style: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
    center: [-74.5, 40],
    zoom: 12
});

const startInput = document.getElementById('start');
const endInput = document.getElementById('end');
const calcBtn = document.getElementById('calc-btn');
const resultsDiv = document.getElementById('results');

// Track markers and selection state
let startMarker = null;
let endMarker = null;
let selectingStart = false;
let userLat = null;
let userLng = null;


// Get user location and center map
function getUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            userLat = position.coords.latitude;
            userLng = position.coords.longitude;
            
            map.flyTo({
                center: [lng, lat],
                zoom: 15,
                duration: 1000
            });
            
            // Automatically set start marker to user location\
            if (startMarker) startMarker.remove();
            startMarker = new maplibregl.Marker({ color: 'green' })
                .setLngLat([lng, lat])
                .addTo(map);
            
            startInput.value = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;

            
            console.log('Located at:', lat, lng);
        }, function(error) {
            console.error('Geolocation error:', error);
        });
    } else {
        console.log('Geolocation not supported');
    }
}

// Calculate distance between two points (Haversine formula)
function calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// Click on map to select start/end
map.on('click', function(e) {
    const lat = e.lngLat.lat;
    const lng = e.lngLat.lng;

    if (selectingStart) {
        // Remove old start marker
        if (startMarker) startMarker.remove();
        
        // Add new start marker
        startMarker = new maplibregl.Marker({ color: 'green' })
            .setLngLat([lng, lat])
            .addTo(map);
        
        startInput.value = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
        selectingStart = false;
        console.log('Start set:', lat, lng);
    } else {
        // Check if start marker exists
        if (!startMarker) {
            alert('Please set start location first');
            return;
        }
        
        // Get start marker coordinates
        const startCoords = startMarker.getLngLat();
        const distance = calculateDistance(startCoords.lat, startCoords.lng, lat, lng);
        
        // Check max distance (3km)
        if (distance > 3) {
            alert(`Too far! Max 3km. You selected ${distance.toFixed(2)}km`);
            return;
        }
        
        // Remove old end marker
        if (endMarker) endMarker.remove();
        
        // Add new end marker
        endMarker = new maplibregl.Marker({ color: 'red' })
            .setLngLat([lng, lat])
            .addTo(map);
        
        endInput.value = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
        console.log('End set:', lat, lng, `Distance: ${distance.toFixed(2)}km`);
        }
});

// Button to start selecting start location
startInput.addEventListener('focus', function() {
    selectingStart = true;
    startInput.placeholder = 'Click on map to select...';
});

// Button to start selecting end location
endInput.addEventListener('focus', function() {
    selectingStart = false;
    endInput.placeholder = 'Click on map to select...';
});

map.on('load', function() {
    console.log('Map loaded');
    getUserLocation();
});

// Tracks mouse coordinates
map.on('mousemove', (e) => {
    document.getElementById('info').innerHTML =
        `Coordinates: ${JSON.stringify(e.lngLat.wrap())}`;
});

//Sends the python backend the cords
calcBtn.addEventListener('click', function() {
    console.log('Calculate clicked');
    
    if (!startMarker || !endMarker) {
        alert('Please set both start and end locations');
        return;
    }
    
    const startCoords = startMarker.getLngLat();
    const endCoords = endMarker.getLngLat();
    
    fetch('http://localhost:8000/main', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            start: { lat: startCoords.lat, lng: startCoords.lng },
            end: { lat: endCoords.lat, lng: endCoords.lng }
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        console.log('Route data:', data);
    })
    .catch(error => console.error('Error:', error));
});

// Show results
resultsDiv.style.display = 'block';
document.getElementById('result-distance').textContent = data.distance_km.toFixed(2) + ' km';
document.getElementById('result-time').textContent = Math.round(data.skate_time_min) + ' min';


