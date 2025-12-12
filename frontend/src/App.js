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

// admin pages
import AdminDashboard from "./pages/admin/Dashboard";
import Users from "./pages/admin/Users"; 
import UserDetails from "./pages/admin/UserDetails";
import ETL from "./pages/admin/ETL";
import Stats from "./pages/admin/Stats";
import DataView from "./pages/admin/DataView";
import AdminLayout from "./pages/admin/AdminLayout";

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

          {/* rute navigacija */}
          <Route path="/profile" element={<Profile />} />
          <Route path="/edit-profile" element={<EditProfile />} />
          <Route path="/city/:cityName" element={<CityPage />} />

          {/* admin routes */}
          <Route path="/admin/dashboard" element={<AdminDashboard />} />
          <Route path="/admin/users" element={<Users />} />
          <Route path="/admin/user/:id" element={<UserDetails />} />
          <Route path="/admin/etl" element={<ETL />} />
          <Route path="/admin/stats" element={<Stats />} />
          <Route path="/admin/data" element={<DataView />} />

        </Routes>

        <Footer />
       </div>
      </Router>
  );
}
