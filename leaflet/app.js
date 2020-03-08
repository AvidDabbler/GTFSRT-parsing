import { leafletKey } from '/private.js'

// realtime library => https://github.com/perliedman/leaflet-realtime

const stopStyle = {
    "color": 'red',
    "radius": 10,
    "fillColor": 'red'
};
const vehicleStyle = {
    "color": 'red',
    "radius": 1,
    "fillColor": 'red'
};

const stopRender= (url, container, c) => {
    return L.realtime(url, {
        interval: 10 * 1000,
        getFeatureId: function(f) {
            return f.properties.id;
        },
        type: 'json',
        cache: true,
        container: container,
        onEachFeature(f, l){
            l.bindPopup(()=>{
                return `Stop Name: ${f.properties.popup}<br>
                        Stop Id: ${f.data.stop_id}<br>
                        StreetView: <a href="http://maps.google.com/maps?q=&layer=c&cbll=${f.data.stop_lat},${f.data.stop_lon}" target="_blank">Stop Location</a>
                        `;
            })
        },
        pointToLayer: function (feature, latlng) {
            return L.circle(latlng, {
                icon: stopStyle})
            }
    })
    .addTo(mymap);
}

const vehiclesRender= (url, container, c) => {
    return L.realtime(url, {
        interval: 10 * 1000,
        getFeatureId: function(f) {
            return f.properties.id;
        },
        type: 'json',
        cache: true,
        container: container,
        onEachFeature(f, l){
            l.bindPopup(()=>{
                return `Route Name: ${f.data.route_full_name}<br>
                        Vehicle Id: ${f.data.vehicleId}<br>
                        StreetView: <a href="http://maps.google.com/maps?q=&layer=c&cbll=${f.data.coordinates[1]},${f.data.coordinates[0]}" target="_blank">Vehicle Location</a>
                        `;
            })
        },

    }).addTo(mymap);
}

var mymap = L.map('map').setView([38.5967820198742, -90.24254675444169], 13),
    subgroup1 = L.featureGroup.subGroup(),
    realtime1 = vehiclesRender('vehicles.json', subgroup1),
    realtime2 = stopRender('stops.json', subgroup1);
       
L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: leafletKey,
}).addTo(mymap);

const showPosition = (position) => {
    let lat = position.coords.latitude;
    let long = position.coords.longitude;
    console.log("Latitude: " + lat + " Longitude: " + long);
    mymap.panTo(new L.LatLng(lat, long));
}

