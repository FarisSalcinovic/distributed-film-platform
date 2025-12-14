import { Link, Outlet } from "react-router-dom";

export default function AdminLayout() {
  return (
    <div className="flex min-h-screen bg-sky-50">

      <main className="flex-1 p-10">
        <Outlet />
      </main>

      <aside className="w-64 bg-white shadow-lg p-6 space-y-6 text-right font-semibold">
        <h2 className="text-2xl font-bold">Admin Panel</h2>

        <nav className="space-y-3">

          <Link to="./dashboard" className="block px-3 py-2 rounded-lg hover:bg-gray-200">
            Dashboard Overview
          </Link>

          <Link to="./users" className="block px-3 py-2 rounded-lg hover:bg-gray-200">
            Manage Users
          </Link>

          <Link to="./etl" className="block px-3 py-2 rounded-lg hover:bg-gray-200">
            ETL Processes
          </Link>

          <Link to="./data" className="block px-3 py-2 rounded-lg hover:bg-gray-200">
            Raw Data Viewer
          </Link>

          <Link to="/profile" className="block px-3 py-2 rounded-lg hover:bg-gray-200 text-purple-700">
            Back to Profile
          </Link>

        </nav>
      </aside>

    </div>
  );
}
