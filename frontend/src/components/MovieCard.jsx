export default function MovieCard({ title, image }) {
  return (
    <div className="w-40 bg-white rounded-2xl shadow hover:shadow-lg transition cursor-pointer overflow-hidden">
      {/* Poster */}
      <img 
        src={image} 
        alt={title} 
        className="h-56 w-full object-cover"
      />

      {/* Title */}
      <div className="p-3">
        <h3 className="font-semibold text-gray-900 text-sm leading-tight">
          {title}
        </h3>
      </div>
    </div>
  );
}
