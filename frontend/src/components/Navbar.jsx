import { Link } from "react-router-dom"; // link za navigaciju izmedju stranica
import movieIcon from "../images/movie.png";


export default function Navbar() {
  return (
    <nav className="flex justify-between items-center px-10 py-6 shadow-sm bg-white">
      {/* Left: Logo */}
      <div className="text-2xl font-bold">
        <Link to="/">
        <img src={movieIcon} alt="CineCity Logo" className="inline-block w-8 h-8 mr-1" />
         CineCity
         </Link></div>

      {/* Center: Navigation links */}
      <ul className="flex gap-8 text-gray-700 font-medium">
        <li className="hover:text-blue-600 cursor-pointer">
          <Link to="/">Home</Link></li>
        <li className="hover:text-blue-600 cursor-pointer">Discover</li>
        <li className="hover:text-blue-600 cursor-pointer">Trending</li>
        <li className="hover:text-blue-600 cursor-pointer">About</li>
      </ul>

      {/* Right: Icons */}
      <div className="flex gap-4 text-xl">
        <button className="hover:text-blue-600">
          <Link to="/profile">👤</Link>
        </button>
      </div>
    </nav>
  );
}
