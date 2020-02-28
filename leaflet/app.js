import { leafletKey } from '/private.js'

const vehicles = 'vehicles.json';

let geojsonLayer = new L.geoJSON(null, {
    pointToLayer: (feature, latlng) => {
        return L.marker(latlng, { icon: customMarker })
        }
});
$.getJSON(vehicles, function(data) {
    geojsonLayer.addData(data.features);
});

var mymap = L.map('map').setView([38.5967820198742, -90.24254675444169], 13),
        realtime = L.realtime({
            url: 'vehicles.json',
            crossOrigin: true,
            type: 'json'
        }, {
            interval: 2 * 1000
        }).addTo(mymap);

       

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: leafletKey,
}).addTo(mymap);

const customMarker = new L.icon({
    iconUrl: "https://unpkg.com/leaflet@1.4.0/dist/images/marker-icon.png",
    iconSize: [25, 41],
    iconAnchor: [10, 41],
    popupAnchor: [2, -40]
  });

const showPosition = (position) => {
    let lat = position.coords.latitude;
    let long = position.coords.longitude;
    console.log("Latitude: " + lat + " Longitude: " + long);
    mymap.panTo(new L.LatLng(lat, long));
}

