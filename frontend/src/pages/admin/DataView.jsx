import AdminLayout from "./AdminLayout";
import { mockRawData } from "../mock/mockRawData";

export default function DataView() {
  return (
    <AdminLayout>
      <h1 className="text-3xl font-bold mb-6">Raw Data</h1>

      <pre className="bg-white p-6 rounded-xl shadow text-sm">
        {JSON.stringify(mockRawData, null, 2)}
      </pre>
    </AdminLayout>
  );
}
