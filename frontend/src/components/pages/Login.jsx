import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { supabase } from '../../services/supabaseClient';
import { User, Mail, Lock, Eye, EyeOff } from 'lucide-react';

function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: '',
    password: '',
    rememberMe: false,
  });

  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));

    setErrors((prev) => ({
      ...prev,
      [name]: '',
    }));

    setServerError('');
  };

  const validateForm = () => {
    const newErrors = {};

    if (!form.email.trim()) {
      newErrors.email = 'Email is required.';
    } else if (!/\S+@\S+\.\S+/.test(form.email)) {
      newErrors.email = 'Enter a valid email address.';
    }

    if (!form.password) {
      newErrors.password = 'Password is required.';
    } else if (form.password.length < 6) {
      newErrors.password = 'Password must contain at least 6 characters.';
    }

    setErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }
    setLoading(true);
    setServerError('');
    try {
      await login(form.email, form.password, form.rememberMe);

      navigate('/dashboard');
    } catch (error) {
      setServerError(
        error?.response?.data?.message ||
          error?.message ||
          'Unable to login. Please check your credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: 'http://localhost:5173/dashboard',
      },
    });
    if (error) {
      setServerError(error.message);
    }
  };

  return (
    <main className="relative flex min-h-[calc(100vh-73px)] items-center justify-center overflow-hidden bg-[#050816] px-4 py-10">
      {/* Background glow */}
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-[450px] w-[450px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-900 blur-[130px]" />

      {/* Login container */}
      <div className="relative mx-auto flex min-h-[calc(100vh-160px)] w-full max-w-[500px] items-center justify-center">

        {/* Login Card */}
        <div className="relative w-full rounded-2xl border border-cyan-400/20 bg-slate-950/60 p-8 shadow-2xl shadow-cyan-950/40 backdrop-blur-xl sm:p-10">

          {/* Logo / heading */}
          <div className="mb-6 text-center">
            <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl border border-cyan-400/30 bg-cyan-400/10">
              <span className="text-2xl">🛡️</span>
            </div>

            <p className="mb-2 text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
              Cogni-Fi
            </p>

            <h1 className="text-3xl font-bold text-white">
              Welcome back
            </h1>

            <p className="mt-2 text-sm text-slate-500">
              Sign in to access your dashboard
            </p>
          </div>

          {/* Server error */}
          {serverError && (
            <div className="mb-5 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
              {serverError}
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate>
            {/* Email */}
            <div className="mb-5">
            <label
              htmlFor="email"
              className="mb-2 block text-large font-medium text-slate-300">
              Email address
            </label>

            <div className="relative">
              <span className="pointer-events-none absolute left-4 top-1/2 z-10 -translate-y-1/2 text-slate-400">
                <Mail size={18} strokeWidth={1.8} />
              </span>

              <input
                id="email"
                name="email"
                type="email"
                value={form.email}
                onChange={handleChange}
                placeholder="you@example.com"
                autoComplete="email"
                className={`w-full rounded-xl border bg-slate-900 px-11 py-3.5 text-sm text-white outline-none transition placeholder:text-slate-600 ${
                  errors.email
                    ? 'border-red-500/60'
                    : 'border-slate-700 focus:border-cyan-400'
                }`}
              />
            </div>

            {errors.email && (
              <p className="mt-2 text-xs text-red-400">
                {errors.email}
              </p>
            )}
          </div>

            {/* Password */}
            <div className="mb-5">
              <label
                htmlFor="password"
                className="mb-2 block text-lr font-medium text-slate-300">
                Password
              </label>

              <div className="relative">
                <span className="pointer-events-none absolute left-4 top-1/2 z-10 -translate-y-1/2 text-slate-400">
                  <Lock size={18} strokeWidth={1.8} />
                </span>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  value={form.password}
                  onChange={handleChange}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  className={`w-full rounded-xl border bg-slate-900 px-11 py-3.5 pr-16 text-sm text-white outline-none transition placeholder:text-slate-600 ${
                    errors.password ? 'border-red-500/60' : 'border-slate-700 focus:border-cyan-400' }`}
                />

                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-cyan-400"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <EyeOff size={19} strokeWidth={1.8} />
                  ) : (
                    <Eye size={19} strokeWidth={1.8} />
                  )}
                </button>
              </div>

              {errors.password && (
                <p className="mt-2 text-xs text-red-400">
                  {errors.password}
                </p>
              )}
            </div>

            <div className="mb-7 flex items-center justify-between">
              <label className="flex cursor-pointer items-center gap-3 text-md text-slate-400">
                <input
                  type="checkbox"
                  name="rememberMe"
                  checked={form.rememberMe}
                  onChange={handleChange}
                  className="mr-3 h-4 w-4 accent-cyan-400"
                />
                Remember me
              </label>

              <button
                type="button"
                className="text-sm font-medium text-cyan-400 hover:text-cyan-300"
              >
                Forgot password?
              </button>
            </div>

            {/* Login */}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-cyan-600 py-3.5 text-sm font-bold text-slate-950 transition duration-300 hover:bg-cyan-400 hover:shadow-[0_0_25px_rgba(34,211,238,0.55)] disabled:cursor-not-allowed disabled:opacity-60">
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <div className="relative my-7 flex items-center">
            <div className="h-px flex-1 bg-slate-800" />
            <span className="px-4 text-xs text-slate-500">OR CONTINUE WITH</span>
            <div className="h-px flex-1 bg-slate-800" />
          </div>

          {/* Google Login */}
          <div className="flex gap-4">
            <button
              type="button"
              onClick={handleGoogleLogin}
              className="flex w-full items-center justify-center gap-2 rounded-xl border border-slate-700/80 bg-white/5 py-3 transition duration-300 hover:border-cyan-400/40 hover:bg-cyan-400/5 hover:shadow-[0_0_18px_rgba(34,211,238,0.15)] "  //text-sm font-medium text-slate-300 transition duration-300 hover:bg-white/10 hover:shadow-[0_0_18px_rgba(34,211,238,0.18)]
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 48 48"
              >
                <path
                  fill="#FFC107"
                  d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917"
                />
                <path
                  fill="#FF3D00"
                  d="m6.306 14.691 6.571 4.819C14.655 15.108 18.961 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 16.318 4 9.656 8.337 6.306 14.691"
                />
                <path
                  fill="#4CAF50"
                  d="M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238A11.9 11.9 0 0 1 24 36c-5.202 0-9.619-3.317-11.283-7.946l-6.522 5.025C9.505 39.556 16.227 44 24 44"
                />
                <path
                  fill="#1976D2"
                  d="M43.611 20.083H42V20H24v8h11.303a12.04 12.04 0 0 1-4.087 5.571l.003-.002 6.19 5.238C36.971 39.205 44 34 44 24c0-1.341-.138-2.65-.389-3.917"
                />
              </svg>
              Continue with Google
            </button>
          </div>

          {/* Sign up */}
          <p className="relative top-3 mt-7 text-center text-md text-slate-500">
            Don't have an account?{' '}
            <Link
              to="/signup"
              className="font-semibold text-cyan-400 hover:text-cyan-300"
            >
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}

export default Login;
