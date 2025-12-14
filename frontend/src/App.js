import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";

import MainNavbar from "./components/MainNavbar";
import Navbar from "./components/Navbar";
import HeroSection from "./components/HeroSection";
import TrendingCities from "./components/TrendingCities";
import PopularGenres from "./components/PopularGenres";
import RecentSearches from "./components/RecentSearches";
import Footer from "./components/Footer";
import RegionalPopularityMap from "./components/RegionalPopularityMap"; // NOVO: Dodaj ovaj import

import Profile from "./pages/Profile";
import EditProfile from "./pages/EditProfile";
import CityPage from "./pages/CityPage";
import AnalyticsDashboard from "./pages/AnalyticsDashboard";

// admin pages
import AdminDashboard from "./pages/admin/Dashboard";
import Users from "./pages/admin/Users";
import UserDetails from "./pages/admin/UserDetails";
import ETL from "./pages/admin/ETL";
import Stats from "./pages/admin/Stats";
import DataView from "./pages/admin/DataView";
import AdminLayout from "./pages/admin/AdminLayout";

import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ProtectedRoute from "./pages/ProtectedRoute";

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-sky-50">
          <Routes>

            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />

            {/* Home Page but protected */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <>
                    <MainNavbar />
                    <HeroSection />
                    <TrendingCities />
                    <PopularGenres />
                    <RecentSearches />
                    <Footer />
                  </>
                </ProtectedRoute>
              }
            />

            {/* World Film Map - NOVA RUTA */}
            <Route
              path="/map/regional-popularity"
              element={
                <ProtectedRoute>
                  <>
                    <MainNavbar />
                    <div className="container mx-auto px-4 py-8">
                      <RegionalPopularityMap />
                    </div>
                    <Footer />
                  </>
                </ProtectedRoute>
              }
            />

            {/* Profile rute */}
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <>
                    <MainNavbar />
                    <Profile />
                    <Footer />
                  </>
                </ProtectedRoute>
              }
            />

            <Route
              path="/edit-profile"
              element={
                <ProtectedRoute>
                  <>
                    <MainNavbar />
                    <EditProfile />
                    <Footer />
                  </>
                </ProtectedRoute>
              }
            />

            <Route
              path="/city/:cityName"
              element={
                <ProtectedRoute>
                  <>
                    <MainNavbar />
                    <CityPage />
                    <Footer />
                  </>
                </ProtectedRoute>
              }
            />

            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <>
                    <MainNavbar />
                    <AnalyticsDashboard />
                    <Footer />
                  </>
                </ProtectedRoute>
              }
            />

            {/* Admin rute */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute>
                  <>
                    <MainNavbar />
                    <AdminLayout />
                    <Footer />
                  </>
                </ProtectedRoute>
              }
            >
              <Route path="dashboard" element={<AdminDashboard />} />
              <Route path="users" element={<Users />} />
              <Route path="user/:id" element={<UserDetails />} />
              <Route path="etl" element={<ETL />} />
              <Route path="stats" element={<Stats />} />
              <Route path="data" element={<DataView />} />
            </Route>

          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}