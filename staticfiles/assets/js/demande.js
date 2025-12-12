
/**
 * SCRIPT COMPLET POUR LA GESTION DES CARTES ET GÉOLOCALISATION
 * Version complètement réécrite avec architecture moderne
 */

// =====================================================
// CONFIGURATION ET CONSTANTES
// =====================================================

const CONFIG = {
    // Coordonnées par défaut (Abidjan, Côte d'Ivoire)
    DEFAULT_COORDS: [5.3560, -4.0193],
    DEFAULT_ZOOM: 10,
    DETAIL_ZOOM: 16,
    
    // Limites géographiques de la Côte d'Ivoire
    BOUNDS: {
        southwest: [4.0, -8.0],
        northeast: [11.0, -2.0]
    },
    
    // Options de géolocalisation
    GEOLOCATION: {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 300000
    },
    
    // Configuration des cartes
    MAPS: {
        start: {
            containerId: 'start-map',
            inputId: 'adresse_depart',
            latId: 'latitude_depart',
            lngId: 'longitude_depart',
            buttonId: 'useCurrentLocationStart',
            toggleButtonId: 'toggleMapViewStart'
        },
        destination: {
            containerId: 'destination-map',
            inputId: 'adresse_destination',
            latId: 'latitude_destination',
            lngId: 'longitude_destination',
            buttonId: 'useCurrentLocationDestination',
            toggleButtonId: 'toggleMapViewDestination'
        }
    }
};

const MESSAGES = {
    SUCCESS: {
        LOCATION_FOUND: "Position récupérée avec succès !",
        ADDRESS_UPDATED: "Adresse mise à jour"
    },
    ERROR: {
        PERMISSION_DENIED: "L'accès à votre position a été refusé. Veuillez autoriser la géolocalisation.",
        POSITION_UNAVAILABLE: "Votre position n'a pas pu être déterminée. Vérifiez votre connexion.",
        TIMEOUT: "La récupération de votre position a pris trop de temps. Veuillez réessayer.",
        NOT_SUPPORTED: "La géolocalisation n'est pas supportée par votre navigateur.",
        GEOCODING_FAILED: "Impossible de récupérer l'adresse pour cette position.",
        OUT_OF_BOUNDS: "Votre position semble être en dehors de la Côte d'Ivoire.",
        INVALID_COORDINATES: "Coordonnées invalides détectées."
    }
};

// =====================================================
// UTILITAIRES
// =====================================================

class Utils {
    /**
     * Arrondir un nombre à 5 décimales
     */
    static roundTo5Decimals(num) {
        return Math.round(num * 100000) / 100000;
    }
    
    /**
     * Vérifier si les coordonnées sont dans les limites de la Côte d'Ivoire
     */
    static isWithinBounds(coords) {
        const [lat, lng] = coords;
        const { southwest, northeast } = CONFIG.BOUNDS;
        return lat >= southwest[0] && lat <= northeast[0] && 
               lng >= southwest[1] && lng <= northeast[1];
    }
    
    /**
     * Valider les coordonnées
     */
    static validateCoordinates(coords) {
        if (!Array.isArray(coords) || coords.length !== 2) return false;
        const [lat, lng] = coords;
        return !isNaN(lat) && !isNaN(lng) && 
               lat >= -90 && lat <= 90 && 
               lng >= -180 && lng <= 180;
    }
    
    /**
     * Créer un délai
     */
    static delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    /**
     * Logger avec timestamp
     */
    static log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        console[type](`[${timestamp}] ${message}`);
    }
}

// =====================================================
// GESTIONNAIRE D'INTERFACE UTILISATEUR
// =====================================================

class UIManager {
    constructor() {
        this.loadingOverlay = document.getElementById('loadingOverlay');
    }
    
    /**
     * Afficher/masquer l'overlay de chargement
     */
    toggleLoading(show) {
        if (this.loadingOverlay) {
            this.loadingOverlay.style.display = show ? 'flex' : 'none';
        }
    }
    
    /**
     * Gérer l'état d'un bouton
     */
    toggleButtonState(buttonId, isLoading) {
        const button = document.getElementById(buttonId);
        if (!button) return;
        
        if (isLoading) {
            button.classList.add('loading');
            button.disabled = true;
            button.setAttribute('data-original-html', button.innerHTML);
            button.innerHTML = '<i class="bx bx-loader-alt bx-spin me-1"></i>Localisation...';
        } else {
            button.classList.remove('loading');
            button.disabled = false;
            const originalHtml = button.getAttribute('data-original-html');
            if (originalHtml) {
                button.innerHTML = originalHtml;
                button.removeAttribute('data-original-html');
            }
        }
    }
    
    /**
     * Afficher une notification
     */
    showNotification(message, type = 'info') {
        Utils.log(message, type === 'error' ? 'error' : 'log');
        
        // Vous pouvez remplacer par votre système de notification
        if (type === 'error') {
            alert(`❌ ${message}`);
        } else if (type === 'success') {
            console.log(`✅ ${message}`);
        }
    }
    
    /**
     * Basculer la visibilité d'un élément
     */
    toggleVisibility(elementId, forceShow = null) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        if (forceShow !== null) {
            element.style.display = forceShow ? 'block' : 'none';
        } else {
            element.style.display = element.style.display === 'none' ? 'block' : 'none';
        }
    }
}

// =====================================================
// GESTIONNAIRE DE GÉOLOCALISATION
// =====================================================

class GeolocationManager {
    constructor(uiManager) {
        this.uiManager = uiManager;
    }
    
    /**
     * Vérifier le support de la géolocalisation
     */
    isSupported() {
        return 'geolocation' in navigator;
    }
    
    /**
     * Vérifier les permissions de géolocalisation
     */
    async checkPermissions() {
        if (!navigator.permissions) return 'unknown';
        
        try {
            const permission = await navigator.permissions.query({ name: 'geolocation' });
            return permission.state;
        } catch (error) {
            Utils.log('Impossible de vérifier les permissions', 'warn');
            return 'unknown';
        }
    }
    
    /**
     * Obtenir la position actuelle (version Promise)
     */
    getCurrentPosition() {
        return new Promise((resolve, reject) => {
            if (!this.isSupported()) {
                reject(new Error(MESSAGES.ERROR.NOT_SUPPORTED));
                return;
            }
            
            navigator.geolocation.getCurrentPosition(
                resolve,
                reject,
                CONFIG.GEOLOCATION
            );
        });
    }
    
    /**
     * Obtenir la position avec retry
     */
    async getCurrentPositionWithRetry(maxRetries = 2) {
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                const position = await this.getCurrentPosition();
                return position;
            } catch (error) {
                Utils.log(`Tentative ${attempt} échouée: ${error.message}`, 'warn');
                
                if (attempt === maxRetries) {
                    throw error;
                }
                
                await Utils.delay(1000 * attempt);
            }
        }
    }
    
    /**
     * Traiter les erreurs de géolocalisation
     */
    handleError(error) {
        let message;
        
        if (error.code) {
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    message = MESSAGES.ERROR.PERMISSION_DENIED;
                    break;
                case error.POSITION_UNAVAILABLE:
                    message = MESSAGES.ERROR.POSITION_UNAVAILABLE;
                    break;
                case error.TIMEOUT:
                    message = MESSAGES.ERROR.TIMEOUT;
                    break;
                default:
                    message = `Erreur de géolocalisation: ${error.message}`;
            }
        } else {
            message = error.message || 'Erreur inconnue';
        }
        
        this.uiManager.showNotification(message, 'error');
    }
}

// =====================================================
// GESTIONNAIRE DE CARTES YANDEX
// =====================================================

class YandexMapManager {
    constructor(config, uiManager, geolocationManager) {
        this.config = config;
        this.uiManager = uiManager;
        this.geolocationManager = geolocationManager;
        this.map = null;
        this.placemark = null;
        this.suggestView = null;
        this.isSatelliteView = false;
        this.elements = {};
    }
    
    /**
     * Initialiser les éléments DOM
     */
    initElements() {
        this.elements = {
            container: document.getElementById(this.config.containerId),
            input: document.getElementById(this.config.inputId),
            latInput: document.getElementById(this.config.latId),
            lngInput: document.getElementById(this.config.lngId),
            locationButton: document.getElementById(this.config.buttonId),
            toggleButton: document.getElementById(this.config.toggleButtonId)
        };
        
        // Vérifier que tous les éléments existent
        for (const [key, element] of Object.entries(this.elements)) {
            if (!element) {
                Utils.log(`Élément manquant: ${key} (${this.config[key + 'Id'] || this.config.containerId})`, 'error');
            }
        }
    }
    
    /**
     * Initialiser la carte Yandex
     */
    initMap() {
        if (!this.elements.container) return;
        
        // Masquer la carte initialement
        this.elements.container.style.display = 'none';
        
        // Créer la carte
        this.map = new ymaps.Map(this.elements.container, {
            center: CONFIG.DEFAULT_COORDS,
            zoom: CONFIG.DEFAULT_ZOOM,
            type: 'yandex#map'
        }, {
            restrictMapArea: [CONFIG.BOUNDS.southwest, CONFIG.BOUNDS.northeast]
        });
        
        // Créer le placemark
        this.placemark = new ymaps.Placemark(CONFIG.DEFAULT_COORDS, {
            balloonContent: 'Position par défaut'
        }, {
            draggable: true
        });
        
        this.map.geoObjects.add(this.placemark);
        
        Utils.log(`Carte initialisée: ${this.config.containerId}`);
    }
    
    /**
     * Initialiser l'autocomplétion
     */
    initAutocomplete() {
        if (!this.elements.input) return;
        
        this.suggestView = new ymaps.SuggestView(this.elements.input, {
            boundedBy: [CONFIG.BOUNDS.southwest, CONFIG.BOUNDS.northeast],
            strictBounds: true,
            results: 10
        });
        
        Utils.log(`Autocomplétion initialisée: ${this.config.inputId}`);
    }
    
    /**
     * Configurer les événements
     */
    setupEvents() {
        this.setupPlacemarkEvents();
        this.setupInputEvents();
        this.setupButtonEvents();
        this.setupAutocompleteEvents();
    }
    
    /**
     * Événements du placemark
     */
    setupPlacemarkEvents() {
        if (!this.placemark) return;
        
        this.placemark.events.add('dragend', async () => {
            try {
                const coords = this.placemark.geometry.getCoordinates();
                const roundedCoords = [
                    Utils.roundTo5Decimals(coords[0]),
                    Utils.roundTo5Decimals(coords[1])
                ];
                
                await this.updateLocationFromCoordinates(roundedCoords);
            } catch (error) {
                Utils.log(`Erreur lors du déplacement du marqueur: ${error.message}`, 'error');
            }
        });
    }
    
    /**
     * Événements de l'input
     */
    setupInputEvents() {
        if (!this.elements.input) return;
        
        // Afficher la carte au clic sur l'input
        this.elements.input.addEventListener('click', () => {
            this.showMap();
        });
        
        // Fermer la carte si clic en dehors
        document.addEventListener('click', (event) => {
            if (!this.elements.container.contains(event.target) && 
                event.target !== this.elements.input) {
                this.hideMap();
            }
        });
    }
    
    /**
     * Événements des boutons
     */
    setupButtonEvents() {
        // Bouton de géolocalisation
        if (this.elements.locationButton) {
            this.elements.locationButton.addEventListener('click', () => {
                this.useCurrentLocation();
            });
        }
        
        // Bouton de basculement de vue
        if (this.elements.toggleButton) {
            this.elements.toggleButton.addEventListener('click', () => {
                this.toggleMapView();
            });
        }
    }
    
    /**
     * Événements de l'autocomplétion
     */
    setupAutocompleteEvents() {
        if (!this.suggestView) return;
        
        this.suggestView.events.add('select', async (e) => {
            try {
                const selectedAddress = e.get('item').value;
                await this.geocodeAddress(selectedAddress);
            } catch (error) {
                Utils.log(`Erreur lors de la sélection d'adresse: ${error.message}`, 'error');
            }
        });
    }
    
    /**
     * Géocoder une adresse
     */
    async geocodeAddress(address) {
        try {
            const result = await ymaps.geocode(address, {
                boundedBy: [CONFIG.BOUNDS.southwest, CONFIG.BOUNDS.northeast],
                strictBounds: true
            });
            
            const firstGeoObject = result.geoObjects.get(0);
            if (!firstGeoObject) {
                throw new Error('Adresse introuvable');
            }
            
            const coords = firstGeoObject.geometry.getCoordinates();
            const roundedCoords = [
                Utils.roundTo5Decimals(coords[0]),
                Utils.roundTo5Decimals(coords[1])
            ];
            
            await this.updateMapAndForm(roundedCoords, address);
            this.showMap();
            
        } catch (error) {
            throw new Error(`Géocodage échoué: ${error.message}`);
        }
    }
    
    /**
     * Géocodage inverse (coordonnées vers adresse)
     */
    async reverseGeocode(coords) {
        try {
            const result = await ymaps.geocode(coords);
            const firstGeoObject = result.geoObjects.get(0);
            
            if (!firstGeoObject) {
                throw new Error('Aucune adresse trouvée');
            }
            
            return firstGeoObject.getAddressLine();
        } catch (error) {
            throw new Error(MESSAGES.ERROR.GEOCODING_FAILED);
        }
    }
    
    /**
     * Utiliser la position actuelle
     */
    async useCurrentLocation() {
        this.uiManager.toggleLoading(true);
        this.uiManager.toggleButtonState(this.config.buttonId, true);
        
        try {
            const position = await this.geolocationManager.getCurrentPositionWithRetry();
            
            const coords = [
                Utils.roundTo5Decimals(position.coords.latitude),
                Utils.roundTo5Decimals(position.coords.longitude)
            ];
            
            // Valider les coordonnées
            if (!Utils.validateCoordinates(coords)) {
                throw new Error(MESSAGES.ERROR.INVALID_COORDINATES);
            }
            
            if (!Utils.isWithinBounds(coords)) {
                throw new Error(MESSAGES.ERROR.OUT_OF_BOUNDS);
            }
            
            await this.updateLocationFromCoordinates(coords);
            this.showMap();
            
            this.uiManager.showNotification(MESSAGES.SUCCESS.LOCATION_FOUND, 'success');
            
        } catch (error) {
            this.geolocationManager.handleError(error);
        } finally {
            this.uiManager.toggleLoading(false);
            this.uiManager.toggleButtonState(this.config.buttonId, false);
        }
    }
    
    /**
     * Mettre à jour la localisation à partir de coordonnées
     */
    async updateLocationFromCoordinates(coords) {
        try {
            const address = await this.reverseGeocode(coords);
            await this.updateMapAndForm(coords, address);
        } catch (error) {
            // En cas d'échec du géocodage inverse, on met à jour quand même la carte
            await this.updateMapAndForm(coords, `${coords[0]}, ${coords[1]}`);
            Utils.log(`Géocodage inverse échoué: ${error.message}`, 'warn');
        }
    }
    
    /**
     * Mettre à jour la carte et le formulaire
     */
    async updateMapAndForm(coords, address) {
        // Mettre à jour la carte
        this.map.setCenter(coords, CONFIG.DETAIL_ZOOM);
        this.placemark.geometry.setCoordinates(coords);
        this.placemark.properties.set('balloonContent', address);
        
        // Mettre à jour le formulaire
        if (this.elements.input) this.elements.input.value = address;
        if (this.elements.latInput) this.elements.latInput.value = coords[0];
        if (this.elements.lngInput) this.elements.lngInput.value = coords[1];
        
        Utils.log(`Position mise à jour: ${address} (${coords.join(', ')})`);
    }
    
    /**
     * Basculer entre vue normale et satellite
     */
    toggleMapView() {
        if (!this.map || !this.elements.toggleButton) return;
        
        if (this.isSatelliteView) {
            this.map.setType('yandex#map');
            this.elements.toggleButton.innerHTML = '<i class="bx bx-map me-1"></i>Vue satellite';
        } else {
            this.map.setType('yandex#satellite');
            this.elements.toggleButton.innerHTML = '<i class="bx bx-map me-1"></i>Vue normale';
        }
        
        this.isSatelliteView = !this.isSatelliteView;
    }
    
    /**
     * Afficher la carte
     */
    showMap() {
        if (this.elements.container) {
            this.elements.container.style.display = 'block';
            if (this.map) {
                this.map.container.fitToViewport();
            }
        }
    }
    
    /**
     * Masquer la carte
     */
    hideMap() {
        if (this.elements.container) {
            this.elements.container.style.display = 'none';
        }
    }
    
    /**
     * Initialisation complète
     */
    async init() {
        try {
            this.initElements();
            this.initMap();
            this.initAutocomplete();
            this.setupEvents();
            
            Utils.log(`Carte initialisée avec succès: ${this.config.containerId}`);
        } catch (error) {
            Utils.log(`Erreur lors de l'initialisation de la carte: ${error.message}`, 'error');
        }
    }
}

// =====================================================
// GESTIONNAIRE PRINCIPAL DE L'APPLICATION
// =====================================================

class CourierApp {
    constructor() {
        this.uiManager = new UIManager();
        this.geolocationManager = new GeolocationManager(this.uiManager);
        this.maps = {};
    }
    
    /**
     * Initialiser l'application
     */
    async init() {
        try {
            Utils.log('Initialisation de l\'application...');
            
            // Vérifier les permissions de géolocalisation
            const permission = await this.geolocationManager.checkPermissions();
            if (permission === 'denied') {
                Utils.log('Géolocalisation refusée par l\'utilisateur', 'warn');
            }
            
            // Initialiser les cartes
            await this.initMaps();
            
            // Configurer les événements globaux
            this.setupGlobalEvents();
            
            Utils.log('Application initialisée avec succès !');
            
        } catch (error) {
            Utils.log(`Erreur lors de l'initialisation: ${error.message}`, 'error');
        }
    }
    
    /**
     * Initialiser les cartes
     */
    async initMaps() {
        for (const [mapName, mapConfig] of Object.entries(CONFIG.MAPS)) {
            try {
                const mapManager = new YandexMapManager(
                    mapConfig, 
                    this.uiManager, 
                    this.geolocationManager
                );
                
                await mapManager.init();
                this.maps[mapName] = mapManager;
                
            } catch (error) {
                Utils.log(`Erreur lors de l'initialisation de la carte ${mapName}: ${error.message}`, 'error');
            }
        }
    }
    
    /**
     * Configurer les événements globaux
     */
    setupGlobalEvents() {
        // Gérer les erreurs JavaScript globales
        window.addEventListener('error', (event) => {
            Utils.log(`Erreur JavaScript: ${event.error.message}`, 'error');
        });
        
        // Gérer les promesses rejetées
        window.addEventListener('unhandledrejection', (event) => {
            Utils.log(`Promesse rejetée: ${event.reason}`, 'error');
        });
    }
    
    /**
     * Obtenir une carte par nom
     */
    getMap(mapName) {
        return this.maps[mapName];
    }
    
    /**
     * Nettoyer les ressources
     */
    destroy() {
        // Nettoyer les cartes
        for (const map of Object.values(this.maps)) {
            if (map.map) {
                map.map.destroy();
            }
        }
        
        this.maps = {};
        Utils.log('Application nettoyée');
    }
}

// =====================================================
// INITIALISATION GLOBALE
// =====================================================

// Instance globale de l'application
let courierApp = null;

// Initialisation quand Yandex Maps est prêt
ymaps.ready(async function() {
    try {
        courierApp = new CourierApp();
        await courierApp.init();
        
        // Exposer l'application globalement pour le debugging
        window.courierApp = courierApp;
        
    } catch (error) {
        Utils.log(`Erreur fatale: ${error.message}`, 'error');
    }
});

// Nettoyage avant fermeture de la page
window.addEventListener('beforeunload', () => {
    if (courierApp) {
        courierApp.destroy();
    }
});
