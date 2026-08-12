import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function SignUp() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeTerms: false,
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
    setErrors((prev) => ({ ...prev, [name]: '' }));
    setServerError('');
  };

  const validateForm = () => {
    const newErrors = {};

    if (!form.fullName.trim()) {
      newErrors.fullName = 'Full name is required.';
    }

    if (!form.email.trim()) {
      newErrors.email = 'Email is required.';
    } else if (!/\S+@\S+\.\S+/.test(form.email)) {
      newErrors.email = 'Enter a valid email address.';
    }

    if (!form.password) {
      newErrors.password = 'Password is required.';
    } else if (form.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters.';
    }

    if (form.password !== form.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match.';
    }

    if (!form.agreeTerms) {
      newErrors.agreeTerms = 'You must agree to the terms and conditions.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setLoading(true);
    setServerError('');

    try {
      // API Registration Hook Placeholder
      // await register(form.fullName, form.email, form.password);
      
      navigate('/login');
    } catch (error) {
      setServerError(error?.message || 'Registration failed. Try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative flex min-h-[calc(100vh-73px)] items-center justify-center overflow-hidden bg-[#050816] px-4 py-10">
      
      {/* Background glow matching the Login style */}
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-900/60 blur-[130px]" />

      <div className="relative mx-auto flex min-h-[calc(100vh-160px)] w-full max-w-[520px] items-center justify-center">
        <div className="relative w-full rounded-2xl border border-cyan-400/20 bg-slate-950/60 p-8 shadow-2xl shadow-cyan-950/40 backdrop-blur-xl sm:p-10">
          
          {/* Header */}
          <div className="mb-6 text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-cyan-400/30 bg-cyan-400/10">
              <span className="text-2xl">🛡️</span>
            </div>
            <p className="mb-1 text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">CogniFi</p>
            <h1 className="text-3xl font-bold text-white">Create Account</h1>
            <p className="mt-1 text-sm text-slate-500">Get started with your security console monitoring profile</p>
          </div>

          {serverError && (
            <div className="mb-5 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
              {serverError}
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate className="space-y-4">
            
            {/* Full Name Input */}
            <div>
              <label htmlFor="fullName" className="mb-1.5 block text-sm font-medium text-slate-300">Full Name</label>
              <div className="relative">
                <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">👤</span>
                <input
                  id="fullName"
                  name="fullName"
                  type="text"
                  value={form.fullName}
                  onChange={handleChange}
                  placeholder="John Doe"
                  className={`w-full rounded-xl border bg-slate-900 px-11 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 ${
                    errors.fullName ? 'border-red-500/60' : 'border-slate-700 focus:border-cyan-400'
                  }`}
                />
              </div>
              {errors.fullName && <p className="mt-1.5 text-xs text-red-400">{errors.fullName}</p>}
            </div>

            {/* Email Input */}
            <div>
              <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-slate-300">Email Address</label>
              <div className="relative">
                <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">✉️</span>
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="you@example.com"
                  className={`w-full rounded-xl border bg-slate-900 px-11 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 ${
                    errors.email ? 'border-red-500/60' : 'border-slate-700 focus:border-cyan-400'
                  }`}
                />
              </div>
              {errors.email && <p className="mt-1.5 text-xs text-red-400">{errors.email}</p>}
            </div>

            {/* Password Input */}
            <div>
              <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-slate-300">Password</label>
              <div className="relative">
                <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">🔒</span>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  value={form.password}
                  onChange={handleChange}
                  placeholder="Create a strong password"
                  className={`w-full rounded-xl border bg-slate-900 px-11 py-3 pr-12 text-sm text-white outline-none transition placeholder:text-slate-600 ${
                    errors.password ? 'border-red-500/60' : 'border-slate-700 focus:border-cyan-400'
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-cyan-400 text-xs"
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>
              {errors.password && <p className="mt-1.5 text-xs text-red-400">{errors.password}</p>}
            </div>

            {/* Confirm Password Input */}
            <div>
              <label htmlFor="confirmPassword" className="mb-1.5 block text-sm font-medium text-slate-300">Confirm Password</label>
              <div className="relative">
                <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">🛡️</span>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showPassword ? 'text' : 'password'}
                  value={form.confirmPassword}
                  onChange={handleChange}
                  placeholder="Repeat your password"
                  className={`w-full rounded-xl border bg-slate-900 px-11 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 ${
                    errors.confirmPassword ? 'border-red-500/60' : 'border-slate-700 focus:border-cyan-400'
                  }`}
                />
              </div>
              {errors.confirmPassword && <p className="mt-1.5 text-xs text-red-400">{errors.confirmPassword}</p>}
            </div>

            {/* Terms and Conditions */}
            <div className="pt-1">
              <label className="flex cursor-pointer items-start text-xs text-slate-400">
                <input
                  type="checkbox"
                  name="agreeTerms"
                  checked={form.agreeTerms}
                  onChange={handleChange}
                  className="mr-3 mt-0.5 h-4 w-4 accent-cyan-400 rounded"
                />
                <span>
                  I agree to the{' '}
                  <button type="button" className="text-cyan-400 hover:underline">Terms of Service</button>
                  {' '}and{' '}
                  <button type="button" className="text-cyan-400 hover:underline">Privacy Policy</button>.
                </span>
              </label>
              {errors.agreeTerms && <p className="mt-1 text-xs text-red-400">{errors.agreeTerms}</p>}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-cyan-600 py-3.5 text-sm font-bold text-slate-950 transition duration-300 hover:bg-cyan-400 hover:shadow-[0_0_25px_rgba(34,211,238,0.55)] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? 'Registering Account...' : 'Sign Up'}
            </button>
          </form>

          {/* Bottom redirection Link */}
          <p className="mt-6 text-center text-sm text-slate-500">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold text-cyan-400 hover:text-cyan-300">
              Sign in
            </Link>
          </p>

        </div>
      </div>
    </main>
  );
}

export default SignUp;