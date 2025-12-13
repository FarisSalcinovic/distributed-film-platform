import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";

export default function Profile() {
  // TEMP USER MOCK (later replaced by backend)
  const user = {
    name: "Sarah Jones",
    email: "sarah@mail.com",
    role: "admin" // change to "user" to hide admin panel link
  };

  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/login");
  }




  return (
    <div className="flex min-h-screen bg-sky-50">

      {/* MAIN PROFILE CONTENT */}
      <main className="flex-1 p-10">
        <h1 className="text-3xl font-bold mb-6">Profile Overview</h1>

        <div className="bg-white shadow p-6 rounded-xl max-w-lg">
          <p className="text-lg font-semibold">Name:</p>
          <p className="mb-4 text-gray-700">{user.name}</p>

          <p className="text-lg font-semibold">Email:</p>
          <p className="mb-4 text-gray-700">{user.email}</p>

          <p className="text-lg font-semibold">Role:</p>
          <p className="text-gray-700 capitalize">{user.role}</p>
        </div>
      </main>

      {/* RIGHT SIDE PANEL */}
      <aside className="w-64 bg-white shadow-lg p-6 space-y-6 text-right">
        {/* <h2 className="text-2xl font-bold">Settings</h2> */}

        <nav className="space-y-3">
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
