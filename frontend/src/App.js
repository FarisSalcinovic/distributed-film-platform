import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";

import MainNavbar from "./components/MainNavbar";
import Navbar from "./components/Navbar";
import HeroSection from "./components/HeroSection";
import TrendingCities from "./components/TrendingCities";
import PopularGenres from "./components/PopularGenres";
import RecentSearches from "./components/RecentSearches";
import Footer from "./components/Footer";

import Profile from "./pages/Profile"; // nove stranice
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
    // <authProvider>
    <Router>
      <div className="min-h-screen bg-sky-50">
        {/* <Navbar /> */}

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
                </>
              </ProtectedRoute>
            }
          />


          {/* rute navigacija but protected */}
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <MainNavbar />
                <Profile />
              </ProtectedRoute>
            }
          />

          <Route
            path="/edit-profile"
            element={
              <ProtectedRoute>
                <MainNavbar />
                <EditProfile />
              </ProtectedRoute>
            }
          />

          <Route
            path="/city/:cityName"
            element={
              <ProtectedRoute>
                <MainNavbar />
                <CityPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/analytics"
            element={
              <ProtectedRoute>
                <MainNavbar />
                <AnalyticsDashboard />
              </ProtectedRoute>
            }
          />


          <Route
            path="/admin"
            element={
              <ProtectedRoute>
                <MainNavbar />
                <AdminLayout />
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

        <Footer />
       </div>
      </Router>
    //</AuthProvider>
  );
}
