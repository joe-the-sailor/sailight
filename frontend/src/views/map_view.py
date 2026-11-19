"""
Kartenansicht mit GIS-Funktionalität
Verwendet QWebEngineView für die Darstellung von OpenStreetMap/Leaflet
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QToolButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QSize
from typing import Optional, Dict, Any, List
import logging
import json

from frontend.src.config import config
from frontend.src.utils.api_client import api_client
from frontend.src.utils.auth import auth_manager

logger = logging.getLogger("sailight.map_view")


class MapView(QWidget):
    """Kartenansicht mit GIS-Funktionalität"""
    
    # Signale
    feature_selected = pyqtSignal(dict)
    map_loaded = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialisiert die Kartenansicht"""
        super().__init__(parent)
        
        # Fenster-Eigenschaften
        self.setWindowTitle("Karte")
        self.setObjectName("MapView")
        
        # Hauptlayout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        # Toolbar erstellen
        self._toolbar = self._create_toolbar()
        self._main_layout.addWidget(self._toolbar)
        
        # WebEngineView für die Karte
        self._web_view = QWebEngineView(self)
        self._web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self._main_layout.addWidget(self._web_view)
        
        # HTML-Inhalt laden
        self._load_map_html()
        
        # JavaScript-Bridge einrichten
        self._setup_javascript_bridge()
        
        # Daten laden
        self._load_initial_data()
        
        logger.info("Kartenansicht initialisiert")
    
    def _create_toolbar(self) -> QToolBar:
        """Erstellt die Toolbar für die Karte"""
        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(20, 20))
        
        # Zoom In
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setIcon(QIcon.fromTheme("zoom-in"))
        zoom_in_action.setToolTip("Vergrößern")
        zoom_in_action.triggered.connect(self._zoom_in)
        toolbar.addAction(zoom_in_action)
        
        # Zoom Out
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setIcon(QIcon.fromTheme("zoom-out"))
        zoom_out_action.setToolTip("Verkleinern")
        zoom_out_action.triggered.connect(self._zoom_out)
        toolbar.addAction(zoom_out_action)
        
        # Reset Zoom
        reset_zoom_action = QAction("Reset Zoom", self)
        reset_zoom_action.setIcon(QIcon.fromTheme("view-refresh"))
        reset_zoom_action.setToolTip("Zoom zurücksetzen")
        reset_zoom_action.triggered.connect(self._reset_zoom)
        toolbar.addAction(reset_zoom_action)
        
        toolbar.addSeparator()
        
        # Layer-Steuerung
        self._layer_menu = toolbar.addMenu("Layer")
        
        # Schaltschränke Layer
        self._cabinets_layer_action = self._layer_menu.addAction("Schaltschränke")
        self._cabinets_layer_action.setCheckable(True)
        self._cabinets_layer_action.setChecked(True)
        self._cabinets_layer_action.triggered.connect(self._toggle_cabinets_layer)
        
        # Masten Layer
        self._poles_layer_action = self._layer_menu.addAction("Masten")
        self._poles_layer_action.setCheckable(True)
        self._poles_layer_action.setChecked(True)
        self._poles_layer_action.triggered.connect(self._toggle_poles_layer)
        
        # Leuchtstellen Layer
        self._light_points_layer_action = self._layer_menu.addAction("Leuchtstellen")
        self._light_points_layer_action.setCheckable(True)
        self._light_points_layer_action.setChecked(True)
        self._light_points_layer_action.triggered.connect(self._toggle_light_points_layer)
        
        # Leitungsgruppen Layer
        self._circuit_groups_layer_action = self._layer_menu.addAction("Leitungsgruppen")
        self._circuit_groups_layer_action.setCheckable(True)
        self._circuit_groups_layer_action.setChecked(True)
        self._circuit_groups_layer_action.triggered.connect(self._toggle_circuit_groups_layer)
        
        toolbar.addSeparator()
        
        # Standort
        locate_action = QAction("Zu Luxemburg", self)
        locate_action.setIcon(QIcon.fromTheme("go-home"))
        locate_action.setToolTip("Zurück zu Luxemburg")
        locate_action.triggered.connect(self._locate_to_luxembourg)
        toolbar.addAction(locate_action)
        
        return toolbar
    
    def _load_map_html(self):
        """Lädt den HTML-Inhalt für die Karte"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sailight Map</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background-color: {config.BACKGROUND_COLOR};
                }}
                #map {{
                    width: 100%;
                    height: 100%;
                }}
                .leaflet-control-attribution {{
                    background-color: rgba(0, 0, 0, 0.7) !important;
                    color: white !important;
                }}
                .leaflet-popup-content {{
                    background-color: {config.SURFACE_COLOR} !important;
                    color: {config.TEXT_COLOR} !important;
                }}
                .leaflet-popup-content-wrapper {{
                    background-color: {config.SURFACE_COLOR} !important;
                    color: {config.TEXT_COLOR} !important;
                    border: 1px solid {config.BORDER_COLOR} !important;
                }}
                .leaflet-popup-tip {{
                    background-color: {config.SURFACE_COLOR} !important;
                }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
                // Karte initialisieren
                const map = L.map('map').setView([{config.GIS_DEFAULT_CENTER[1]}, {config.GIS_DEFAULT_CENTER[0]}], {config.GIS_DEFAULT_ZOOM});
                
                // OpenStreetMap Layer
                const osmLayer = L.tileLayer('{config.MAP_TILE_URL}', {{
                    attribution: '{config.MAP_ATTRIBUTION}'
                }}).addTo(map);
                
                // Layer-Gruppen
                const cabinetsLayer = L.layerGroup();
                const polesLayer = L.layerGroup();
                const lightPointsLayer = L.layerGroup();
                const circuitGroupsLayer = L.layerGroup();
                
                // Layer zur Karte hinzufügen
                cabinetsLayer.addTo(map);
                polesLayer.addTo(map);
                lightPointsLayer.addTo(map);
                circuitGroupsLayer.addTo(map);
                
                // Marker-Cluster (für viele Punkte)
                const markers = L.markerClusterGroup({{
                    maxClusterRadius: 50,
                    spiderfyOnMaxZoom: true,
                    showCoverageOnHover: false
                }});
                
                // Funktion zum Hinzufügen von Markern
                function addMarker(lat, lng, icon, popupContent, data) {{
                    const marker = L.marker([lat, lng], {{icon: icon}})
                        .bindPopup(popupContent)
                        .on('click', function() {{
                            // Signal an Python senden
                            if (window.pywebview) {{
                                window.pywebview.api.featureSelected(data);
                            }}
                        }});
                    markers.addLayer(marker);
                    return marker;
                }}
                
                // Funktion zum Hinzufügen von Leuchtstellen
                function addLightPoint(lat, lng, data) {{
                    const icon = L.icon({{
                        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41],
                        popupAnchor: [1, -34]
                    }});
                    
                    const popupContent = `
                        <b>Leuchtstelle: ${{data.identifier}}</b><br>
                        Status: ${{data.status}}<br>
                        Typ: ${{data.light_type || 'N/A'}}<br>
                        Leistung: ${{data.power || 'N/A'}} W
                    `;
                    
                    const marker = addMarker(lat, lng, icon, popupContent, {{
                        type: 'light_point',
                        ...data
                    }});
                    
                    lightPointsLayer.addLayer(marker);
                    return marker;
                }}
                
                // Funktion zum Hinzufügen von Masten
                function addPole(lat, lng, data) {{
                    const icon = L.icon({{
                        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-gray.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41],
                        popupAnchor: [1, -34]
                    }});
                    
                    const popupContent = `
                        <b>Mast: ${{data.identifier}}</b><br>
                        Höhe: ${{data.height || 'N/A'}} m<br>
                        Material: ${{data.material || 'N/A'}}<br>
                        Status: ${{data.status}}
                    `;
                    
                    const marker = addMarker(lat, lng, icon, popupContent, {{
                        type: 'pole',
                        ...data
                    }});
                    
                    polesLayer.addLayer(marker);
                    return marker;
                }}
                
                // Funktion zum Hinzufügen von Schaltschränken
                function addCabinet(lat, lng, data) {{
                    const icon = L.icon({{
                        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41],
                        popupAnchor: [1, -34]
                    }});
                    
                    const popupContent = `
                        <b>Schaltschrank: ${{data.identifier}}</b><br>
                        Name: ${{data.name}}<br>
                        Spannung: ${{data.voltage_level || 'N/A'}}<br>
                        Status: ${{data.status}}
                    `;
                    
                    const marker = addMarker(lat, lng, icon, popupContent, {{
                        type: 'cabinet',
                        ...data
                    }});
                    
                    cabinetsLayer.addLayer(marker);
                    return marker;
                }}
                
                // Funktion zum Hinzufügen von Leitungsgruppen
                function addCircuitGroup(lat, lng, data) {{
                    const icon = L.icon({{
                        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41],
                        popupAnchor: [1, -34]
                    }});
                    
                    const popupContent = `
                        <b>Leitungsgruppe: ${{data.identifier}}</b><br>
                        Name: ${{data.name}}<br>
                        Phase: ${{data.phase || 'N/A'}}<br>
                        Status: ${{data.status}}
                    `;
                    
                    const marker = addMarker(lat, lng, icon, popupContent, {{
                        type: 'circuit_group',
                        ...data
                    }});
                    
                    circuitGroupsLayer.addLayer(marker);
                    return marker;
                }}
                
                // Funktion zum Zentrieren der Karte
                function centerMap(lat, lng, zoom) {{
                    map.setView([lat, lng], zoom);
                }}
                
                // Funktion zum Ändern des Zooms
                function setZoom(zoom) {{
                    map.setZoom(zoom);
                }}
                
                // Funktion zum Hinzufügen von GeoJSON
                function addGeoJSON(geojson, layer) {{
                    L.geoJSON(geojson, {{
                        pointToLayer: function(feature, latlng) {{
                            return L.circleMarker(latlng, {{
                                radius: 8,
                                fillColor: "#ff7800",
                                color: "#000",
                                weight: 1,
                                opacity: 1,
                                fillOpacity: 0.8
                            }});
                        }}
                    }}).addTo(layer);
                }}
                
                // Funktion zum Entfernen aller Marker
                function clearLayer(layer) {{
                    layer.clearLayers();
                }}
                
                // Funktion zum Entfernen aller Marker
                function clearAll() {{
                    cabinetsLayer.clearLayers();
                    polesLayer.clearLayers();
                    lightPointsLayer.clearLayers();
                    circuitGroupsLayer.clearLayers();
                    markers.clearLayers();
                }}
                
                // Funktion zum Anzeigen von Feature-Details
                function showFeatureDetails(feature) {{
                    console.log('Feature selected:', feature);
                }}
                
                // Funktion zum Aktualisieren der Layer-Sichtbarkeit
                function setLayerVisibility(layerName, visible) {{
                    if (layerName === 'cabinets') {{
                        if (visible) {{
                            cabinetsLayer.addTo(map);
                        }} else {{
                            map.removeLayer(cabinetsLayer);
                        }}
                    }} else if (layerName === 'poles') {{
                        if (visible) {{
                            polesLayer.addTo(map);
                        }} else {{
                            map.removeLayer(polesLayer);
                        }}
                    }} else if (layerName === 'light_points') {{
                        if (visible) {{
                            lightPointsLayer.addTo(map);
                        }} else {{
                            map.removeLayer(lightPointsLayer);
                        }}
                    }} else if (layerName === 'circuit_groups') {{
                        if (visible) {{
                            circuitGroupsLayer.addTo(map);
                        }} else {{
                            map.removeLayer(circuitGroupsLayer);
                        }}
                    }}
                }}
                
                // Funktion zum Hinzufügen von Polylinien (für Leitungsgruppen)
                function addPolyline(coordinates, data) {{
                    const polyline = L.polyline(coordinates, {{
                        color: '#FFA500',
                        weight: 3,
                        opacity: 0.7
                    }}).bindPopup(`<b>Leitungsgruppe: ${{data.identifier}}</b>`);
                    
                    circuitGroupsLayer.addLayer(polyline);
                    return polyline;
                }}
                
                // API für Python
                window.sailightMap = {{
                    addLightPoint: addLightPoint,
                    addPole: addPole,
                    addCabinet: addCabinet,
                    addCircuitGroup: addCircuitGroup,
                    centerMap: centerMap,
                    setZoom: setZoom,
                    addGeoJSON: addGeoJSON,
                    clearLayer: clearLayer,
                    clearAll: clearAll,
                    setLayerVisibility: setLayerVisibility,
                    addPolyline: addPolyline
                }};
            </script>
        </body>
        </html>
        """
        
        self._web_view.setHtml(html)
    
    def _setup_javascript_bridge(self):
        """Richtet die JavaScript-Bridge ein"""
        # JavaScript-Objekt für die Kommunikation mit Python
        self._web_view.page().setWebChannel(self)
    
    def _load_initial_data(self):
        """Lädt die anfänglichen Daten"""
        if not auth_manager.is_authenticated:
            return
        
        # Leuchtstellen laden
        self._load_light_points()
        
        # Masten laden
        self._load_poles()
        
        # Schaltschränke laden
        self._load_cabinets()
        
        # Leitungsgruppen laden
        self._load_circuit_groups()
    
    async def _load_light_points(self):
        """Lädt die Leuchtstellen von der API"""
        response = await api_client.get(
            f"{config.API_V1_STR}/light-points",
            params={"page_size": 10000}
        )
        
        if response.success and response.data:
            for lp in response.data.get("items", []):
                if lp.get("geom") and lp.get("geom", {}).get("coordinates"):
                    coords = lp["geom"]["coordinates"]
                    self._web_view.page().runJavaScript(
                        f"window.sailightMap.addLightPoint({coords[1]}, {coords[0]}, {json.dumps(lp)});"
                    )
    
    async def _load_poles(self):
        """Lädt die Masten von der API"""
        response = await api_client.get(
            f"{config.API_V1_STR}/poles",
            params={"page_size": 10000}
        )
        
        if response.success and response.data:
            for pole in response.data.get("items", []):
                if pole.get("geom") and pole.get("geom", {}).get("coordinates"):
                    coords = pole["geom"]["coordinates"]
                    self._web_view.page().runJavaScript(
                        f"window.sailightMap.addPole({coords[1]}, {coords[0]}, {json.dumps(pole)});"
                    )
    
    async def _load_cabinets(self):
        """Lädt die Schaltschränke von der API"""
        response = await api_client.get(
            f"{config.API_V1_STR}/cabinets",
            params={"page_size": 10000}
        )
        
        if response.success and response.data:
            for cabinet in response.data.get("items", []):
                if cabinet.get("geom") and cabinet.get("geom", {}).get("coordinates"):
                    coords = cabinet["geom"]["coordinates"]
                    self._web_view.page().runJavaScript(
                        f"window.sailightMap.addCabinet({coords[1]}, {coords[0]}, {json.dumps(cabinet)});"
                    )
    
    async def _load_circuit_groups(self):
        """Lädt die Leitungsgruppen von der API"""
        response = await api_client.get(
            f"{config.API_V1_STR}/circuit-groups",
            params={"page_size": 10000}
        )
        
        if response.success and response.data:
            for cg in response.data.get("items", []):
                if cg.get("geom") and cg.get("geom", {}).get("coordinates"):
                    coords = cg["geom"]["coordinates"]
                    self._web_view.page().runJavaScript(
                        f"window.sailightMap.addCircuitGroup({coords[1]}, {coords[0]}, {json.dumps(cg)});"
                    )
    
    def _zoom_in(self):
        """Vergrößert die Karte"""
        self._web_view.page().runJavaScript("window.sailightMap.setZoom(map.getZoom() + 1);")
    
    def _zoom_out(self):
        """Verkleinert die Karte"""
        self._web_view.page().runJavaScript("window.sailightMap.setZoom(map.getZoom() - 1);")
    
    def _reset_zoom(self):
        """Setzt den Zoom zurück"""
        self._web_view.page().runJavaScript(
            f"window.sailightMap.centerMap({config.GIS_DEFAULT_CENTER[1]}, {config.GIS_DEFAULT_CENTER[0]}, {config.GIS_DEFAULT_ZOOM});"
        )
    
    def _locate_to_luxembourg(self):
        """Zentriert die Karte auf Luxemburg"""
        self._web_view.page().runJavaScript(
            f"window.sailightMap.centerMap({config.GIS_DEFAULT_CENTER[1]}, {config.GIS_DEFAULT_CENTER[0]}, {config.GIS_DEFAULT_ZOOM});"
        )
    
    def _toggle_cabinets_layer(self, checked: bool):
        """Schaltet den Schaltschränke-Layer um"""
        self._web_view.page().runJavaScript(f"window.sailightMap.setLayerVisibility('cabinets', {str(checked).lower()});")
    
    def _toggle_poles_layer(self, checked: bool):
        """Schaltet den Masten-Layer um"""
        self._web_view.page().runJavaScript(f"window.sailightMap.setLayerVisibility('poles', {str(checked).lower()});")
    
    def _toggle_light_points_layer(self, checked: bool):
        """Schaltet den Leuchtstellen-Layer um"""
        self._web_view.page().runJavaScript(f"window.sailightMap.setLayerVisibility('light_points', {str(checked).lower()});")
    
    def _toggle_circuit_groups_layer(self, checked: bool):
        """Schaltet den Leitungsgruppen-Layer um"""
        self._web_view.page().runJavaScript(f"window.sailightMap.setLayerVisibility('circuit_groups', {str(checked).lower()});")
    
    def center_on_feature(self, feature: Dict[str, Any]):
        """Zentriert die Karte auf ein bestimmtes Feature"""
        if feature.get("geom") and feature.get("geom", {}).get("coordinates"):
            coords = feature["geom"]["coordinates"]
            self._web_view.page().runJavaScript(
                f"window.sailightMap.centerMap({coords[1]}, {coords[0]}, 16);"
            )
    
    def add_feature(self, feature: Dict[str, Any]):
        """Fügt ein Feature zur Karte hinzu"""
        feature_type = feature.get("type")
        
        if feature_type == "light_point":
            self._web_view.page().runJavaScript(
                f"window.sailightMap.addLightPoint({feature.get('geom', {{'coordinates': [0, 0]}}).get('coordinates', [0, 0])[1]}, "
                f"{feature.get('geom', {{'coordinates': [0, 0]}}).get('coordinates', [0, 0])[0]}, {json.dumps(feature)});"
            )
        elif feature_type == "pole":
            self._web_view.page().runJavaScript(
                f"window.sailightMap.addPole({feature.get('geom', {{'coordinates': [0, 0]}}).get('coordinates', [0, 0])[1]}, "
                f"{feature.get('geom', {{'coordinates': [0, 0]}}).get('coordinates', [0, 0])[0]}, {json.dumps(feature)});"
            )
        elif feature_type == "cabinet":
            self._web_view.page().runJavaScript(
                f"window.sailightMap.addCabinet({feature.get('geom', {{'coordinates': [0, 0]}}).get('coordinates', [0, 0])[1]}, "
                f"{feature.get('geom', {{'coordinates': [0, 0]}}).get('coordinates', [0, 0])[0]}, {json.dumps(feature)});"
            )
        elif feature_type == "circuit_group":
            self._web_view.page().runJavaScript(
                f"window.sailightMap.addCircuitGroup({feature.get('geom', {{'coordinates': [0, 0]}}).get('coordinates', [0, 0])[1]}, "
                f"{feature.get('geom', {{'coordinates': [0, 0]}}).get('coordinates', [0, 0])[0]}, {json.dumps(feature)});"
            )
    
    def clear_all_features(self):
        """Löscht alle Features von der Karte"""
        self._web_view.page().runJavaScript("window.sailightMap.clearAll();")
    
    def cleanup(self):
        """Bereinigt Ressourcen"""
        self._web_view.deleteLater()
    
    def closeEvent(self, event):
        """Wird aufgerufen, wenn das Widget geschlossen wird"""
        self.cleanup()
        event.accept()
