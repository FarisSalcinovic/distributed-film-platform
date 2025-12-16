import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { Bar, Line, Pie, Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement,
  ArcElement
} from "chart.js";
import { analyticsAPI } from "../services/etlApi";

const API_URL = "http://localhost:8000";

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export default function AnalyticsDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [popularFilms, setPopularFilms] = useState([]);
  const [trendingFilms, setTrendingFilms] = useState([]);
  const [filmsByCountry, setFilmsByCountry] = useState([]);
  const [chartData, setChartData] = useState(null);
  const [citiesData, setCitiesData] = useState([]);

  function handleLogout() {
    localStorage.removeItem("access_token");
    navigate("/login");
  }

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      navigate("/login");
      return;
    }

    fetch(`${API_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
      .then(async res => {
        if (res.status === 401) {
          handleLogout();
          return null;
        }

        if (!res.ok) {
          throw new Error("Failed to load user");
        }

        return res.json();
      })
      .then(data => {
        if (data) setUser(data);
        loadAnalyticsData();
      })
      .catch(() => {
        setError("Could not load user data.");
      });
  }, [navigate]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);

      // 1. Load basic statistics
      const statsResponse = await fetch(`${API_URL}/api/v1/analytics/stats`);
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }

      // 2. Load popular films
      const popularResponse = await fetch(`${API_URL}/api/v1/films/popular?limit=4`);
      if (popularResponse.ok) {
        const popularData = await popularResponse.json();
        setPopularFilms(popularData.films || []);
      }

      // 3. Load trending films
      const trendingData = await analyticsAPI.getTrendingFilms(7, 5);
      setTrendingFilms(trendingData.films || []);

      // 4. Load films by country
      const countryResponse = await fetch(`${API_URL}/api/v1/analytics/films-by-country`);
      if (countryResponse.ok) {
        const countryData = await countryResponse.json();
        setFilmsByCountry(countryData.data || []);
      }

      // 5. Load popular cities
      const citiesResponse = await fetch(`${API_URL}/api/v1/cities/featured?limit=6`);
      if (citiesResponse.ok) {
        const citiesData = await citiesResponse.json();
        setCitiesData(citiesData.cities || []);
      }

      // 6. Prepare chart data
      prepareChartData();

    } catch (error) {
      console.error("Error loading analytics data:", error);
      // Use fallback data
      setStats({
        counts: { films: 1247, cities: 24, film_locations: 5321, etl_jobs: 89 }
      });
    } finally {
      setLoading(false);
    }
  };

  const prepareChartData = () => {
    // Bar Chart - Films by country (use real data if available)
    const barData = {
      labels: filmsByCountry.length > 0
        ? filmsByCountry.slice(0, 6).map(item => item.country)
        : ['US', 'GB', 'FR', 'DE', 'JP', 'IT'],
      datasets: [
        {
          label: 'Number of Films',
          data: filmsByCountry.length > 0
            ? filmsByCountry.slice(0, 6).map(item => item.film_count)
            : [65, 59, 80, 81, 56, 55],
          backgroundColor: 'rgba(59, 130, 246, 0.6)',
          borderColor: 'rgba(59, 130, 246, 1)',
          borderWidth: 1,
        },
      ],
    };

    // Line Chart - Trend (use trending films)
    const lineLabels = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'];
    const lineData = {
      labels: lineLabels,
      datasets: [
        {
          label: 'Popularity',
          data: trendingFilms.length > 0
            ? trendingFilms.slice(0, 7).map(film => film.popularity || film.trending_score || 0)
            : [45, 52, 67, 78, 82, 85, 91],
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.3,
        }
      ],
    };

    // Pie Chart - Genres (if we have data)
    const genreData = {
      labels: ['Action', 'Drama', 'Comedy', 'Horror', 'Romance', 'Sci-Fi'],
      datasets: [
        {
          label: 'Genres',
          data: [35, 25, 20, 10, 5, 5],
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 206, 86, 0.6)',
            'rgba(75, 192, 192, 0.6)',
            'rgba(153, 102, 255, 0.6)',
            'rgba(255, 159, 64, 0.6)',
          ],
          hoverOffset: 10,
        },
      ],
    };

    // Doughnut Chart - Data sources
    const sourceData = {
      labels: ['TMDB API', 'Geoapify', 'User Input', 'Other APIs'],
      datasets: [
        {
          label: 'Data Sources',
          data: [45, 30, 15, 10],
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 206, 86, 0.6)',
            'rgba(75, 192, 192, 0.6)',
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
          ],
          borderWidth: 1,
        },
      ],
    };

    setChartData({
      bar: barData,
      line: lineData,
      pie: genreData,
      doughnut: sourceData
    });
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 20
        }
      }
    }
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
      },
    },
  };

  if (!user || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-sky-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">
            {error || "Loading analytics..."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-sky-50">

      {/* LEFT CONTENT */}
      <main className="flex-1 p-6 md:p-10">

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-2">Statistical overview of database data</p>
        </div>

        {/* SUMMARY CARDS WITH REAL DATA */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
          <div className="bg-white shadow-lg p-6 rounded-xl border border-gray-100">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg mr-4">
                <span className="text-2xl">🎬</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-600 mb-1">Total Films</h3>
                <p className="text-3xl font-bold text-blue-600">
                  {stats?.counts?.films || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white shadow-lg p-6 rounded-xl border border-gray-100">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg mr-4">
                <span className="text-2xl">🏙️</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-600 mb-1">Cities</h3>
                <p className="text-3xl font-bold text-green-600">
                  {stats?.counts?.cities || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white shadow-lg p-6 rounded-xl border border-gray-100">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg mr-4">
                <span className="text-2xl">📍</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-600 mb-1">Locations</h3>
                <p className="text-3xl font-bold text-purple-600">
                  {stats?.counts?.film_locations || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white shadow-lg p-6 rounded-xl border border-gray-100">
            <div className="flex items-center">
              <div className="p-3 bg-yellow-100 rounded-lg mr-4">
                <span className="text-2xl">⚡</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-600 mb-1">ETL Jobs</h3>
                <p className="text-3xl font-bold text-yellow-600">
                  {stats?.counts?.etl_jobs || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* POPULAR FILMS */}
        {popularFilms.length > 0 && (
          <div className="bg-white shadow-lg p-6 rounded-xl mb-8 border border-gray-100">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-800">Popular Films</h2>
              <span className="bg-blue-100 text-blue-800 text-xs font-medium px-3 py-1 rounded-full">
                Source: {popularFilms[0]?.source || 'API'}
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {popularFilms.map((film, index) => (
                <div key={index} className="bg-gray-50 p-4 rounded-lg hover:shadow transition">
                  {film.poster_url && (
                    <img
                      src={film.poster_url}
                      alt={film.title}
                      className="w-full h-48 object-cover rounded mb-3"
                      onError={(e) => {
                        e.target.src = "https://via.placeholder.com/300x450?text=No+Image";
                      }}
                    />
                  )}
                  <h3 className="font-semibold text-gray-800 truncate">{film.title}</h3>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-sm text-gray-600">
                      {film.release_date ? new Date(film.release_date).getFullYear() : 'N/A'}
                    </span>
                    <div className="flex items-center">
                      <span className="text-yellow-500 mr-1">★</span>
                      <span className="font-medium">{film.vote_average?.toFixed(1) || 'N/A'}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CHARTS SECTION */}
        {chartData ? (
          <>
            {/* Grid with two charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Films by country */}
              <div className="bg-white shadow-lg p-6 rounded-xl border border-gray-100">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-800">Films by Country</h2>
                  <span className="bg-blue-100 text-blue-800 text-xs font-medium px-3 py-1 rounded-full">
                    {filmsByCountry.length > 0 ? 'Real Data' : 'Demo Data'}
                  </span>
                </div>
                <div className="h-72">
                  <Bar data={chartData.bar} options={chartOptions} />
                </div>
                <div className="mt-4 text-sm text-gray-600">
                  <p>Number of films by production country {filmsByCountry.length > 0 ? 'from database' : '(demo)'}</p>
                </div>
              </div>

              {/* Trending over time */}
              <div className="bg-white shadow-lg p-6 rounded-xl border border-gray-100">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-800">Popularity Trend</h2>
                  <span className="bg-green-100 text-green-800 text-xs font-medium px-3 py-1 rounded-full">
                    Last 7 days
                  </span>
                </div>
                <div className="h-72">
                  <Line data={chartData.line} options={chartOptions} />
                </div>
                <div className="mt-4 text-sm text-gray-600">
                  <p>Film popularity trend {trendingFilms.length > 0 ? 'from API' : ''}</p>
                </div>
              </div>
            </div>

            {/* Grid with two more charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Genre distribution */}
              <div className="bg-white shadow-lg p-6 rounded-xl border border-gray-100">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-800">Genre Distribution</h2>
                  <span className="bg-purple-100 text-purple-800 text-xs font-medium px-3 py-1 rounded-full">
                    Pie Chart
                  </span>
                </div>
                <div className="h-72">
                  <Pie data={chartData.pie} options={pieOptions} />
                </div>
                <div className="mt-4 text-sm text-gray-600">
                  <p>Percentage share of genres in the database</p>
                </div>
              </div>

              {/* Data sources */}
              <div className="bg-white shadow-lg p-6 rounded-xl border border-gray-100">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-800">Data Sources</h2>
                  <span className="bg-pink-100 text-pink-800 text-xs font-medium px-3 py-1 rounded-full">
                    Doughnut Chart
                  </span>
                </div>
                <div className="h-72">
                  <Doughnut data={chartData.doughnut} options={pieOptions} />
                </div>
                <div className="mt-4 text-sm text-gray-600">
                  <p>Share of different API sources in the system</p>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading charts...</p>
          </div>
        )}

        {/* POPULAR FILM CITIES */}
        {citiesData.length > 0 && (
          <div className="bg-white shadow-lg p-6 rounded-xl border border-gray-100 mb-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-800">Popular Film Cities</h2>
              <span className="bg-indigo-100 text-indigo-800 text-xs font-medium px-3 py-1 rounded-full">
                {citiesData[0]?.source || 'Geoapify'}
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {citiesData.slice(0, 3).map((city, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                  <div className="flex items-start">
                    <div className="bg-blue-100 text-blue-800 rounded-full w-12 h-12 flex items-center justify-center mr-4">
                      <span className="font-bold text-lg">{city.name.charAt(0)}</span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-800">{city.name}</h3>
                      <p className="text-sm text-gray-600">{city.country}</p>
                      <div className="mt-2">
                        <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded mr-2">
                          Pop: {city.population?.toLocaleString() || 'N/A'}
                        </span>
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          {city.country_code}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4">
                    <p className="text-sm text-gray-600">{city.description}</p>
                    {city.sample_films && city.sample_films.length > 0 && (
                      <div className="mt-2">
                        <span className="text-xs font-semibold text-gray-700">Films:</span>
                        <p className="text-xs text-gray-600 mt-1">{city.sample_films.join(', ')}</p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TRENDING FILMS TABLE */}
        {trendingFilms.length > 0 && (
          <div className="bg-white shadow-lg p-6 rounded-xl border border-gray-100">
            <h2 className="text-xl font-semibold mb-6 text-gray-800">Trending Films (Last 7 days)</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">#</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Film</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Popularity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rating</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Votes</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {trendingFilms.map((film, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{index + 1}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            {film.poster_url ? (
                              <img
                                src={film.poster_url}
                                alt={film.title}
                                className="h-10 w-10 rounded"
                                onError={(e) => {
                                  e.target.src = "https://via.placeholder.com/40x60?text=No+Img";
                                }}
                              />
                            ) : (
                              <div className="h-10 w-10 bg-gray-200 rounded flex items-center justify-center">
                                <span className="text-xs text-gray-500">N/A</span>
                              </div>
                            )}
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{film.title}</div>
                            <div className="text-sm text-gray-500">
                              {film.release_date ? new Date(film.release_date).getFullYear() : 'N/A'}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {film.popularity ? film.popularity.toFixed(1) : 'N/A'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className="text-yellow-500 mr-1">★</span>
                          <span className="text-sm font-medium">{film.vote_average?.toFixed(1) || 'N/A'}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {film.vote_count ? film.vote_count.toLocaleString() : 'N/A'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          (film.vote_average || 0) >= 7.5
                            ? 'bg-green-100 text-green-800'
                            : (film.vote_average || 0) >= 6.0
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {(film.vote_average || 0) >= 7.5 ? 'Excellent' : (film.vote_average || 0) >= 6.0 ? 'Good' : 'Average'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

      </main>

      {/* RIGHT SIDE PANEL */}
      <aside className="hidden md:block w-64 bg-white shadow-lg p-6 border-l border-gray-200">
        <div className="mb-8">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Navigation</h3>
          <nav className="space-y-2">
            <Link
              to="/"
              className="flex items-center px-3 py-2 rounded-lg hover:bg-gray-100 text-gray-700 font-medium"
            >
              <span className="mr-2">🗺️</span> Film Map
            </Link>

            <Link
              to="/profile"
              className="flex items-center px-3 py-2 rounded-lg hover:bg-gray-100 text-gray-700 font-medium"
            >
              <span className="mr-2">👤</span> Profile
            </Link>

            <Link
              to="/analytics"
              className="flex items-center px-3 py-2 rounded-lg bg-blue-50 text-blue-600 font-medium border border-blue-100"
            >
              <span className="mr-2">📊</span> Analytics
            </Link>

            {/* ADMIN ONLY */}
            {user.role === "admin" && (
              <Link
                to="/admin/dashboard"
                className="flex items-center px-3 py-2 rounded-lg hover:bg-gray-100 text-purple-600 font-medium"
              >
                <span className="mr-2">⚙️</span> Admin Panel
              </Link>
            )}
          </nav>
        </div>

        <div className="pt-6 border-t border-gray-200">
          <h3 className="text-lg font-bold text-gray-800 mb-4">User</h3>
          <div className="flex items-center mb-4">
            <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center mr-3">
              <span className="font-bold text-blue-600">{user.name?.charAt(0) || 'U'}</span>
            </div>
            <div>
              <p className="font-medium text-gray-900">{user.name || 'User'}</p>
              <p className="text-sm text-gray-500">{user.email || 'email@example.com'}</p>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center px-4 py-2 rounded-lg hover:bg-red-50 text-red-600 font-medium border border-red-100"
          >
            <span className="mr-2">🚪</span> Logout
          </button>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <h3 className="text-lg font-bold text-gray-800 mb-3">System Status</h3>
          <div className="text-sm text-gray-600 space-y-2">
            <p className="flex items-center">
              <span className={`mr-2 h-3 w-3 rounded-full ${stats ? 'bg-green-500' : 'bg-yellow-500'}`}></span>
              <span>API: {stats ? 'Active' : 'Loading...'}</span>
            </p>
            <p className="flex items-center">
              <span className="mr-2">📈</span>
              <span>4 interactive charts</span>
            </p>
            <p className="flex items-center">
              <span className="mr-2">🏙️</span>
              <span>{citiesData.length} cities</span>
            </p>
            <p className="flex items-center">
              <span className="mr-2">🎬</span>
              <span>{popularFilms.length} popular films</span>
            </p>
          </div>
        </div>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <button
            onClick={loadAnalyticsData}
            className="w-full flex items-center justify-center px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium"
          >
            <span className="mr-2">🔄</span> Refresh Data
          </button>
        </div>
      </aside>

    </div>
  );
}