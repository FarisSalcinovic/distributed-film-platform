import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const { login, error, clearError } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  async function handleLogin(e) {
    e.preventDefault();
    clearError();

    try {
      await login(username, password);
      navigate("/profile");
    } catch {
      // error already handled by context
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-sky-50">
      <form onSubmit={handleLogin} className="bg-white p-8 rounded-xl shadow w-80">
        <h1 className="text-2xl font-bold mb-6 text-center">Login</h1>

        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

        <input
          type="text"
          placeholder="Username"
          className="w-full border p-2 rounded mb-4"
          value={username}
          onChange={e => setUsername(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full border p-2 rounded mb-4"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />

        <button type="submit" className="w-full bg-purple-600 text-white py-2 rounded-lg">
          Login
        </button>

        <p className="text-sm text-center mt-4">
          No account?{" "}
          <Link to="/signup" className="text-purple-600 font-medium">
            Sign up
          </Link>
        </p>
      </form>
    </div>
  );
}
