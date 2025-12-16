import { Link } from "react-router-dom";
import { FaMapMarkerAlt } from "react-icons/fa";
import { useAuth } from "../context/AuthContext";
import movieIcon from "../images/movie.png";

export default function MainNavbar() {
  const { user } = useAuth();

  return (
    <nav className="flex justify-between items-center px-6 md:px-10 py-4 md:py-6 shadow-sm bg-white sticky top-0 z-50">
      
      {/* Left: Logo */}
      <div className="text-xl md:text-2xl font-bold">
        <Link to="/" className="flex items-center hover:text-blue-600 transition-colors">
          <img
            src={movieIcon}
            alt="CineCity Logo"
            className="inline-block w-6 h-6 md:w-8 md:h-8 mr-2"
          />
          <span className="hidden sm:inline">CineCity</span>
        </Link>
      </div>

      {/* Center: Navigation links */}
      <ul className="flex gap-4 md:gap-8 text-gray-700 font-medium">

        <li className="hover:text-blue-600 cursor-pointer transition-colors">
          <Link to="/map/regional-popularity" className="flex items-center">
            <FaMapMarkerAlt className="mr-1 md:mr-2 text-purple-900" />
            <span className="hidden sm:inline text-purple-900">World Map</span>
          </Link>
        </li>

        <li className="hover:text-blue-600 cursor-pointer transition-colors hidden md:block">
          <Link to="/analytics">Analytics</Link>
        </li>

        {/* ADMIN ONLY */}
        {user?.role === "admin" && (
          <li className="hover:text-blue-600 cursor-pointer transition-colors hidden md:block">
            <Link to="/admin/dashboard">Admin</Link>
          </li>
        )}
      </ul>

      {/* Right: Profile */}
      <div className="flex gap-4 md:gap-8 text-gray-700 font-medium">
        <Link to="/profile" className="flex items-center hover:text-blue-600 transition-colors">
          <span className="text-xl md:text-2xl">👤</span>
        </Link>
      </div>

    </nav>
  );
}
