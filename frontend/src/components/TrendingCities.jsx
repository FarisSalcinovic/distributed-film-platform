import CityCard from "../components/CityCard";
import { Link } from "react-router-dom";


export default function TrendingCities() {
  return (
    <section className="mt-20 px-6 text-center">
      <h2 className="text-3xl font-bold mb-2">Trending Cities</h2>
      <p className="text-gray-600 mb-10">
        Cities with best movie selection ✨
      </p>

      <div className="flex justify-center gap-6 flex-wrap">
        <Link to="/city/Mostar">
        <CityCard icon="🗽" name="Mostar" country="Bosnia and Herzegovina" /></Link>
        <Link to="/city/Zenica">
        <CityCard icon="🎬" name="Zenica" country="Bosnia and Herzegovina" /></Link>
        <Link to="/city/Lleida">
        <CityCard icon="🏙️" name="Lleida" country="Spain" /></Link>
        <Link to="/city/Monza">
        <CityCard icon="🧧" name="Monza" country="Italy" /></Link>
      </div>
    </section>
  );
}