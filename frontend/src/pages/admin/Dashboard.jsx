import { Link } from "react-router-dom";

export default function AdminDashboard() {
  return (
    <div className="flex min-h-screen bg-gray-100">
      
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-md p-6">
        <h2 className="text-2xl font-bold mb-8">Admin Panel</h2>

        <nav className="space-y-4">
          <Link to="/admin/dashboard" className="block text-gray-700 hover:text-blue-600">
            Dashboard
          </Link>

          <Link to="/admin/users" className="block text-gray-700 hover:text-blue-600">
            Users
          </Link>

          <Link to="/admin/etl" className="block text-gray-700 hover:text-blue-600">
            ETL Processes
          </Link>

          <Link to="/admin/stats" className="block text-gray-700 hover:text-blue-600">
            Statistics
          </Link>

          <Link to="/admin/data" className="block text-gray-700 hover:text-blue-600">
            Raw Data Viewer
          </Link>
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-10">
        <h1 className="text-3xl font-bold mb-6">Dashboard Overview</h1>

        {/* Example cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">

          <div className="bg-white p-6 rounded-xl shadow">
            <h3 className="text-lg font-semibold">Total Users</h3>
            <p className="text-3xl font-bold mt-2">104</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow">
            <h3 className="text-lg font-semibold">Movies Indexed</h3>
            <p className="text-3xl font-bold mt-2">3200</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow">
            <h3 className="text-lg font-semibold">ETL Runs</h3>
            <p className="text-3xl font-bold mt-2">12</p>
          </div>
        </div>
      </main>

    </div>
  );
}