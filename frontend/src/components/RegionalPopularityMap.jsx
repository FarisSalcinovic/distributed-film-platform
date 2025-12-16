import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, GeoJSON } from 'react-leaflet';
import { analyticsAPI } from '../services/etlApi';
import { FaFilm, FaStar, FaMapMarkerAlt } from 'react-icons/fa';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Leaflet icon fix
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet/dist/images/marker-shadow.png'
});

// Custom marker icon
const customIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet/dist/images/marker-icon.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowUrl: 'https://unpkg.com/leaflet/dist/images/marker-shadow.png',
  shadowSize: [41, 41]
});

// Active marker icon (kada je selektovano)
const activeIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowUrl: 'https://unpkg.com/leaflet/dist/images/marker-shadow.png',
  shadowSize: [41, 41]
});

const RegionalPopularityMap = () => {
  const [countries, setCountries] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [popularFilms, setPopularFilms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mapLoading, setMapLoading] = useState(false);
  const mapRef = useRef(null);
  const markersRef = useRef({});

  // Fallback countries data ako API ne radi
  const fallbackCountries = [
    { country_code: 'US', country_name: 'United States', latitude: 39.8283, longitude: -98.5795, capital: 'Washington DC' },
    { country_code: 'GB', country_name: 'United Kingdom', latitude: 55.3781, longitude: -3.4360, capital: 'London' },
    { country_code: 'FR', country_name: 'France', latitude: 46.2276, longitude: 2.2137, capital: 'Paris' },
    { country_code: 'DE', country_name: 'Germany', latitude: 51.1657, longitude: 10.4515, capital: 'Berlin' },
    { country_code: 'JP', country_name: 'Japan', latitude: 36.2048, longitude: 138.2529, capital: 'Tokyo' },
    { country_code: 'IT', country_name: 'Italy', latitude: 41.8719, longitude: 12.5674, capital: 'Rome' },
    { country_code: 'ES', country_name: 'Spain', latitude: 40.4637, longitude: -3.7492, capital: 'Madrid' },
    { country_code: 'CA', country_name: 'Canada', latitude: 56.1304, longitude: -106.3468, capital: 'Ottawa' },
    { country_code: 'AU', country_name: 'Australia', latitude: -25.2744, longitude: 133.7751, capital: 'Canberra' },
    { country_code: 'BR', country_name: 'Brazil', latitude: -14.2350, longitude: -51.9253, capital: 'Brasília' },
    { country_code: 'IN', country_name: 'India', latitude: 20.5937, longitude: 78.9629, capital: 'New Delhi' },
    { country_code: 'CN', country_name: 'China', latitude: 35.8617, longitude: 104.1954, capital: 'Beijing' },
    { country_code: 'RU', country_name: 'Russia', latitude: 61.5240, longitude: 105.3188, capital: 'Moscow' },
    { country_code: 'MX', country_name: 'Mexico', latitude: 23.6345, longitude: -102.5528, capital: 'Mexico City' },
    { country_code: 'KR', country_name: 'South Korea', latitude: 35.9078, longitude: 127.7669, capital: 'Seoul' },
  ];

  useEffect(() => {
    loadCountries();
  }, []);

  const loadCountries = async () => {
    setLoading(true);
    try {
      // Probaj da dobiješ podatke iz API-ja
      const data = await analyticsAPI.getFilmsWithLocations(50);

      // Proveri strukturu odgovora
      if (data.regions && data.regions.length > 0) {
        setCountries(data.regions);
      } else if (data.films && data.films.length > 0) {
        // Ako API vraća filmove, ekstraktuj jedinstvene zemlje
        const uniqueCountries = [];
        const countryMap = new Map();

        data.films.forEach(film => {
          if (film.country_code && !countryMap.has(film.country_code)) {
            countryMap.set(film.country_code, true);
            uniqueCountries.push({
              country_code: film.country_code,
              country_name: film.country_name || film.country_code,
              latitude: film.latitude || getRandomCoordinate(film.country_code),
              longitude: film.longitude || getRandomCoordinate(film.country_code, false)
            });
          }
        });

        setCountries(uniqueCountries.length > 0 ? uniqueCountries : fallbackCountries);
      } else {
        // Fallback na hardkodirane zemlje
        console.log('Using fallback countries data');
        setCountries(fallbackCountries);
      }
    } catch (err) {
      console.error('Failed to load countries data:', err);
      setCountries(fallbackCountries);
    }
    setLoading(false);
  };

  // Helper funkcija za koordinate ako nema u podacima
  const getRandomCoordinate = (seed, isLatitude = true) => {
    const hash = seed.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    if (isLatitude) {
      return 20 + (hash % 50) - 25; // Između -5 i 45
    }
    return -100 + (hash % 200) - 100; // Između -200 i 0
  };

  const handleCountryClick = async (country) => {
  console.log('🎯 1. Počinje handleCountryClick za:', country.country_code, country.country_name);

  setMapLoading(true);
  setSelectedCountry(country);

  try {
    console.log('🎯 2. Proveravam analyticsAPI:', analyticsAPI);
    console.log('🎯 3. Proveravam getPopularFilmsByRegion:', analyticsAPI.getPopularFilmsByRegion);

    console.log(`🎯 4. Pozivam API za region: ${country.country_code}...`);

    // ⭐ VAŽNO: Koristite country_code kao region parametar
    const filmsResponse = await analyticsAPI.getPopularFilmsByRegion(country.country_code, 3);

    console.log('✅ 5. Dobio API odgovor:', filmsResponse);
    console.log('✅ Tip odgovora:', typeof filmsResponse);
    console.log('✅ Keys u odgovoru:', Object.keys(filmsResponse || {}));

    // Proverite različite moguće strukture odgovora
    let films = [];

    if (filmsResponse.films && Array.isArray(filmsResponse.films)) {
      console.log('✅ Pronađen films array sa', filmsResponse.films.length, 'filmova');
      films = filmsResponse.films;
    } else if (filmsResponse.movies && Array.isArray(filmsResponse.movies)) {
      console.log('✅ Pronađen movies array sa', filmsResponse.movies.length, 'filmova');
      films = filmsResponse.movies;
    } else if (Array.isArray(filmsResponse)) {
      console.log('✅ Odgovor je direktno array sa', filmsResponse.length, 'filmova');
      films = filmsResponse;
    } else if (filmsResponse.data && Array.isArray(filmsResponse.data)) {
      console.log('✅ Pronađen data array sa', filmsResponse.data.length, 'filmova');
      films = filmsResponse.data;
    } else {
      console.warn('⚠️ Neočekivana struktura odgovora. Pokušavam da ekstraktujem filmove...');

      // Probajte da nađete bilo koji array u odgovoru
      for (const key in filmsResponse) {
        if (Array.isArray(filmsResponse[key])) {
          console.log('✅ Pronađen array u propertiju:', key, 'sa', filmsResponse[key].length, 'elementa');
          films = filmsResponse[key];
          break;
        }
      }

      if (films.length === 0) {
        console.warn('⚠️ Nije pronađen nijedan array u odgovoru');
      }
    }

    console.log('✅ 6. Postavljam filmove:', films.length);
    setPopularFilms(films);

    // Ažuriraj marker ikonu
    if (markersRef.current[country.country_code]) {
      markersRef.current[country.country_code].setIcon(activeIcon);
    }

  } catch (err) {
    console.error('❌ GREŠKA u handleCountryClick:', err);
    console.error('❌ Error details:', err);
    console.error('❌ Error message:', err.message);
    console.error('❌ Error stack:', err.stack);

    if (err.response) {
      console.error('❌ Response status:', err.response.status);
      console.error('❌ Response data:', err.response.data);
      console.error('❌ Response headers:', err.response.headers);
      console.error('❌ Request URL:', err.response.config?.url);
    }

    // Prikaži mock podatke samo za demo
    console.log('🔄 Prikazujem mock podatke...');
    setPopularFilms([
      {
        id: 1,
        title: `The Great Adventure (${country.country_name})`,
        vote_average: 7.8,
        release_date: '2023-05-15',
        overview: 'An epic adventure film set in beautiful locations.'
      },
      {
        id: 2,
        title: `${country.country_name} Nights`,
        vote_average: 8.2,
        release_date: '2022-11-30',
        overview: 'A romantic drama capturing the spirit of the country.'
      },
      {
        id: 3,
        title: `Mystery in ${country.country_name}`,
        vote_average: 6.9,
        release_date: '2021-08-20',
        overview: 'A thrilling mystery that keeps you guessing until the end.'
      },
    ]);
  }

  console.log('🎯 7. Završavam handleCountryClick');
  setMapLoading(false);
};

  const resetMarkerIcons = () => {
    Object.values(markersRef.current).forEach(marker => {
      if (marker && marker.setIcon) {
        marker.setIcon(customIcon);
      }
    });
  };

  const handleMarkerClick = (country, marker) => {
    resetMarkerIcons();
    markersRef.current[country.country_code] = marker;
    handleCountryClick(country);
  };

  const flag = (cc) => {
    if (!cc) return '🏳️';
    const codePoints = cc.toUpperCase().split('').map(c => 127397 + c.charCodeAt());
    return String.fromCodePoint(...codePoints);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading world map...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-4">
      <div className="lg:col-span-2 bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="p-4 bg-gradient-to-r from-blue-600 to-blue-800 text-white">
          <h1 className="text-2xl font-bold flex items-center">
            <FaMapMarkerAlt className="mr-3" /> World Film Popularity Map
          </h1>
          <p className="text-blue-100">Click on any country marker to see top 3 films</p>
        </div>

        <MapContainer
          ref={mapRef}
          center={[20, 0]}
          zoom={2}
          style={{ height: '500px' }}
          className="rounded-b-xl"
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />

          {countries.map((country, index) => (
            <Marker
              key={`${country.country_code}-${index}`}
              position={[country.latitude, country.longitude]}
              icon={selectedCountry?.country_code === country.country_code ? activeIcon : customIcon}
              eventHandlers={{
                click: (e) => {
                  const marker = e.target;
                  handleMarkerClick(country, marker);
                },
                mouseover: (e) => {
                  e.target.openPopup();
                },
                mouseout: (e) => {
                  e.target.closePopup();
                }
              }}
            >
              <Popup>
                <div className="text-center">
                  <div className="text-2xl">{flag(country.country_code)}</div>
                  <strong className="text-lg">{country.country_name}</strong>
                  <div className="mt-2">
                    <button
                      onClick={() => handleCountryClick(country)}
                      className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition"
                    >
                      Show Top Films
                    </button>
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="p-4 bg-gradient-to-r from-purple-600 to-purple-800 text-white">
          <h2 className="text-xl font-bold flex items-center">
            <FaFilm className="mr-2" /> Top Films
          </h2>
        </div>

        <div className="p-6">
          {selectedCountry ? (
            <>
              <div className="flex items-center mb-6">
                <div className="text-4xl mr-4">{flag(selectedCountry.country_code)}</div>
                <div>
                  <h3 className="text-2xl font-bold">{selectedCountry.country_name}</h3>
                  <p className="text-gray-600 text-sm">{selectedCountry.capital || 'Top film destination'}</p>
                </div>
              </div>

              {mapLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
                  <p className="mt-4 text-gray-600">Loading films...</p>
                </div>
              ) : popularFilms.length > 0 ? (
                <>
                  <h4 className="font-semibold mb-4 text-gray-700 border-b pb-2">Top 3 Films</h4>
                  <div className="space-y-4">
                    {popularFilms.map((film, index) => (
                      <div key={index} className="flex gap-4 bg-gray-50 p-4 rounded-lg border border-gray-200 hover:bg-gray-100 transition">
                        <div className="flex-shrink-0">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center text-white font-bold">
                            {index + 1}
                          </div>
                        </div>
                        <div className="flex-1">
                          <div className="font-semibold text-lg">{film.title}</div>
                          <div className="flex items-center mt-1">
                            <FaStar className="text-yellow-500 mr-1" />
                            <span className="font-medium">{film.vote_average?.toFixed(1) || 'N/A'}/10</span>
                            {film.release_date && (
                              <span className="ml-4 text-sm text-gray-500">
                                {new Date(film.release_date).getFullYear()}
                              </span>
                            )}
                          </div>
                          {film.overview && (
                            <p className="text-sm text-gray-600 mt-2 line-clamp-2">{film.overview}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <FaFilm className="text-4xl mx-auto mb-4 text-gray-300" />
                  <p>No films found for this country.</p>
                  <p className="text-sm mt-2">Try another country.</p>
                </div>
              )}

              <div className="mt-8 pt-6 border-t">
                <button
                  onClick={() => {
                    setSelectedCountry(null);
                    setPopularFilms([]);
                    resetMarkerIcons();
                  }}
                  className="w-full bg-gray-100 hover:bg-gray-200 text-gray-800 py-2 rounded-lg transition font-medium"
                >
                  Clear Selection
                </button>
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🌎</div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">Select a Country</h3>
              <p className="text-gray-500 mb-6">Click on any marker on the map to see the top 3 films from that country</p>
              <div className="text-left bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-800 mb-2">Try clicking on:</h4>
                <ul className="space-y-2">
                  {countries.slice(0, 5).map(country => (
                    <li key={country.country_code} className="flex items-center">
                      <span className="mr-2">{flag(country.country_code)}</span>
                      <span>{country.country_name}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RegionalPopularityMap;