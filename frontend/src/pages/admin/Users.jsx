import AdminLayout from "./AdminLayout";
import { Link } from "react-router-dom";
import { mockUsers } from "../mock/mockUsers";

export default function Users() {
  return (
    <AdminLayout>
      <h1 className="text-3xl font-bold mb-6">Manage Users</h1>

      <table className="w-full border">
        <thead>
          <tr className="bg-gray-200">
            <th className="p-3">ID</th>
            <th className="p-3">Name</th>
            <th className="p-3">Email</th>
            <th className="p-3">Role</th>
            <th className="p-3"></th>
          </tr>
        </thead>

        <tbody>
           {mockUsers.map(user => (
            <tr key={user.id} className="border-b">
              <td className="p-3">{user.id}</td>
              <td className="p-3">{user.name}</td>
              <td className="p-3">{user.email}</td>
              <td className="p-3">{user.role}</td>
              <td className="p-3">
                <Link to={`/admin/user/${user.id}`} className="text-blue-600">Edit</Link>
              </td>
            </tr> 
          ))}
        </tbody>
      </table>
    </AdminLayout>
  );
}
