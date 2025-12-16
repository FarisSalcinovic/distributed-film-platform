import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

const API_URL = "http://localhost:8000"; // or 5050

export default function Profile() {
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
          // ❌ token invalid → real logout
          handleLogout();
          return null;
        }

        if (!res.ok) {
          // ⚠️ backend error but keep user logged in
          throw new Error("Failed to load profile");
        }

        return res.json();
      })
      .then(data => {
        if (data) setUser(data);
      })
      .catch(() => {
        setError("Could not load profile data.");
      });
  }, [navigate]);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-sky-50">
        <p className="text-gray-600">
          {error || "Loading profile..."}
        </p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-sky-50">

      {/* MAIN CONTENT */}
      <main className="flex-1 p-10">
        <h1 className="text-3xl font-bold mb-6">Profile Overview</h1>

        <div className="bg-white shadow p-6 rounded-xl max-w-lg">
          <p className="text-lg font-semibold">Name:</p>
          <p className="mb-4 text-gray-700">
            {user.full_name || user.username}
          </p>

          <p className="text-lg font-semibold">Email:</p>
          <p className="mb-4 text-gray-700">{user.email}</p>

          <p className="text-lg font-semibold">Role:</p>
          <p className="text-gray-700 capitalize">{user.role}</p>
        </div>
      </main>

      {/* SIDE PANEL */}
      <aside className="w-64 bg-white shadow-lg p-6 text-right">
        <nav className="space-y-3">

          <Link
            to="/profile"
            className="block px-3 py-2 rounded-lg bg-gray-200 text-gray-700 font-medium"
          >
            Profile Overview
          </Link>

          <Link
            to="/analytics"
            className="block px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-700 font-medium"
          >
            Analytics Dashboard
          </Link>

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
