import React from 'react';

function PasswordStrengthMeter({ password }) {
  if (!password) return null;

  const checks = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[^A-Za-z0-9]/.test(password),
  };

  const score = Object.values(checks).filter(Boolean).length;

  let strength = 'Weak';
  let strengthColor = 'text-red-400';

  if (score >= 4) {
    strength = 'Strong';
    strengthColor = 'text-green-400';
  } else if (score >= 3) {
    strength = 'Medium';
    strengthColor = 'text-yellow-400';
  }

  return (
    <div className="mt-[-12px] mb-5">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs text-slate-500">
          Password strength
        </span>

        <span className={`text-xs font-medium ${strengthColor}`}>
          {strength}
        </span>
      </div>

      <div className="mb-3 flex gap-1">
        {[1, 2, 3, 4, 5].map((bar) => (
          <div
            key={bar}
            className={`h-1 flex-1 rounded ${
              bar <= score
                ? score >= 4
                  ? 'bg-green-400'
                  : score >= 3
                    ? 'bg-yellow-400'
                    : 'bg-red-400'
                : 'bg-slate-800'
            }`}
          />
        ))}
      </div>

      <div className="space-y-1 text-xs text-slate-500">
        <p className={checks.length ? 'text-green-400' : ''}>
          ✓ At least 8 characters
        </p>
        <p className={checks.uppercase ? 'text-green-400' : ''}>
          ✓ One uppercase letter
        </p>
        <p className={checks.lowercase ? 'text-green-400' : ''}>
          ✓ One lowercase letter
        </p>
        <p className={checks.number ? 'text-green-400' : ''}>
          ✓ One number
        </p>
        <p className={checks.special ? 'text-green-400' : ''}>
          ✓ One special character
        </p>
      </div>
    </div>
  );
}

export default PasswordStrengthMeter;