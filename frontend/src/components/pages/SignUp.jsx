import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
<<<<<<< HEAD
=======
import { supabase } from '../../services/supabaseClient';

//import api from '../../services/api';

import InputField from '../common/InputField';
import PasswordStrengthMeter from '../common/PasswordStrengthMeter';
>>>>>>> 97d4a63cd42c9ed0e0b48932c88bf1f975afecda

function SignUp() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
<<<<<<< HEAD
    agreeTerms: false,
  });

  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
=======
    terms: false,
  });

  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

>>>>>>> 97d4a63cd42c9ed0e0b48932c88bf1f975afecda
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
<<<<<<< HEAD
    setErrors((prev) => ({ ...prev, [name]: '' }));
=======

    setErrors((prev) => ({
      ...prev,
      [name]: '',
    }));

>>>>>>> 97d4a63cd42c9ed0e0b48932c88bf1f975afecda
    setServerError('');
  };

  const validateForm = () => {
    const newErrors = {};

    if (!form.fullName.trim()) {
      newErrors.fullName = 'Full name is required.';
<<<<<<< HEAD
=======
    } else if (form.fullName.trim().length < 2) {
      newErrors.fullName = 'Enter a valid full name.';
>>>>>>> 97d4a63cd42c9ed0e0b48932c88bf1f975afecda
    }

    if (!form.email.trim()) {
      newErrors.email = 'Email is required.';
    } else if (!/\S+@\S+\.\S+/.test(form.email)) {
      newErrors.email = 'Enter a valid email address.';
    }

    if (!form.password) {
      newErrors.password = 'Password is required.';
<<<<<<< HEAD
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
=======
    } else if (form.password.length < 8) {
      newErrors.password =
        'Password must contain at least 8 characters.';
    } else if (
      !/[A-Z]/.test(form.password) ||
      !/[a-z]/.test(form.password) ||
      !/[0-9]/.test(form.password) ||
      !/[^A-Za-z0-9]/.test(form.password)
    ) {
      newErrors.password =
        'Use uppercase, lowercase, number and special character.';
    }

    if (!form.confirmPassword) {
      newErrors.confirmPassword =
        'Please confirm your password.';
    } else if (form.password !== form.confirmPassword) {
      newErrors.confirmPassword =
        'Passwords do not match.';
    }

    if (!form.terms) {
      newErrors.terms =
        'You must accept the Terms & Conditions.';
    }

    return newErrors;
>>>>>>> 97d4a63cd42c9ed0e0b48932c88bf1f975afecda
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

<<<<<<< HEAD
    if (!validateForm()) return;

    setLoading(true);
    setServerError('');

    try {
      // API Registration Hook Placeholder
      // await register(form.fullName, form.email, form.password);
      
      navigate('/login');
    } catch (error) {
      setServerError(error?.message || 'Registration failed. Try again.');
=======
    setServerError('');
    setSuccessMessage('');

    const validationErrors = validateForm();

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setErrors({});
    setLoading(true);

    try {
      const { data, error } = await supabase.auth.signUp({
        email: form.email,
        password: form.password,
        options: {
          data: {
            full_name: form.fullName,
          },
        },
      });

      if (error) {
        throw error;
      }

      if (!data.session) {
        throw new Error('Signup succeeded, but no login session was created.');
      }

      setSuccessMessage('Account created successfully!');

      setTimeout(() => {
        navigate('/dashboard');
      }, 1000);
    } catch (error) {
      setServerError(error.message);
>>>>>>> 97d4a63cd42c9ed0e0b48932c88bf1f975afecda
    } finally {
      setLoading(false);
    }
  };

<<<<<<< HEAD
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
=======
  const userIcon = (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="17"
      height="17"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21a8 8 0 0 1 16 0" />
    </svg>
  );

  const mailIcon = (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="17"
      height="17"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <path d="m3 7 9 6 9-6" />
    </svg>
  );

  const lockIcon = (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="17"
      height="17"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="4" y="10" width="16" height="11" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" />
    </svg>
  );

  const eyeIcon = (visible) => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {visible ? (
        <>
          <path d="M3 3l18 18" />
          <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" />
          <path d="M9.9 4.2A10.5 10.5 0 0 1 12 4c7 0 10 8 10 8a16.7 16.7 0 0 1-3.2 4.4" />
          <path d="M6.6 6.6C3.8 8.5 2 12 2 12s3.5 8 10 8a9.9 9.9 0 0 0 4.1-.9" />
        </>
      ) : (
        <>
          <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" />
          <circle cx="12" cy="12" r="3" />
        </>
      )}
    </svg>
  );

  const handleGoogleSignup = async () => {
    setServerError('');

    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/dashboard`,
      },
    });

    if (error) {
      setServerError(error.message);
    }
  };

  const handleAppleSignup = async () => {
    setServerError('');

    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'apple',
      options: {
        redirectTo: `${window.location.origin}/dashboard`,
      },
    });

    if (error) {
      setServerError(error.message);
    }
  };

  return (
    <main className="min-h-screen bg-[#050816] px-4 py-12 text-slate-200">
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-[450px] w-[450px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-900 blur-[130px]" />
      <div className="mx-auto flex w-full max-w-[500px] items-center justify-center">
        <div className="relative w-full rounded-2xl border border-cyan-400/20 bg-slate-950/60 p-8 shadow-2xl shadow-cyan-950/40 backdrop-blur-xl sm:p-10">

          {/* Heading */}
          <div className="mb-8 text-center">
            <p className="mb-2 text-sm font-semibold tracking-[0.3em] text-cyan-400">
              COGNI-FI
            </p>

            <h1 className="text-3xl font-bold text-white">
              Create your account
            </h1>

            <p className="mt-2 text-sm text-slate-500">
              Sign up to access your network dashboard
            </p>
          </div>

          {/* Server Error */}
          {serverError && (
            <div className="mb-6 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-400">
>>>>>>> 97d4a63cd42c9ed0e0b48932c88bf1f975afecda
              {serverError}
            </div>
          )}

<<<<<<< HEAD
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
=======
          {/* Success */}
          {successMessage && (
            <div className="mb-6 rounded-xl border border-green-500/40 bg-green-500/10 px-4 py-3 text-sm text-green-400">
              {successMessage}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <InputField
              label="Full name"
              name="fullName"
              placeholder="Enter your full name"
              value={form.fullName}
              onChange={handleChange}
              error={errors.fullName}
              icon={userIcon}
            />

            <InputField
              label="Email address"
              name="email"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={handleChange}
              error={errors.email}
              icon={mailIcon}
            />

            <InputField
              label="Password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Create a password"
              value={form.password}
              onChange={handleChange}
              error={errors.password}
              icon={lockIcon}
              rightElement={
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="text-slate-500 transition hover:text-cyan-400"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {eyeIcon(showPassword)}
                </button>
              }
            />

            <PasswordStrengthMeter
              password={form.password}
            />

           <InputField
              label="Confirm password"
              name="confirmPassword"
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="Re-enter your password"
              value={form.confirmPassword}
              onChange={handleChange}
              error={errors.confirmPassword}
              icon={lockIcon}
              rightElement={
                <button
                  type="button"
                  onClick={() =>
                    setShowConfirmPassword(!showConfirmPassword)
                  }
                  className="text-slate-500 transition hover:text-cyan-400"
                  aria-label={
                    showConfirmPassword
                      ? 'Hide password'
                      : 'Show password'
                  }
                >
                  {eyeIcon(showConfirmPassword)}
                </button>
              }
            />

            {/* Terms */}
            <div className="mb-6">
              <label className="flex cursor-pointer items-start gap-4 text-md text-slate-400">
                <input
                  type="checkbox"
                  name="terms"
                  checked={form.terms}
                  onChange={handleChange}
                  className="mt-0.5 h-4 w-4 accent-cyan-400"
                />

                <span>
                  I agree to the{' '}
                  <button
                    type="button"
                    className=" text-cyan-400 hover:text-cyan-300"
                  >
                    Terms & Conditions
                  </button>
                  .
                </span>
              </label>

              {errors.terms && (
                <p className="mt-2 text-xs text-red-400">
                  {errors.terms}
                </p>
              )}
            </div>

            {/* Sign Up */}
>>>>>>> 97d4a63cd42c9ed0e0b48932c88bf1f975afecda
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-cyan-600 py-3.5 text-sm font-bold text-slate-950 transition duration-300 hover:bg-cyan-400 hover:shadow-[0_0_25px_rgba(34,211,238,0.55)] disabled:cursor-not-allowed disabled:opacity-60"
            >
<<<<<<< HEAD
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

=======
              {loading ? 'Creating account...' : 'Create account'}
            </button>

            <div className="my-6 flex items-center gap-3">
              <div className="h-px flex-1 bg-slate-700" />
              <span className="text-xs text-slate-500">OR CONTINUE WITH</span>
              <div className="h-px flex-1 bg-slate-700" />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={handleGoogleSignup}
                className="flex items-center justify-center gap-2 rounded-xl border border-slate-700/80 bg-white/5 py-3 transition duration-300 hover:border-cyan-400/40 hover:bg-cyan-400/5 hover:shadow-[0_0_18px_rgba(34,211,238,0.15)]"
              >
                {/* Google icon */}
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 48 48"
                >
                  <path
                    fill="#FFC107"
                    d="M43.611 20.083H42V20H24v8h11.303C33.649 32.657 29.22 36 24 36c-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917"
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

                <span className="text-sm text-slate-300">Continue with Google</span>
              </button>

              <button
                type="button"
                onClick={handleAppleSignup}
                className="flex items-center justify-center gap-2 rounded-xl border border-slate-700/80 bg-white/5 py-3 transition duration-300 hover:border-cyan-400/40 hover:bg-cyan-400/5 hover:shadow-[0_0_18px_rgba(34,211,238,0.15)]"
              >
                {/* Apple icon */}
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  className="text-white"
                >
                  <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.09.8 1.19-.24 2.33-.93 3.6-.84 1.54.12 2.7.74 3.47 1.88-3.18 1.9-2.43 6.08.49 7.26-.58 1.52-1.34 3.03-2.65 3.87zM12.03 7.25C11.88 4.99 13.71 3.13 15.78 3c.29 2.6-2.36 4.52-3.75 4.25z" />
                </svg>

                <span className="text-sm text-slate-300">Continue with Apple</span>
              </button>
            </div>

          </form>

          {/* Login */}
          <p className="relative top-3 mt-7 text-center text-md text-slate-500">
            Already have an account?{' '}
            <Link
              to="/login"
              className="font-semibold text-cyan-400 hover:text-cyan-300"
            >
              Sign in
            </Link>
          </p>
>>>>>>> 97d4a63cd42c9ed0e0b48932c88bf1f975afecda
        </div>
      </div>
    </main>
  );
}

export default SignUp;