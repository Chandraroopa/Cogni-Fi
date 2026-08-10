import React from 'react';

/**
 * PLACEHOLDER — Member 2 (Ashwini shenoy) builds the real version.
 * Expected structure (from task breakdown):
 *
 * function Login() {
 *   const { login } = useAuth();
 *   const [form, setForm] = useState({ email: '', password: '' });
 *
 *   const handleSubmit = async (e) => {
 *     e.preventDefault();
 *     await login(form.email, form.password); // calls services/api.js
 *     navigate('/dashboard');
 *   };
 *
 *   return (
 *     <form onSubmit={handleSubmit}>
 *       <input type="email" ... />
 *       <input type="password" ... />
 *       <button type="submit">Login</button>
 *     </form>
 *   );
 * }
 */
function Login() {
  return (
    <div className="container py-5 text-center text-muted">
      <h3>Login Page — coming soon</h3>
      <p>(Placeholder — Member 2 to implement)</p>
    </div>
  );
}

export default Login;
