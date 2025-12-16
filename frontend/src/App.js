// frontend/src/App.js
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";

import MainNavbar from "./components/MainNavbar";
import Footer from "./components/Footer";
import RegionalPopularityMap from "./components/RegionalPopularityMap";

import Profile from "./pages/Profile";
import EditProfile from "./pages/EditProfile";
import CityPage from "./pages/CityPage";
import AnalyticsDashboard from "./pages/AnalyticsDashboard";
import ChartsPage from "./pages/ChartsPage"; // VAŽNO: Dodaj ovaj import

// admin
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

            {/* AUTH */}
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />

            {/* NEW HOME — WORLD MAP */}
            <Route
              path="/"
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

            {/* CHARTS PAGE */}
            <Route
              path="/charts"
              element={
                <ProtectedRoute>
                  <>
                    <MainNavbar />
                    <ChartsPage />
                    <Footer />
                  </>
                </ProtectedRoute>
              }
            />

            {/* OPTIONAL: redirect old map route to home */}
            <Route
              path="/map/regional-popularity"
              element={<Navigate to="/" replace />}
            />

            {/* PROFILE */}
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

            {/* ADMIN */}
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