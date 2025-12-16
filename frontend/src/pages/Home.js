import React, { useState, useEffect } from 'react';
import MovieCard from '../components/MovieCard';
import { fetchPopularMovies } from '../services/api';

const Home = () => {
  const [popularMovies, setPopularMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [apiSource, setApiSource] = useState('');

  useEffect(() => {
    loadPopularMovies();
  }, []);

  const loadPopularMovies = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await fetchPopularMovies(4);

      setPopularMovies(data.films || []);
      setApiSource(data.source || 'unknown');

      if (!data.films || data.films.length === 0) {
        setError('No movies found. Please try again later.');
      }
    } catch (err) {
      console.error('Error loading popular movies:', err);
      setError('Failed to load movies. Showing sample data.');

      // Fallback sample data
      setPopularMovies([
        {
          film_id: 1,
          title: "The Shawshank Redemption",
          overview: "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
          release_date: "1994-09-23",
          popularity: 100,
          vote_average: 8.7,
          vote_count: 24000,
          poster_url: "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
          genres: ["Drama", "Crime"]
        },
        {
          film_id: 2,
          title: "The Godfather",
          overview: "The aging patriarch of an organized crime dynasty transfers control to his reluctant son.",
          release_date: "1972-03-24",
          popularity: 95,
          vote_average: 8.7,
          vote_count: 18000,
          poster_url: "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
          genres: ["Drama", "Crime"]
        },
        {
          film_id: 3,
          title: "The Dark Knight",
          overview: "When the menace known as the Joker wreaks havoc on Gotham City, Batman must accept one of the greatest psychological tests.",
          release_date: "2008-07-18",
          popularity: 90,
          vote_average: 8.5,
          vote_count: 30000,
          poster_url: "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
          genres: ["Action", "Crime", "Drama"]
        },
        {
          film_id: 4,
          title: "Pulp Fiction",
          overview: "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.",
          release_date: "1994-10-14",
          popularity: 85,
          vote_average: 8.5,
          vote_count: 25000,
          poster_url: "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
          genres: ["Crime", "Drama"]
        }
      ]);

      setApiSource('fallback');
    } finally {
      setLoading(false);
    }
  };

  const getYearFromDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).getFullYear();
    } catch {
      return 'N/A';
    }
  };

  const getGenreFromIds = (genreIds) => {
    // Map TMDB genre IDs to names
    const genreMap = {
      28: "Action",
      12: "Adventure",
      16: "Animation",
      35: "Comedy",
      80: "Crime",
      99: "Documentary",
      18: "Drama",
      10751: "Family",
      14: "Fantasy",
      36: "History",
      27: "Horror",
      10402: "Music",
      9648: "Mystery",
      10749: "Romance",
      878: "Science Fiction",
      10770: "TV Movie",
      53: "Thriller",
      10752: "War",
      37: "Western"
    };

    if (!genreIds || !Array.isArray(genreIds)) return [];
    return genreIds.map(id => genreMap[id] || `Genre ${id}`).slice(0, 2);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Welcome Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          Welcome to <span className="text-blue-600">Film Platform</span>
        </h1>
        <p className="text-gray-600 text-lg max-w-2xl mx-auto">
          Discover trending movies, explore filming locations, and analyze film data from around the world.
        </p>
      </div>

      {/* Popular Movies Section */}
      <div className="mb-12">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
          <div>
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">🔥 Popular This Week</h2>
            <div className="flex items-center gap-2 mt-2">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                apiSource === 'tmdb_api' ? 'bg-green-100 text-green-800' :
                apiSource === 'database' ? 'bg-blue-100 text-blue-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {apiSource === 'tmdb_api' ? '📡 Live TMDB API' :
                 apiSource === 'database' ? '💾 From Database' :
                 apiSource === 'fallback' ? '📦 Sample Data' :
                 'Loading...'}
              </span>
              {popularMovies.length > 0 && (
                <span className="text-sm text-gray-600">
                  {popularMovies.length} movies loaded
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={loadPopularMovies}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-2 px-4 rounded-lg flex items-center gap-2 transition-colors"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Loading...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Refresh Movies
                </>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-yellow-700">
                  {error}
                </p>
              </div>
            </div>
          </div>
        )}

        {loading ? (
          <div className="flex justify-center items-center h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading popular movies from TMDB...</p>
              <p className="text-sm text-gray-500 mt-2">Fetching real-time data</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {popularMovies.map((movie) => {
              const genres = getGenreFromIds(movie.genre_ids);
              const year = getYearFromDate(movie.release_date);

              return (
                <div key={movie.film_id} className="group">
                  <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300 h-full flex flex-col">
                    {/* Movie Poster */}
                    <div className="relative overflow-hidden bg-gray-100">
                      <img
                        src={movie.poster_url || 'https://via.placeholder.com/500x750?text=No+Poster'}
                        alt={movie.title}
                        className="w-full h-80 object-cover transition-transform duration-500 group-hover:scale-105"
                        onError={(e) => {
                          e.target.onerror = null;
                          e.target.src = 'https://via.placeholder.com/500x750?text=No+Image';
                        }}
                      />

                      {/* Rating Badge */}
                      <div className="absolute top-4 right-4 bg-black bg-opacity-75 text-white px-3 py-1 rounded-full flex items-center">
                        <svg className="w-4 h-4 text-yellow-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                        <span className="font-bold">{movie.vote_average?.toFixed(1) || 'N/A'}</span>
                      </div>

                      {/* Year Badge */}
                      <div className="absolute top-4 left-4 bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
                        {year}
                      </div>
                    </div>

                    {/* Movie Info */}
                    <div className="p-5 flex-grow flex flex-col">
                      <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors line-clamp-2">
                        {movie.title}
                      </h3>

                      <div className="mb-4">
                        {genres.length > 0 && (
                          <p className="text-gray-600 text-sm mb-2">
                            {genres.join(', ')}
                          </p>
                        )}
                        <p className="text-gray-700 text-sm line-clamp-3">
                          {movie.overview || 'No description available'}
                        </p>
                      </div>

                      {/* Stats */}
                      <div className="mt-auto pt-4 border-t border-gray-100">
                        <div className="flex justify-between text-sm text-gray-500">
                          <div className="flex items-center">
                            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                            </svg>
                            {year}
                          </div>
                          <div className="flex items-center">
                            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                            </svg>
                            {movie.vote_count?.toLocaleString() || '0'} votes
                          </div>
                        </div>
                        {movie.popularity && (
                          <div className="flex items-center mt-2 text-xs text-gray-400">
                            <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clipRule="evenodd" />
                            </svg>
                            Popularity: {Math.round(movie.popularity)}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Features Section */}
      <div className="max-w-6xl mx-auto mb-12">
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8 shadow-lg">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-8 text-center">
            🎬 Platform Features
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="font-bold text-lg mb-2">Real-time Film Data</h3>
              <p className="text-gray-600 text-sm">
                Live data from TMDB API showing trending movies worldwide.
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 className="font-bold text-lg mb-2">Location Analytics</h3>
              <p className="text-gray-600 text-sm">
                Track filming locations and analyze geographical film data.
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="font-bold text-lg mb-2">Data Analytics</h3>
              <p className="text-gray-600 text-sm">
                Advanced analytics and visualization of film industry trends.
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 className="font-bold text-lg mb-2">ETL Dashboard</h3>
              <p className="text-gray-600 text-sm">
                Real-time ETL job monitoring and data pipeline management.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white text-center">
        <h2 className="text-2xl md:text-3xl font-bold mb-4">Ready to Explore More?</h2>
        <p className="mb-6 text-blue-100 max-w-2xl mx-auto">
          Join thousands of film enthusiasts and data analysts using our platform to discover, analyze, and visualize film data in real-time.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="/register"
            className="bg-white text-blue-600 hover:bg-gray-100 font-bold py-3 px-8 rounded-lg transition-colors"
          >
            Get Started Free
          </a>
          <a
            href="/login"
            className="bg-transparent border-2 border-white hover:bg-white hover:text-blue-600 text-white font-bold py-3 px-8 rounded-lg transition-colors"
          >
            Sign In
          </a>
        </div>
      </div>

      {/* API Status Info */}
      <div className="mt-8 text-center text-sm text-gray-500">
        <p>
          Data sourced from TMDB API • Updated in real-time • Showing {popularMovies.length} trending movies
        </p>
      </div>
    </div>
  );
};

export default Home;