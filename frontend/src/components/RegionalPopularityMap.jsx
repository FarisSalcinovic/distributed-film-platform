import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { mapAPI } from '../services/api';
import { FaFilm, FaStar, FaGlobeAmericas, FaMapMarkerAlt, FaSyncAlt } from 'react-icons/fa';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Popravi ikone za Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png')
});

const RegionalPopularityMap = () => {
  const [mapData, setMapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCountry, setSelectedCountry] = useState(null);

  useEffect(() => {
    loadMapData();
  }, []);

  const loadMapData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await mapAPI.getRegionalPopularity();
      setMapData(data);

      // Automatski odaberi prvu zemlju ako postoji
      if (data.regions && data.regions.length > 0) {
        setSelectedCountry(data.regions[0]);
      }
    } catch (err) {
      console.error('Error loading regional popularity map:', err);
      setError('Failed to load regional popularity data. Please try again later.');

      // Fallback na test podatke
      setMapData({
        regions: [
          {
            country_code: 'US',
            country_name: 'United States',
            capital_city: 'Washington, D.C.',
            latitude: 38.89511,
            longitude: -77.03637,
            total_movies_analyzed: 10,
            top_movies: [
              {
                film_id: 1,
                title: 'The Shawshank Redemption',
                vote_average: 8.7,
                poster_url: 'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg',
                overview: 'Two imprisoned men bond over a number of years...'
              },
              {
                film_id: 2,
                title: 'The Godfather',
                vote_average: 8.7,
                poster_url: 'https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg',
                overview: 'The aging patriarch of an organized crime dynasty...'
              },
              {
                film_id: 3,
                title: 'The Dark Knight',
                vote_average: 8.5,
                poster_url: 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
                overview: 'When the Joker wreaks havoc on Gotham City...'
              }
            ],
            top_genres: [
              { name: 'Drama', count: 5, percentage: 45 },
              { name: 'Crime', count: 3, percentage: 30 },
              { name: 'Action', count: 2, percentage: 25 }
            ]
          },
          {
            country_code: 'GB',
            country_name: 'United Kingdom',
            capital_city: 'London',
            latitude: 51.5074,
            longitude: -0.1278,
            total_movies_analyzed: 8,
            top_movies: [
              {
                film_id: 4,
                title: 'Harry Potter and the Philosopher\'s Stone',
                vote_average: 8.1,
                poster_url: 'https://image.tmdb.org/t/p/w500/wuMc08IPKEatf9rnMNXvIDxqP4W.jpg',
                overview: 'A young boy discovers he is a wizard...'
              },
              {
                film_id: 5,
                title: 'Skyfall',
                vote_average: 7.8,
                poster_url: 'https://image.tmdb.org/t/p/w500/9tJx2fG9eR79kK6OXE2xELrE0Es.jpg',
                overview: 'James Bond\'s loyalty to M is tested...'
              },
              {
                film_id: 6,
                title: 'The King\'s Speech',
                vote_average: 8.0,
                poster_url: 'https://image.tmdb.org/t/p/w500/uK7VkHKB4LT3qnlvqaXww6RAxkt.jpg',
                overview: 'The story of King George VI of the United Kingdom...'
              }
            ],
            top_genres: [
              { name: 'Fantasy', count: 4, percentage: 40 },
              { name: 'Adventure', count: 3, percentage: 35 },
              { name: 'Drama', count: 2, percentage: 25 }
            ]
          }
        ]
      });

      // Odaberi US kao fallback
      setSelectedCountry({
        country_code: 'US',
        country_name: 'United States',
        capital_city: 'Washington, D.C.',
        latitude: 38.89511,
        longitude: -77.03637,
        top_movies: [
          { title: 'The Shawshank Redemption', vote_average: 8.7 },
          { title: 'The Godfather', vote_average: 8.7 },
          { title: 'The Dark Knight', vote_average: 8.5 }
        ],
        top_genres: [
          { name: 'Drama', percentage: 45 },
          { name: 'Crime', percentage: 30 },
          { name: 'Action', percentage: 25 }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const getCountryFlagEmoji = (countryCode) => {
    // Konvertujemo kod u Unicode za emoji zastave
    const codePoints = countryCode
      .toUpperCase()
      .split('')
      .map(char => 127397 + char.charCodeAt());
    return String.fromCodePoint(...codePoints);
  };

  const createCustomIcon = (countryCode) => {
    return L.divIcon({
      html: `<div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 16px;
        border: 3px solid white;
        box-shadow: 0 3px 10px rgba(0,0,0,0.3);
        cursor: pointer;
        transition: all 0.3s ease;
      ">
        ${getCountryFlagEmoji(countryCode)}
      </div>`,
      className: 'custom-marker',
      iconSize: [36, 36],
      iconAnchor: [18, 36]
    });
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px] bg-white rounded-xl shadow-lg">
        <div className="animate-spin rounded-full h-20 w-20 border-b-4 border-blue-600 mb-6"></div>
        <p className="text-xl font-medium text-gray-800 mb-2">Loading World Film Map</p>
        <p className="text-gray-600 max-w-md text-center">
          Fetching real-time film popularity data from TMDB and Geoapify APIs...
        </p>
        <div className="mt-6 flex items-center space-x-4 text-sm text-gray-500">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
            <span>Loading country data</span>
          </div>
          <div className="flex items-center">
            <FaFilm className="mr-2 text-purple-500" />
            <span>Fetching movies</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mr-4">
            <FaGlobeAmericas className="text-3xl text-white" />
          </div>
          <div className="text-left">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
              World Film Popularity Map
            </h1>
            <p className="text-gray-600 mt-2">
              Explore trending movies and genres across different countries in real-time
            </p>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap justify-center gap-4">
          <div className="flex items-center px-4 py-2 bg-blue-50 rounded-lg">
            <div className="w-4 h-4 rounded-full bg-blue-500 mr-2"></div>
            <span className="text-sm font-medium text-gray-700">Click markers for details</span>
          </div>
          <div className="flex items-center px-4 py-2 bg-purple-50 rounded-lg">
            <FaStar className="text-yellow-500 mr-2" />
            <span className="text-sm font-medium text-gray-700">Movie ratings from TMDB</span>
          </div>
          <div className="flex items-center px-4 py-2 bg-green-50 rounded-lg">
            <FaFilm className="text-green-500 mr-2" />
            <span className="text-sm font-medium text-gray-700">Genre analysis</span>
          </div>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Map Section - 2/3 width */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="p-4 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-lg font-bold text-gray-800 flex items-center">
                <FaMapMarkerAlt className="mr-2 text-blue-600" />
                Interactive World Map
              </h2>
              <div className="text-sm text-gray-600">
                {mapData?.regions?.length || 0} countries loaded
              </div>
            </div>

            <div className="h-[500px] relative">
              <MapContainer
                center={[20, 0]}
                zoom={2}
                style={{ height: '100%', width: '100%' }}
                scrollWheelZoom={true}
                className="rounded-b-xl"
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {mapData?.regions?.map((region, index) => (
                  <Marker
                    key={`${region.country_code}-${index}`}
                    position={[region.latitude, region.longitude]}
                    icon={createCustomIcon(region.country_code)}
                    eventHandlers={{
                      click: () => {
                        setSelectedCountry(region);
                        // Scroll to top of details panel on mobile
                        if (window.innerWidth < 1024) {
                          document.querySelector('.details-panel')?.scrollIntoView({ behavior: 'smooth' });
                        }
                      },
                      mouseover: (e) => {
                        e.target.openPopup();
                      },
                      mouseout: (e) => {
                        e.target.closePopup();
                      }
                    }}
                  >
                    <Popup maxWidth={300} minWidth={250}>
                      <div className="p-3">
                        <div className="flex items-center mb-3">
                          <span className="text-2xl mr-2">{getCountryFlagEmoji(region.country_code)}</span>
                          <div>
                            <h3 className="font-bold text-lg text-gray-900">{region.country_name}</h3>
                            <p className="text-gray-600 text-sm">Capital: {region.capital_city}</p>
                          </div>
                        </div>

                        <div className="space-y-3">
                          <div>
                            <h4 className="font-semibold text-sm text-gray-700 mb-2 border-b pb-1">Top Movies:</h4>
                            <div className="space-y-2">
                              {region.top_movies?.slice(0, 2).map((movie, idx) => (
                                <div key={idx} className="flex items-start gap-2 p-2 hover:bg-gray-50 rounded">
                                  <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded flex items-center justify-center mt-1">
                                    <span className="text-xs font-bold text-blue-600">{idx + 1}</span>
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-gray-900 truncate">{movie.title}</p>
                                    <div className="flex items-center text-xs text-gray-600 mt-1">
                                      <FaStar className="text-yellow-500 mr-1" />
                                      <span>{movie.vote_average}/10</span>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>

                          <div>
                            <h4 className="font-semibold text-sm text-gray-700 mb-2 border-b pb-1">Popular Genres:</h4>
                            <div className="flex flex-wrap gap-1">
                              {region.top_genres?.map((genre, idx) => (
                                <span
                                  key={idx}
                                  className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded"
                                >
                                  {genre.name}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>

                        <div className="mt-4 pt-3 border-t border-gray-200">
                          <button
                            onClick={() => setSelectedCountry(region)}
                            className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded transition-colors"
                          >
                            View Full Details →
                          </button>
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                ))}
              </MapContainer>
            </div>
          </div>

          {/* Map Controls */}
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            <div className="text-sm text-gray-600">
              <span className="font-medium">Data Source:</span> TMDB API + Geoapify Geocoding
            </div>
            <div className="flex gap-3">
              <button
                onClick={loadMapData}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-medium rounded-lg transition-all hover:shadow-lg"
              >
                <FaSyncAlt className={loading ? 'animate-spin' : ''} />
                Refresh Map Data
              </button>
              <button
                onClick={() => mapAPI.getTestMapData().then(setMapData)}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium rounded-lg transition-colors"
              >
                Test Data
              </button>
            </div>
          </div>
        </div>

        {/* Details Panel - 1/3 width */}
        <div className="lg:col-span-1 details-panel">
          <div className="bg-white rounded-xl shadow-lg overflow-hidden sticky top-6">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900 flex items-center">
                {selectedCountry ? (
                  <>
                    <span className="text-2xl mr-3">{getCountryFlagEmoji(selectedCountry.country_code)}</span>
                    <div>
                      {selectedCountry.country_name}
                      <span className="text-sm font-normal text-gray-500 block mt-1">
                        Film Popularity Analysis
                      </span>
                    </div>
                  </>
                ) : (
                  'Select a Country'
                )}
              </h2>
            </div>

            {selectedCountry ? (
              <div className="p-6 space-y-8 max-h-[calc(100vh-200px)] overflow-y-auto">
                {/* Country Stats */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-blue-50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-blue-600 mb-1">
                      {selectedCountry.total_movies_analyzed || '10+'}
                    </div>
                    <div className="text-sm text-gray-600">Movies Analyzed</div>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-purple-600 mb-1">
                      {selectedCountry.top_movies?.length || 3}
                    </div>
                    <div className="text-sm text-gray-600">Top Films</div>
                  </div>
                </div>

                {/* Top Movies */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold text-gray-800 flex items-center">
                      <FaFilm className="mr-2 text-blue-500" />
                      Top 3 Movies
                    </h3>
                    <span className="text-sm text-gray-500">By Popularity</span>
                  </div>
                  <div className="space-y-4">
                    {selectedCountry.top_movies?.map((movie, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-4 p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors cursor-pointer"
                        onClick={() => {
                          // Ovdje možeš dodati funkcionalnost za otvaranje detalja filma
                          console.log('Selected movie:', movie);
                        }}
                      >
                        <div className="flex-shrink-0">
                          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                            {index + 1}
                          </div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-semibold text-gray-900 mb-1 truncate">{movie.title}</h4>
                          <div className="flex items-center">
                            <FaStar className="text-yellow-500 mr-1" />
                            <span className="font-medium text-gray-700">{movie.vote_average}/10</span>
                            {movie.release_date && (
                              <span className="ml-2 text-sm text-gray-500">
                                ({new Date(movie.release_date).getFullYear()})
                              </span>
                            )}
                          </div>
                          {movie.overview && (
                            <p className="text-sm text-gray-600 mt-2 line-clamp-2">{movie.overview}</p>
                          )}
                        </div>
                        {movie.poster_url && (
                          <div className="flex-shrink-0">
                            <img
                              src={movie.poster_url}
                              alt={movie.title}
                              className="w-16 h-20 object-cover rounded-lg shadow"
                              onError={(e) => {
                                e.target.onerror = null;
                                e.target.src = 'https://via.placeholder.com/64x80?text=No+Image';
                              }}
                            />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Top Genres */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold text-gray-800 flex items-center">
                      <FaStar className="mr-2 text-purple-500" />
                      Popular Genres
                    </h3>
                    <span className="text-sm text-gray-500">Distribution</span>
                  </div>
                  <div className="space-y-4">
                    {selectedCountry.top_genres?.map((genre, index) => (
                      <div key={index}>
                        <div className="flex justify-between text-sm mb-2">
                          <div className="flex items-center">
                            <div className="w-3 h-3 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 mr-2"></div>
                            <span className="font-medium text-gray-800">{genre.name}</span>
                          </div>
                          <span className="font-bold text-gray-900">{genre.percentage}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                          <div
                            className="bg-gradient-to-r from-purple-500 to-pink-500 h-2.5 rounded-full transition-all duration-300"
                            style={{ width: `${genre.percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Additional Info */}
                <div className="pt-6 border-t border-gray-200">
                  <h4 className="font-bold text-gray-800 mb-4">Map Legend</h4>
                  <div className="space-y-3">
                    <div className="flex items-center">
                      <div className="w-6 h-6 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 mr-3"></div>
                      <div>
                        <p className="font-medium text-gray-800">Country Marker</p>
                        <p className="text-sm text-gray-600">Click for detailed film analysis</p>
                      </div>
                    </div>
                    <div className="flex items-center">
                      <div className="w-6 h-6 bg-yellow-500 rounded-full flex items-center justify-center mr-3">
                        <FaStar className="text-white text-xs" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-800">TMDB Rating</p>
                        <p className="text-sm text-gray-600">Average user rating (out of 10)</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-12 text-center">
                <div className="text-5xl mb-4">🌍</div>
                <h3 className="text-lg font-bold text-gray-800 mb-2">Select a Country</h3>
                <p className="text-gray-600">
                  Click on any country marker on the map to see detailed film popularity analysis
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegionalPopularityMap;