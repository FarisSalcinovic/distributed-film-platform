import { useParams, Link } from "react-router-dom";
import { mockUsers } from "../mock/mockUsers";
import AdminLayout from "./AdminLayout";

export default function UserDetails() {
  const { id } = useParams();
  const user = mockUsers.find(u => u.id == id);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Edit User</h1>

      <div className="bg-white p-6 rounded-xl shadow max-w-md">
        <label className="font-semibold">Name</label>
        <input className="border p-2 rounded w-full mb-4" defaultValue={user.name} />

        <label className="font-semibold">Email</label>
        <input className="border p-2 rounded w-full mb-4" defaultValue={user.email} />

        <label className="font-semibold">Role</label>
        <select className="border p-2 rounded w-full mb-4" defaultValue={user.role}>
          <option>user</option>
          <option>admin</option>
        </select>

        <button className="bg-blue-600 text-white px-4 py-2 rounded mr-3">Save</button>
        <Link to="/admin/users" className="text-blue-600">Back</Link>
      </div>
    </div>
  );
}
