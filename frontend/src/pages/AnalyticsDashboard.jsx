import { Link } from "react-router-dom";

// MOCK DATA
const cityAnalytics = [
  { city: "Paris", movies: 183, sources: 3 },
  { city: "Tokyo", movies: 210, sources: 4 },
  { city: "Madrid", movies: 140, sources: 2 },
  { city: "London", movies: 260, sources: 5 },
  { city: "Toronto", movies: 120, sources: 2 }
];

// TEMP USER MOCK
const user = {
  name: "Sarah Jones",
  email: "sarah@mail.com",
  role: "admin"
};

export default function AnalyticsDashboard() {
  return (
    <div className="flex min-h-screen bg-sky-50">

      {/* LEFT CONTENT */}
      <main className="flex-1 p-10">

        {/* PAGE TITLE */}
        <h1 className="text-3xl font-bold mb-2">Analytics Dashboard</h1>

        {/* BACK TO PROFILE */}
        <Link
          to="/profile"
          className="inline-block mb-6 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-purple-200 transition font-medium"
        >
          ← Back to Profile
        </Link>

        {/* SUMMARY CARDS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">

          <div className="bg-white shadow p-6 rounded-xl">
            <h3 className="font-semibold text-gray-600">Total Cities Index</h3>
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

        {/* LINE CHART SECTION */}
        <div className="bg-white shadow p-6 rounded-xl mb-10">
          <h2 className="text-xl font-semibold mb-4">Movies per City</h2>

          <div className="w-full h-80">
            {/* Recharts line chart is commented for now */}
          </div>
        </div>

        {/* BAR CHART SECTION */}
        <div className="bg-white shadow p-6 rounded-xl mb-10">
          <h2 className="text-xl font-semibold mb-4">City Comparison</h2>

          <div className="w-full h-80">
            {/* Recharts bar chart is commented for now */}
          </div>
        </div>

      </main>

      {/* RIGHT SIDE PANEL */}
      <aside className="w-64 bg-white shadow-lg p-6 space-y-6">


        <nav className="space-y-3 text-right">

          <Link
            to="/profile"
            className="block px-3 py-2 rounded-lg bg-gray-200 text-gray-700 font-medium"
          >
            Profile Overview
          </Link>

          <Link
            to="/edit-profile"
            className="block px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-700 font-medium"
          >
            Edit Profile
          </Link>

          <Link
            to="/analytics"
            className="block px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-700 font-medium"
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

          <Link
            to="/"
            className="block px-3 py-2 rounded-lg hover:bg-red-100 text-red-600 font-medium"
          >
            Logout
          </Link>

        </nav>
      </aside>

    </div>
  );
}
