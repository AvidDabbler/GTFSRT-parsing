const vehicles = 'vehicles.json';


var mymap = L.map('map').setView([38.5967820198742, -90.24254675444169], 13);

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1Ijoid2FsdGVyaiIsImEiOiJjazZ0cjZ5M2gwMGxrM21zMmt4Z3p4OWNlIn0.7no-7gXBw5azPXlETiK05A'
}).addTo(mymap);

const customMarker = new L.icon({
    iconUrl: "https://unpkg.com/leaflet@1.4.0/dist/images/marker-icon.png",
    iconSize: [25, 41],
    iconAnchor: [10, 41],
    popupAnchor: [2, -40]
  });

const getLocation = () => {
    // LOAD IN GEOJSON DATA
    var geojsonLayer = new L.geoJSON(null, {
        pointToLayer: (feature, latlng) => {
            return L.marker(latlng, { icon: customMarker })
            }
    });

    $.getJSON(vehicles, function(data) {
        geojsonLayer.addData(data.features);
    });

    geojsonLayer.addTo(mymap);

    // FIND THEM!!! PUT THE DOT ON THEM YOU WILL!!!
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else { 
        x.innerHTML = "Geolocation is not supported by this browser.";
    }
}

const showPosition = (position) => {
    let lat = position.coords.latitude;
    let long = position.coords.longitude;
    console.log("Latitude: " + lat + " Longitude: " + long);
    mymap.panTo(new L.LatLng(lat, long));
}



getLocation();

