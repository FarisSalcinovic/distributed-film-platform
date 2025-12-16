import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

const API_URL = "http://localhost:8000"; // change if needed

// MOCK ANALYTICS DATA (replace later with backend)
const cityAnalytics = [
  { city: "Paris", movies: 183, sources: 3 },
  { city: "Tokyo", movies: 210, sources: 4 },
  { city: "Madrid", movies: 140, sources: 2 },
  { city: "London", movies: 260, sources: 5 },
  { city: "Toronto", movies: 120, sources: 2 }
];

export default function AnalyticsDashboard() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [error, setError] = useState("");

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
      })
      .catch(() => {
        setError("Could not load user data.");
      });
  }, [navigate]);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-sky-50">
        <p className="text-gray-600">
          {error || "Loading analytics..."}
        </p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-sky-50">

      {/* LEFT CONTENT */}
      <main className="flex-1 p-10">

        <h1 className="text-3xl font-bold mb-6">Analytics Dashboard</h1>

        {/* SUMMARY CARDS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">

          <div className="bg-white shadow p-6 rounded-xl">
            <h3 className="font-semibold text-gray-600">Total Cities Indexed</h3>
            <p className="text-4xl font-bold">{cityAnalytics.length}</p>
          </div>

          <div className="bg-white shadow p-6 rounded-xl">
            <h3 className="font-semibold text-gray-600">Total Movies Indexed</h3>
            <p className="text-4xl font-bold">
              {cityAnalytics.reduce((sum, item) => sum + item.movies, 0)}
            </p>
          </div>

          <div className="bg-white shadow p-6 rounded-xl">
            <h3 className="font-semibold text-gray-600">Total Data Sources</h3>
            <p className="text-4xl font-bold">
              {cityAnalytics.reduce((sum, item) => sum + item.sources, 0)}
            </p>
          </div>

        </div>

        {/* CHART PLACEHOLDERS */}
        <div className="bg-white shadow p-6 rounded-xl mb-10">
          <h2 className="text-xl font-semibold mb-4">Movies per City</h2>
          <div className="w-full h-80 flex items-center justify-center text-gray-400">
            Chart placeholder
          </div>
        </div>

        <div className="bg-white shadow p-6 rounded-xl mb-10">
          <h2 className="text-xl font-semibold mb-4">City Comparison</h2>
          <div className="w-full h-80 flex items-center justify-center text-gray-400">
            Chart placeholder
          </div>
        </div>

      </main>

      {/* RIGHT SIDE PANEL */}
      <aside className="w-64 bg-white shadow-lg p-6 text-right">
        <nav className="space-y-3">

          <Link
            to="/profile"
            className="block px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-700 font-medium"
          >
            Profile Overview
          </Link>


          <Link
            to="/analytics"
            className="block px-3 py-2 rounded-lg bg-gray-200 text-gray-700 font-medium"
          >
            Analytics Dashboard
          </Link>

          {/* ADMIN ONLY */}
          {user.role === "admin" && (
            <Link
              to="/admin/dashboard"
              className="block px-3 py-2 rounded-lg hover:bg-gray-200 text-purple-700 font-medium"
            >
              Admin Dashboard
            </Link>
          )}

          <button
            onClick={handleLogout}
            className="block w-full text-right px-3 py-2 rounded-lg hover:bg-red-100 text-red-600 font-medium"
          >
            Logout
          </button>

        </nav>
      </aside>

    </div>
  );
}
