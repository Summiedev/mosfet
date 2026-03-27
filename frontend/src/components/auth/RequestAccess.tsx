'use client';

import { useState } from 'react';
import { Check, Lock, Mail, User, Building2, Stethoscope, Users, Activity } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';

interface RoleOption {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

const roles: RoleOption[] = [
  {
    id: 'radiologist',
    name: 'Radiologist',
    description: 'Full access, scan guidance, reports, AI suggestions',
   icon: Stethoscope,
  },
  {
    id: 'rad-technician',
    name: 'Rad. Technician',
    description: 'Scan operation, voice input, basic report assistance',
    icon: Stethoscope,
  },
  {
    id: 'admin',
    name: 'Admin',
    description: 'Manage users, audit logs, data export',
    icon: Stethoscope,
  },
  {
    id: 'physician',
    name: 'Physician',
    description: 'View reports for assigned patients only',
    icon: Stethoscope,
  },
];

export default function RequestAccess() {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    role: '',
    hospitalId: '',
    department: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState(false);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.fullName.trim()) {
      newErrors.fullName = 'Full name is required';
    }
    if (!formData.email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Valid email is required';
    }
    if (!formData.role) {
      newErrors.role = 'Please select a role';
    }
    if (!formData.hospitalId.trim()) {
      newErrors.hospitalId = 'Hospital ID is required';
    }
    if (!formData.department.trim()) {
      newErrors.department = 'Department is required';
    }
    if (!formData.password || formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    if (!formData.agreeToTerms) {
      newErrors.agreeToTerms = 'You must agree to the terms';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      setSubmitted(true);
      console.log('Form submitted:', formData);
      // Handle form submission to your backend
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const selectedRole = roles.find((r) => r.id === formData.role);

  return (
    <div className="min-h-screen bg-[#020618] flex items-center justify-center p-3">      <div className="w-full max-w-2xl">
        <div className="bg-[#0F172B] border border-slate-800 rounded-2xl p-8 shadow-2xl">
          {/* Header */}
          <div>
            <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center">
              <Activity className="w-12 h-12 text-[#615FFF]" />
            </div>
            <h1 className="text-3xl font-bold text-white">RadFlow</h1>
          </div>
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-white mb-2">Request access</h2>
            <p className="text-slate-400">Create an account to continue</p>
          </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Full Name and Email */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-[#9CA3AF] mb-2">
                  Full Name <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <User className="absolute left-4 top-4 w-6 h-5 text-[#9CA3AF] z-10" />
                  <Input
                    type="text"
                    name="fullName"
                    placeholder="Dr Jzane"
                    value={formData.fullName}
                    onChange={handleInputChange}
                    className=" pt-7 pl-12 pb-6 bg-[#020618] border-[#314158] text-[#314158]   placeholder-slate-500  focus:border-[#314158] focus:ring-2 focus:ring-blue-500/20"
                  />
                </div>
                {errors.fullName && <p className="text-red-400 text-sm mt-1">{errors.fullName}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-[#9CA3AF] mb-2">
                  Email <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <Mail className="absolute left-4 top-4.5 w-6 h-5 text-[#9CA3AF] z-10" />
                  <Input
                    type="email"
                    name="email"
                    placeholder="doctor@hospital.com"
                    value={formData.email}
                    onChange={handleInputChange}
                    className=" pt-7 pl-12 pb-6 bg-[#020618] border-[#314158] rounded-lg  text-[#314158]  placeholder-slate-500 focus:border-[#314158]  focus:ring-1 focus:ring-blue-500/20"
                  />
                </div>
                {errors.email && <p className="text-red-400 text-sm mt-1">{errors.email}</p>}
              </div>
            </div>

            {/* Role Selection */}
            <div>
              <label className="block text-sm font-medium text-[#9CA3AF] mb-3">
                Role <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {roles.map((role) => {
                  const Icon = role.icon;
                  const isSelected = formData.role === role.id;
                  return (
                    <button
                      key={role.id}
                      type="button"
                      onClick={() =>
                        setFormData((prev) => ({
                          ...prev,
                          role: role.id,
                        }))
                      }
                      className={`p-4 rounded-lg border-2 text-left transition-all ${isSelected
                          ? 'border-[#2A3042] bg-[#1E2433]'
                          : 'border-slate-700 bg-[#1E2433] hover:border-slate-600'
                        }`}
                    >
                      <div className="flex items-start gap-3">
                        <Icon className="w-5 h-5 text-[#9CA3AF] mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="font-medium text-white">{role.name}</p>
                          <p className="text-xs text-[#6B7280] mt-1">{role.description}</p>
                        </div>
                        {isSelected && <Check className="w-5 h-5 text-blue-400 flex-shrink-0" />}
                      </div>
                    </button>
                  );
                })}
              </div>
              {errors.role && <p className="text-red-400 text-sm mt-1">{errors.role}</p>}
            </div>

            {/* Hospital ID and Department */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-[#9CA3AF] mb-2">
                  Hospital ID <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <Building2 className="absolute left-3 top-4.5 w-5 h-5 text-slate-500 z-10" />
                  <Input
                    type="text"
                    name="hospitalId"
                    placeholder="HSP-001"
                    value={formData.hospitalId}
                    onChange={handleInputChange}
                    className="pt-7 pl-12 pb-6  text-[#4B5563] border-[#2A3042] bg-[#1E2433] text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20"
                  />
                </div>
                {errors.hospitalId && <p className="text-red-400 text-sm mt-1">{errors.hospitalId}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-[#9CA3AF] mb-2">Department <span className="text-red-500">*</span></label>
                <Input
                  type="text"
                  name="department"
                  placeholder="Diagnostic Imaging"
                  value={formData.department}
                  onChange={handleInputChange}
                  className=" pt-7 pl-12 pb-6  text-[#4B5563] border-[#2A3042] text-white bg-[#1E2433] placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20"
                />
                {errors.department && <p className="text-red-400 text-sm mt-1">{errors.department}</p>}
              </div>
            </div>

            {/* Password Fields */}
            <div>
              <label className="block text-sm font-medium text-[#9CA3AF] mb-2">
                Password <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-500 z-10" />
                <Input
                  type="password"
                  name="password"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="pl-10 pb-6 pt-6 bg-[#020618] border-[#314158] text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20"
                />
              </div>
              {errors.password && <p className="text-red-400 text-sm mt-1">{errors.password}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-[#9CA3AF] mb-2">
                Confirm Password <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-500 z-10" />
                <Input
                  type="password"
                  name="confirmPassword"
                  placeholder="••••••••"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="pl-10 pb-6 pt-6 bg-[#020618] border-[#314158] text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20"
                />
              </div>
              {errors.confirmPassword && (
                <p className="text-red-400 text-sm mt-1">{errors.confirmPassword}</p>
              )}
            </div>

            {/* Terms Agreement */}
            <div className="flex items-start gap-3">
              <Checkbox
                id="agreeToTerms"
                checked={formData.agreeToTerms}
                onCheckedChange={(checked) =>
                  setFormData((prev) => ({ ...prev, agreeToTerms: checked === true }))
                }
                className="mt-1 border-slate-700 data-[state=checked]:bg-blue-500 data-[state=checked]:border-blue-500"
              />
              <label htmlFor="agreeToTerms" className="text-sm text-slate-400 cursor-pointer">
                I agree to the Terms of Service and Privacy Policy and will comply with data protection policies.
              </label>
            </div>
            {errors.agreeToTerms && <p className="text-red-400 text-sm">{errors.agreeToTerms}</p>}

            <Button
              type="submit"
              className="w-full bg-[#4F39F6]  hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-6 rounded-lg transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98]"
            >
              Request access
              <span className="ml-2">→</span>
            </Button>

            {/* Sign In Link */}
            <div className="text-center">
              <p className="text-slate-400 text-sm">
                Already have an account?{' '}
                <a href="/login" className="text-blue-400 hover:text-blue-300 font-medium">
                  Sign in
                </a>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}