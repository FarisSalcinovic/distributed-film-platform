import { Link } from "react-router-dom";

export default function AdminLayout({ children }) {
  return (
    <div className="flex min-h-screen bg-gray-100">
      
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-md p-6">
        <h2 className="text-2xl font-bold mb-8">Admin Panel</h2>

        <nav className="space-y-4">
          <Link to="/admin/dashboard" className="block text-gray-700 hover:text-blue-600">Dashboard</Link>
          <Link to="/admin/users" className="block text-gray-700 hover:text-blue-600">Users</Link>
          <Link to="/admin/etl" className="block text-gray-700 hover:text-blue-600">ETL Processes</Link>
          <Link to="/admin/stats" className="block text-gray-700 hover:text-blue-600">Statistics</Link>
          <Link to="/admin/data" className="block text-gray-700 hover:text-blue-600">Raw Data</Link>
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-10">
        {children}
      </main>
    </div>
  );
}
