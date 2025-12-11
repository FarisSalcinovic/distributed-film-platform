import { Link } from "react-router-dom";

export default function Profile() {
  return (
    <div className="p-10 max-w-3xl mx-auto">
      {/* Profile header */}
      <div className="flex items-center gap-6 mb-10">
        <img
          src="https://i.pravatar.cc/150?img=47"
          alt="profile"
          className="w-24 h-24 rounded-full object-cover"
        />

        <div>
          <h1 className="text-3xl font-bold">Azra Kosovic</h1>
          <p className="text-gray-500">Movie Enthusiast</p>

          {/* Edit button */}
          <Link
            to="/edit-profile"
            className="inline-block mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Edit Profile
          </Link>
        </div>
      </div>

      {/* Basic info */}
      <div className="bg-white shadow rounded-2xl p-6">
        <h2 className="text-xl font-semibold mb-4">About</h2>
        <p className="text-gray-600">
          Hi! I enjoy watching films from all around the world. I use CineCity to
          track what I watch and discover new cities with interesting cinema offerings.
        </p>
      </div>
    </div>
  );
}
