import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function Signup() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSignup(e) {
    e.preventDefault();

    try {
      /*
      await fetch("http://localhost:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      */

      // ✅ MOCK SUCCESS
      navigate("/login");

    } catch (err) {
      setError("Signup failed");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-sky-50">
      <form
        onSubmit={handleSignup}
        className="bg-white p-8 rounded-xl shadow w-80"
      >
        <h1 className="text-2xl font-bold mb-6 text-center">Sign Up</h1>

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
          Create account
        </button>

        <p className="text-sm text-center mt-4">
          Already have an account?{" "}
          <Link to="/login" className="text-purple-600 font-medium">
            Login
          </Link>
        </p>
      </form>
    </div>
  );
}
