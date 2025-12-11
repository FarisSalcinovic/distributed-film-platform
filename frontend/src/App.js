import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar";
import HeroSection from "./components/HeroSection";
import TrendingCities from "./components/TrendingCities";
import PopularGenres from "./components/PopularGenres";
import RecentSearches from "./components/RecentSearches";
import Footer from "./components/Footer";

import Profile from "./pages/Profile"; // nove stranice
import EditProfile from "./pages/EditProfile";
import CityPage from "./pages/CityPage";

export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-sky-50">
        <Navbar />

        <Routes>

          {/* Home Page */}
          <Route
            path="/"
            element={
              <>
                <HeroSection />
                <TrendingCities />
                <PopularGenres />
                <RecentSearches />
              </>
            }
          />

          {/* Discover Page */}
          <Route path="/profile" element={<Profile />} />
          <Route path="/edit-profile" element={<EditProfile />} />
          <Route path="/city/:cityName" element={<CityPage />} />

        </Routes>

        <Footer />
       </div>
      </Router>
  );
}
