export default function LeafletMap({ points, height = 320 }) {
  if (!points.length) return null;

  const safePoints = JSON.stringify(points).replace(/<\/script>/gi, '<\\/script>');

  const html = `<!DOCTYPE html>
<html><head>
<meta charset="utf-8"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>body{margin:0}#map{height:100vh;width:100%}</style>
</head><body>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const pts=${safePoints};
const map=L.map('map');
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap contributors'}).addTo(map);
const markers=pts.map(p=>L.marker([p.lat,p.lng]).addTo(map).bindPopup(p.url?'<a href="'+p.url+'" target="_top">'+p.label+'</a>':p.label));
if(pts.length===1){map.setView([pts[0].lat,pts[0].lng],13);}
else{map.fitBounds(L.featureGroup(markers).getBounds().pad(0.2));}
</script>
</body></html>`;

  return (
    <div className="card card-map mt-4">
      <iframe
        title="Map"
        width="100%"
        height={height}
        className="iframe-clean"
        srcDoc={html}
      />
    </div>
  );
}
