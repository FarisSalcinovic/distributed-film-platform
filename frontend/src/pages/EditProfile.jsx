import { Link } from "react-router-dom";

export default function EditProfile() {
  // TEMP USER DATA (replace with backend later)
  const user = {
    name: "Sarah Jones",
    email: "sarah@mail.com",
    role: "admin"
  };

  return (
    <div className="flex min-h-screen bg-sky-50">

      {/* MAIN CONTENT */}
      <main className="flex-1 p-10">
        <h1 className="text-3xl font-bold mb-6">Edit Profile</h1>

        <div className="bg-white shadow p-6 rounded-xl max-w-lg">

          {/* Name */}
          <label className="block font-semibold mb-2">Name</label>
          <input
            type="text"
            defaultValue={user.name}
            className="border p-2 rounded w-full mb-4"
          />

          {/* Email */}
          <label className="block font-semibold mb-2">Email</label>
          <input
            type="email"
            defaultValue={user.email}
            className="border p-2 rounded w-full mb-4"
          />

          {/* Buttons */}
          <div className="flex gap-4 mt-4">
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
              Save Changes
            </button>

            <Link
              to="/profile"
              className="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition"
            >
              Cancel
            </Link>
          </div>
        </div>
      </main>

      {/* RIGHT SIDE PANEL */}
      <aside className="w-64 bg-white shadow-lg p-6 space-y-6 text-right">
        {/* <h2 className="text-2xl font-bold">Settings</h2> */}

        <nav className="space-y-3">

          <Link
            to="/profile"
            className="block px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-700 font-medium"
          >
            Profile Overview
          </Link>

          <Link
            to="/edit-profile"
            className="block px-3 py-2 rounded-lg bg-gray-200 text-gray-700 font-medium"
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
