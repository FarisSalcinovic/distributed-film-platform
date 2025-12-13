import GenreCard from "./GenreCard";

export default function PopularGenres() {
  return (
    <section className="mt-20 px-6 text-center">
      <h2 className="text-3xl font-bold mb-2">Popular Genres</h2>
      <p className="text-gray-600 mb-10">
        Explore movies by your favorite categories 🎭🍿
      </p>

      <div className="flex justify-center gap-6 flex-wrap">
        <GenreCard label="Action" color="#ff4d4d" />
        <GenreCard label="Drama" color="#6c63ff" />
        <GenreCard label="Comedy" color="#ffa726" />
        <GenreCard label="Sci-Fi" color="#26c6da" />
      </div>
    </section>
  );
}