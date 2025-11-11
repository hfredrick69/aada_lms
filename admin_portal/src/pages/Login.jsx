import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

const Login = () => {
  const navigate = useNavigate();
  const { login, error, setError } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (event) => {
    setForm((prev) => ({ ...prev, [event.target.name]: event.target.value }));
    setError(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    try {
      await login(form);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{ backgroundColor: "#f0f6ff" }}>
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Admin Portal</h1>
          <p className="text-base text-gray-600 mt-2">Students Are Our Top Priority!!!</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email*
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              autoComplete="email"
              className="block w-full rounded-md border border-gray-300 bg-white px-3 py-2.5 text-base focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-200"
              value={form.email}
              onChange={handleChange}
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password*
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              autoComplete="current-password"
              className="block w-full rounded-md border border-gray-300 bg-white px-3 py-2.5 text-base focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-200"
              value={form.password}
              onChange={handleChange}
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            type="submit"
            disabled={submitting}
            className="w-full text-white py-3 rounded-md text-base font-medium transition-colors disabled:opacity-60 mt-6 bg-[#d4af37] hover:bg-[#b5942d] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#f0d98a] focus-visible:ring-offset-2 focus-visible:ring-offset-white"
          >
            {submitting ? "SIGNING IN..." : "SIGN IN"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
