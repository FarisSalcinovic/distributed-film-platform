import { Link } from "react-router-dom";

export default function AdminLayout({ children }) {
  return (
    <div className="flex min-h-screen bg-sky-50">

      {/* MAIN CONTENT LEFT */}
      <main className="flex-1 p-10">
        {children}
      </main>

      {/* RIGHT SIDE PANEL (matches your Profile UI) */}
      <aside className="w-64 bg-white shadow-lg p-6 space-y-6 text-right">
        <h2 className="text-2xl font-bold">Admin Panel</h2>

        <nav className="space-y-3">

          <Link
            to="/admin/dashboard"
            className="block px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-800 font-medium"
          >
            Dashboard Overview
          </Link>

          <Link
            to="/admin/users"
            className="block px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-800 font-medium"
          >
            Manage Users
          </Link>

          <Link
            to="/admin/etl"
            className="block px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-800 font-medium"
          >
            ETL Processes
          </Link>

          <Link
            to="/admin/stats"
            className="block px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-800 font-medium"
          >
            Statistics
          </Link>

          <Link
            to="/admin/data"
            className="block px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-800 font-medium"
          >
            Raw Data Viewer
          </Link>

          <Link
            to="/profile"
            className="block px-3 py-2 rounded-lg hover:bg-gray-200 text-purple-700 font-medium"
          >
            Back to Profile
          </Link>

        </nav>
      </aside>

    </div>
  );
}
