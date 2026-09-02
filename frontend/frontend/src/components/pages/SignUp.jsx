import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { supabase } from '../../services/supabaseClient';
import { User, Mail, Lock, Eye, EyeOff } from 'lucide-react';
import InputField from '../common/InputField';
import PasswordStrengthMeter from '../common/PasswordStrengthMeter';

function SignUp() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
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

    if (!form.fullName.trim()) {
      newErrors.fullName = 'Full name is required.';
    } else if (form.fullName.trim().length < 2) {
      newErrors.fullName = 'Enter a valid full name.';
    }

    if (!form.email.trim()) {
      newErrors.email = 'Email is required.';
    } else if (!/\S+@\S+\.\S+/.test(form.email)) {
      newErrors.email = 'Enter a valid email address.';
    }

    if (!form.password) {
      newErrors.password = 'Password is required.';
    } else if (form.password.length < 8) {
      newErrors.password = 'Password must contain at least 8 characters.';
    } else if (
      !/[A-Z]/.test(form.password) ||
      !/[a-z]/.test(form.password) ||
      !/[0-9]/.test(form.password) ||
      !/[^A-Za-z0-9]/.test(form.password)
    ) {
      newErrors.password = 'Use uppercase, lowercase, number and special character.';
    }

    if (!form.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password.';
    } else if (form.password !== form.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match.';
    }

    if (!form.terms) {
      newErrors.terms = 'You must accept the Terms & Conditions.';
    }

    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

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
    } finally {
      setLoading(false);
    }
  };

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
              {serverError}
            </div>
          )}

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
              icon={<User size={17} strokeWidth={1.7} />}
            />

            <InputField
              label="Email address"
              name="email"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={handleChange}
              error={errors.email}
              icon={<Mail size={17} strokeWidth={1.7} />}
            />

            <InputField
              label="Password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Create a password"
              value={form.password}
              onChange={handleChange}
              error={errors.password}
              icon={<Lock size={17} strokeWidth={1.7} />}
              rightElement={
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="text-slate-500 transition hover:text-cyan-400"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <EyeOff size={18} strokeWidth={1.7} />
                  ) : (
                    <Eye size={18} strokeWidth={1.7} />
                  )}
                </button>
              }
            />

            <PasswordStrengthMeter password={form.password} />

            <InputField
              label="Confirm password"
              name="confirmPassword"
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="Re-enter your password"
              value={form.confirmPassword}
              onChange={handleChange}
              error={errors.confirmPassword}
              icon={<Lock size={17} strokeWidth={1.7} />}
              rightElement={
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="text-slate-500 transition hover:text-cyan-400"
                  aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                >
                  {showConfirmPassword ? (
                    <EyeOff size={18} strokeWidth={1.7} />
                  ) : (
                    <Eye size={18} strokeWidth={1.7} />
                  )}
                </button>
              }
            />

            {/* Terms */}
            <div className="mb-6">
              <label className="flex cursor-pointer items-start gap-3 text-sm text-slate-400">
                <input
                  type="checkbox"
                  name="terms"
                  checked={form.terms}
                  onChange={handleChange}
                  className="mt-0.5 h-4 w-4 accent-cyan-400 rounded"
                />
                <span>
                  I agree to the{' '}
                  <button
                    type="button"
                    className="text-cyan-400 hover:text-cyan-300"
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
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-cyan-600 py-3.5 text-sm font-bold text-slate-950 transition duration-300 hover:bg-cyan-400 hover:shadow-[0_0_25px_rgba(34,211,238,0.55)] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? 'Creating account...' : 'Create account'}
            </button>

            <div className="my-6 flex items-center gap-3">
              <div className="h-px flex-1 bg-slate-700" />
              <span className="text-xs text-slate-500">OR CONTINUE WITH</span>
              <div className="h-px flex-1 bg-slate-700" />
            </div>

            <div className="grid grid-cols-1 gap-3">
              <button
                type="button"
                onClick={handleGoogleSignup}
                className="flex items-center justify-center gap-2 rounded-xl border border-slate-700/80 bg-white/5 py-3 transition duration-300 hover:border-cyan-400/40 hover:bg-cyan-400/5 hover:shadow-[0_0_18px_rgba(34,211,238,0.15)]"
              >
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
            </div>
          </form>

          {/* Login Link */}
          <p className="mt-6 text-center text-sm text-slate-500">
            Already have an account?{' '}
            <Link
              to="/login"
              className="font-semibold text-cyan-400 hover:text-cyan-300"
            >
              Sign in
            </Link>
          </p>

        </div>
      </div>
    </main>
  );
}

export default SignUp;