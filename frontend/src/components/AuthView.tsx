import React, { useState } from 'react';
import {
  Shield,
  Lock,
  User,
  Mail,
  Phone,
  Eye,
  EyeOff,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Sparkles,
  Info,
  KeyRound,
  UserCheck
} from 'lucide-react';
import { api } from '../api/client';
import { Patient } from '../types';

interface AuthViewProps {
  onRegisterSuccess: (patient: Patient, token: string) => void;
  onLoginSuccess: (patient: Patient, token: string) => void;
  initialMode?: 'login' | 'register';
}

export const AuthView: React.FC<AuthViewProps> = ({
  onRegisterSuccess,
  onLoginSuccess,
  initialMode = 'register',
}) => {
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Common visibility state
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Register state
  const [name, setName] = useState('');
  const [regUsername, setRegUsername] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPhone, setRegPhone] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Login state
  const [loginIdentifier, setLoginIdentifier] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);

  // Validation rules for Register Password
  const hasMinLength = regPassword.length >= 8;
  const hasUpperCase = /[A-Z]/.test(regPassword);
  const hasNumber = /\d/.test(regPassword);
  const isPasswordValid = hasMinLength && hasUpperCase && hasNumber;
  const passwordsMatch = regPassword.length > 0 && regPassword === confirmPassword;
  const isUsernameValid = /^[a-zA-Z0-9_-]{3,20}$/.test(regUsername.trim());

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError('Please provide your full legal name.');
      return;
    }

    if (!isUsernameValid) {
      setError('Username must be 3-20 characters (letters, numbers, underscore, hyphen only).');
      return;
    }

    if (!isPasswordValid) {
      setError('Password does not meet complexity requirements (min 8 chars, 1 uppercase, 1 digit).');
      return;
    }

    if (!passwordsMatch) {
      setError('Passwords do not match. Please re-enter to confirm.');
      return;
    }

    setLoading(true);
    try {
      const res = await api.register({
        name: name.trim(),
        username: regUsername.trim(),
        email: regEmail.trim() || undefined,
        phone: regPhone.trim() ? (regPhone.startsWith('+91') ? regPhone.trim() : `+91 ${regPhone.trim()}`) : undefined,
        password: regPassword,
      });

      onRegisterSuccess(res.patient, res.access_token);
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please check your details.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!loginIdentifier.trim()) {
      setError('Please enter your username or registered email.');
      return;
    }

    if (!loginPassword) {
      setError('Please enter your password.');
      return;
    }

    setLoading(true);
    try {
      const res = await api.login({
        username_or_email: loginIdentifier.trim(),
        password: loginPassword,
        remember_me: rememberMe,
      });

      onLoginSuccess(res.patient, res.access_token);
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto animate-fade-in-up">
      {/* Clinical Disclaimer Banner */}
      <div className="mb-6 p-3.5 bg-gradient-to-r from-sky-50 to-blue-50 border border-sky-200/80 rounded-xl flex items-start gap-3 shadow-xs">
        <Shield className="w-5 h-5 text-clinical-600 flex-shrink-0 mt-0.5" />
        <div className="text-xs text-sky-950 leading-relaxed">
          <strong className="font-semibold text-clinical-900 block mb-0.5">
            Clinical Information Intelligence Platform
          </strong>
          Authentication safeguards sensitive clinical records under ABDM and DPDP Act guidelines. Non-diagnostic AI assistant with complete audit trail provenance.
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-xl shadow-slate-200/50 overflow-hidden">
        {/* Dual Mode Switcher Tabs */}
        <div className="grid grid-cols-2 bg-slate-100/80 p-1.5 border-b border-slate-200">
          <button
            type="button"
            id="auth-tab-register"
            onClick={() => {
              setMode('register');
              setError(null);
            }}
            className={`py-2.5 rounded-xl text-xs sm:text-sm font-bold flex items-center justify-center gap-2 transition-all ${
              mode === 'register'
                ? 'bg-white text-clinical-700 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>Create Account (New User)</span>
          </button>
          <button
            type="button"
            id="auth-tab-login"
            onClick={() => {
              setMode('login');
              setError(null);
            }}
            className={`py-2.5 rounded-xl text-xs sm:text-sm font-bold flex items-center justify-center gap-2 transition-all ${
              mode === 'login'
                ? 'bg-white text-clinical-700 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <KeyRound className="w-4 h-4" />
            <span>Sign In (Existing User)</span>
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="m-5 mb-0 p-3 bg-rose-50 border border-rose-200 rounded-xl flex items-start gap-2.5 text-xs text-rose-800 animate-shake">
            <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold">Authentication Error: </span>
              {error}
            </div>
          </div>
        )}

        {/* Mode 1: Register Form */}
        {mode === 'register' ? (
          <form onSubmit={handleRegister} className="p-6 sm:p-8 space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Full Legal Name <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <User className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
                <input
                  id="reg-fullname"
                  type="text"
                  required
                  placeholder="e.g. Dr. Rajesh Sharma"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-clinical-500 transition-colors"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Username <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-2 text-xs font-mono text-slate-400">@</span>
                  <input
                    id="reg-username"
                    type="text"
                    required
                    placeholder="rajesh_sharma"
                    value={regUsername}
                    onChange={(e) => setRegUsername(e.target.value.toLowerCase())}
                    className={`w-full pl-8 pr-3 py-2 bg-slate-50 border rounded-lg text-sm text-slate-800 focus:bg-white focus:outline-none focus:ring-2 transition-colors ${
                      regUsername.length > 0 && !isUsernameValid
                        ? 'border-rose-300 focus:ring-rose-400'
                        : 'border-slate-200 focus:ring-clinical-500'
                    }`}
                  />
                </div>
                <p className="text-[10px] text-slate-500 mt-1">3-20 chars (letters, numbers, _ -)</p>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
                  <input
                    id="reg-email"
                    type="email"
                    placeholder="rajesh@medlens.org"
                    value={regEmail}
                    onChange={(e) => setRegEmail(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-clinical-500 transition-colors"
                  />
                </div>
                <p className="text-[10px] text-slate-500 mt-1">For account recovery & alerts</p>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Mobile Number (+91)
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
                <input
                  id="reg-phone"
                  type="tel"
                  placeholder="9876543210"
                  value={regPhone}
                  onChange={(e) => setRegPhone(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-clinical-500 transition-colors"
                />
              </div>
            </div>

            {/* Password Fields */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Password <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
                  <input
                    id="reg-password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    placeholder="••••••••"
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    className="w-full pl-9 pr-10 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-clinical-500 transition-colors"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600 focus:outline-none"
                    title={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Confirm Password <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
                  <input
                    id="reg-confirm-password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    required
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className={`w-full pl-9 pr-10 py-2 bg-slate-50 border rounded-lg text-sm text-slate-800 focus:bg-white focus:outline-none focus:ring-2 transition-colors ${
                      confirmPassword.length > 0
                        ? passwordsMatch
                          ? 'border-emerald-300 focus:ring-emerald-400'
                          : 'border-rose-300 focus:ring-rose-400'
                        : 'border-slate-200 focus:ring-clinical-500'
                    }`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600 focus:outline-none"
                    title={showConfirmPassword ? 'Hide password' : 'Show password'}
                  >
                    {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>

            {/* Password Requirement Badges */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs space-y-1.5">
              <div className="text-[11px] font-semibold text-slate-600 mb-1">Password Strength Checklist:</div>
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div className={`flex items-center gap-1.5 ${hasMinLength ? 'text-emerald-700 font-medium' : 'text-slate-500'}`}>
                  <CheckCircle2 className={`w-3.5 h-3.5 ${hasMinLength ? 'text-emerald-600' : 'text-slate-300'}`} />
                  <span>Min 8 characters</span>
                </div>
                <div className={`flex items-center gap-1.5 ${hasUpperCase ? 'text-emerald-700 font-medium' : 'text-slate-500'}`}>
                  <CheckCircle2 className={`w-3.5 h-3.5 ${hasUpperCase ? 'text-emerald-600' : 'text-slate-300'}`} />
                  <span>1+ Uppercase (A-Z)</span>
                </div>
                <div className={`flex items-center gap-1.5 ${hasNumber ? 'text-emerald-700 font-medium' : 'text-slate-500'}`}>
                  <CheckCircle2 className={`w-3.5 h-3.5 ${hasNumber ? 'text-emerald-600' : 'text-slate-300'}`} />
                  <span>1+ Number (0-9)</span>
                </div>
                <div className={`flex items-center gap-1.5 ${passwordsMatch ? 'text-emerald-700 font-medium' : 'text-slate-500'}`}>
                  <CheckCircle2 className={`w-3.5 h-3.5 ${passwordsMatch ? 'text-emerald-600' : 'text-slate-300'}`} />
                  <span>Passwords match</span>
                </div>
              </div>
            </div>

            {/* Action Button */}
            <button
              id="auth-register-submit-btn"
              type="submit"
              disabled={loading || !isPasswordValid || !passwordsMatch || !isUsernameValid || !name.trim()}
              className="w-full mt-2 py-3 bg-gradient-to-r from-clinical-600 to-clinical-700 hover:from-clinical-700 hover:to-clinical-800 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-bold rounded-xl shadow-md shadow-clinical-500/20 flex items-center justify-center gap-2 transition-all hover-lift"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Creating Secure Account...</span>
                </>
              ) : (
                <>
                  <span>Create Account & Continue to Demographics</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        ) : (
          /* Mode 2: Sign In Form */
          <form onSubmit={handleLogin} className="p-6 sm:p-8 space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Username or Registered Email <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <User className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
                <input
                  id="login-username"
                  type="text"
                  required
                  placeholder="username or user@medlens.org"
                  value={loginIdentifier}
                  onChange={(e) => setLoginIdentifier(e.target.value)}
                  className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-clinical-500 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Password <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
                <input
                  id="login-password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  placeholder="••••••••"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  className="w-full pl-9 pr-10 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-clinical-500 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600 focus:outline-none"
                  title={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs pt-1">
              <label className="flex items-center gap-2 text-slate-600 cursor-pointer">
                <input
                  id="login-remember-me"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded text-clinical-600 border-slate-300 focus:ring-clinical-500"
                />
                <span>Remember me (30-day session)</span>
              </label>

              <button
                type="button"
                onClick={() => alert('Password reset is managed via administrative support or ABHA linked identity.')}
                className="text-clinical-600 hover:underline font-medium"
              >
                Forgot Password?
              </button>
            </div>

            {/* Action Button */}
            <button
              id="auth-login-submit-btn"
              type="submit"
              disabled={loading || !loginIdentifier.trim() || !loginPassword}
              className="w-full mt-3 py-3 bg-gradient-to-r from-clinical-600 to-clinical-700 hover:from-clinical-700 hover:to-clinical-800 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-bold rounded-xl shadow-md shadow-clinical-500/20 flex items-center justify-center gap-2 transition-all hover-lift"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Signing In...</span>
                </>
              ) : (
                <>
                  <span>Sign In to Clinical Record</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        )}
      </div>

      {/* Demo Patients Note */}
      <div className="mt-4 p-3 text-center text-xs text-slate-500">
        <span>Looking for demo sandbox patients? </span>
        <span className="font-semibold text-slate-700">Eleanor Vance</span>,{' '}
        <span className="font-semibold text-slate-700">Arthur Pendelton</span>, and{' '}
        <span className="font-semibold text-slate-700">Maya Rodriguez</span> remain 1-click accessible anytime from the top patient switcher.
      </div>
    </div>
  );
};
