export default function CityCard({ icon, name, country }) {
  return (
    <div className="bg-white rounded-2xl shadow p-6 w-40 text-center hover:shadow-lg transition cursor-pointer">
      <div className="text-4xl">{icon}</div>
      <h3 className="font-semibold mt-2 text-lg">{name}</h3>
      <p className="text-gray-500 text-sm">{country}</p>
    </div>
  );
}