import React from 'react';

function InputField({
  label,
  name,
  type = 'text',
  placeholder,
  value,
  onChange,
  error,
  icon,
  rightElement,
}) {
  return (
    <div className="mb-5">
      <label
        htmlFor={name}
        className="mb-2 block text-lr font-medium text-slate-300"
      >
        {label}
      </label>

      <div
        className={`flex h-[52px] w-full items-center rounded-xl border bg-white/5 px-4 transition ${
          error
            ? 'border-red-500/70 focus-within:ring-1 focus-within:ring-red-500/30'
            : 'border-slate-700/80 focus-within:border-cyan-400/60 focus-within:ring-1 focus-within:ring-cyan-400/20'
        }`}
      >
        {/* Left icon */}
        {icon && (
          <span className="mr-3 flex shrink-0 items-center text-slate-500">
            {icon}
          </span>
        )}

        <input
          id={name}
          name={name}
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          className="min-w-0 flex-1 bg-transparent text-sm text-slate-200 outline-none placeholder:text-slate-600"
        />

        {/* Right icon/button */}
        {rightElement && (
          <span className="ml-2 flex shrink-0 items-center">
            {rightElement}
          </span>
        )}
      </div>

      {error && (
        <p className="mt-2 text-xs text-red-400">
          {error}
        </p>
      )}
    </div>
  );
}

export default InputField;