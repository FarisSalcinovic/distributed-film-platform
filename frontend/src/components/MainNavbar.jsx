import { Link } from "react-router-dom";
import { FaMapMarkerAlt } from "react-icons/fa";
import movieIcon from "../images/movie.png";

export default function MainNavbar() {
  return (
    <nav className="flex justify-between items-center px-6 md:px-10 py-4 md:py-6 shadow-sm bg-white sticky top-0 z-50">
      {/* Left: Logo */}
      <div className="text-xl md:text-2xl font-bold">
        <Link to="/" className="flex items-center hover:text-blue-600 transition-colors">
          <img src={movieIcon} alt="CineCity Logo" className="inline-block w-6 h-6 md:w-8 md:h-8 mr-2" />
          <span className="hidden sm:inline">CineCity</span>
        </Link>
      </div>

      {/* Center: Navigation links */}
      <ul className="flex gap-4 md:gap-8 text-gray-700 font-medium">
        <li className="hover:text-blue-600 cursor-pointer transition-colors">
          <Link to="/" className="flex items-center">
            <span className="hidden sm:inline">Home</span>
            <span className="sm:hidden">🏠</span>
          </Link>
        </li>
        <li className="hover:text-blue-600 cursor-pointer transition-colors">
          <Link to="/map/regional-popularity" className="flex items-center">
            <FaMapMarkerAlt className="mr-1 md:mr-2" />
            <span className="hidden sm:inline">World Map</span>
          </Link>
        </li>
        <li className="hover:text-blue-600 cursor-pointer transition-colors hidden md:block">
          <Link to="/analytics">Analytics</Link>
        </li>
        <li className="hover:text-blue-600 cursor-pointer transition-colors hidden md:block">
          <Link to="/admin/dashboard">Admin</Link>
        </li>
      </ul>

      {/* Right: Icons */}
      <div className="flex gap-4 text-lg md:text-xl">
        <button className="hover:text-blue-600 transition-colors">
          <Link to="/profile" className="flex items-center">
            <span className="text-xl md:text-2xl">👤</span>
            <span className="hidden md:inline ml-2 text-sm">Profile</span>
          </Link>
        </button>
      </div>
    </nav>
  );
}