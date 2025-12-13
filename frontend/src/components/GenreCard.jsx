export default function GenreCard({ label, color }) {
  return (
    <div
      className={`rounded-2xl shadow p-6 w-40 h-40 text-center text-white font-semibold cursor-pointer hover:scale-105 transition`}
      style={{ backgroundColor: color }}
    >
      <div className="text-lg mt-8">{label}</div>
    </div>
  );
}