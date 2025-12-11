import { useParams } from "react-router-dom";
import MovieCard from "../components/MovieCard";

export default function CityPage() {
  const { cityName } = useParams(); // dynamic name from URL

  return (
    <div className="px-8 py-10 max-w-6xl mx-auto">

      {/* City Header */}
      <h1 className="text-4xl font-bold mb-2">{cityName}</h1>
      <p className="text-gray-600 mb-8">
        Discover the best movies and experiences in {cityName}.
      </p>

      {/* Browse by Genre */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Browse by Genre</h2>
        <div className="flex gap-4 flex-wrap">
          <div className="bg-red-400 text-white px-6 py-4 rounded-xl shadow">Action</div>
          <div className="bg-purple-400 text-white px-6 py-4 rounded-xl shadow">Drama</div>
          <div className="bg-orange-400 text-white px-6 py-4 rounded-xl shadow">Comedy</div>
          <div className="bg-green-500 text-white px-6 py-4 rounded-xl shadow">Sci-Fi</div>
        </div>
      </section>

      {/* Popular Movies */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Popular in {cityName}</h2>
        <div className="flex gap-6 flex-wrap">
          <MovieCard title="Movie 1" image="https://picsum.photos/200/300?1" />
          <MovieCard title="Movie 2" image="https://picsum.photos/200/300?2" />
          <MovieCard title="Movie 3" image="https://picsum.photos/200/300?3" />
          <MovieCard title="Movie 4" image="https://picsum.photos/200/300?4" />
        </div>
      </section>

      {/* Coming Soon */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Coming Soon</h2>
        <div className="flex gap-6 flex-wrap">
          <MovieCard title="Soon 1" image="https://picsum.photos/200/300?5" />
          <MovieCard title="Soon 2" image="https://picsum.photos/200/300?6" />
          <MovieCard title="Soon 3" image="https://picsum.photos/200/300?7" />
        </div>
      </section>

      {/* Explore other cities */}
      <div className="bg-red-400 text-white p-8 rounded-3xl shadow mt-8">
        <h3 className="text-2xl font-semibold mb-4">Explore Movies in other cities of country</h3>
        <p className="mb-4">Find movies and popular cinemas around the world.</p>
        <button className="bg-white text-red-600 px-6 py-3 rounded-xl font-semibold">
          Discover Other Cities
        </button>
      </div>

    </div>
  );
}