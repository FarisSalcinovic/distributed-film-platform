import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

const API_URL = "http://localhost:8000"; // change to 5050 if needed

export default function Signup() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSignup(e) {
    e.preventDefault();
    setError("");

    try {
      const res = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          username,
          email,
          password,
          full_name: fullName
        })
      });

      const data = await res.json();

      if (!res.ok) {
        // Backend validation errors (FastAPI style)
        if (Array.isArray(data.detail)) {
          setError(data.detail[0]?.msg || "Validation error");
        } else {
          setError(data.detail || "Signup failed");
        }
        return;
      }

      // ✅ SUCCESS
      // Backend creates user; redirect to login
      navigate("/login");

    } catch (err) {
      setError("Cannot connect to server");
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
          type="text"
          placeholder="Username"
          className="w-full border p-2 rounded mb-4"
          value={username}
          onChange={e => setUsername(e.target.value)}
          required
        />

        <input
          type="text"
          placeholder="Full name"
          className="w-full border p-2 rounded mb-4"
          value={fullName}
          onChange={e => setFullName(e.target.value)}
          required
        />

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
