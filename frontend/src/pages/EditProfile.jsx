import { Link } from "react-router-dom";

export default function EditProfile() {
  return (
    <div className="p-10 max-w-xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Edit Profile</h1>

      <div className="bg-white shadow rounded-2xl p-6">
        <label className="block font-medium">Display Name</label>
        <input 
          type="text"
          className="w-full border rounded-lg p-2 mt-1 mb-4"
          defaultValue="Sarah Johnson"
        />

        <label className="block font-medium">Bio</label>
        <textarea
          className="w-full border rounded-lg p-2 mt-1 mb-4"
          defaultValue="I love exploring cinema from different cultures!"
        ></textarea>

        <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg">
          Save Changes
        </button>

        <Link to="/profile" className="block text-center mt-4 text-blue-600 hover:underline">
          Cancel
        </Link>
      </div>
    </div>
  );
}
