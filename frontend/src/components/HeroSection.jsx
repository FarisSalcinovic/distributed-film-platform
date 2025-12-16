export default function HeroSection() {
  return (
    <section className="text-center mt-20 px-6">
      {/* Big Title */}
      <h1 className="text-5xl font-extrabold leading-tight">
        Discover Movies{" "}
        <span className="text-blue-600">
          Perfect for <br /> Your City
        </span>
      </h1>

      {/* Subtitle */}
      <p className="text-gray-600 mt-4 max-w-xl mx-auto">
        Find the best movies and genres tailored to your location 🗺️🎞️
      </p>

      {/* Input + Button */}
      <div className="mt-8 flex justify-center gap-3 flex-col sm:flex-row items-center">
        <input
          type="text"
          placeholder="Enter any city"
          className="border rounded-xl px-4 py-3 w-64 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        <button className="bg-blue-600 hover:bg-blue-700 transition text-white px-8 py-3 rounded-xl font-semibold shadow">
          Discover Movies
        </button>
      </div>
    </section>
  );
}