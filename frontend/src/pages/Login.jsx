import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleLogin(e) {
    e.preventDefault();

    try {
      // 🔁 BACKEND WILL GO HERE LATER
      /*
      const res = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });

      if (!res.ok) throw new Error("Invalid credentials");

      const data = await res.json();
      localStorage.setItem("token", data.access_token);
      */

      // ✅ MOCK SUCCESS (for now)
      localStorage.setItem("token", "mock-token");
      navigate("/");

    } catch (err) {
      setError("Login failed");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-sky-50">
      <form
        onSubmit={handleLogin}
        className="bg-white p-8 rounded-xl shadow w-80"
      >
        <h1 className="text-2xl font-bold mb-6 text-center">Login</h1>

        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

        <input
          type="email"
          placeholder="Email"
          className="w-full border p-2 rounded mb-4"
          value={email}
          onChange={e => setEmail(e.target.value)}
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

        <button
          type="submit"
          className="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition"
        >
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