import { useAuthStore } from '../store/authStore';
import { authApi } from '../api';

export default function SettingsPage() {
  const { user, logout } = useAuthStore();

  const handleLogout = async () => {
    try {
      await authApi.logout();
      logout();
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">Manage your account and preferences</p>
      </div>

      {/* Profile */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Profile</h2>
        <div className="space-y-3">
          <div>
            <label className="text-sm font-medium text-gray-500">Name</label>
            <p className="text-gray-900">{user?.name}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Email</label>
            <p className="text-gray-900">{user?.email}</p>
          </div>
        </div>
      </div>

      {/* Data Management */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Data Management</h2>
        <p className="text-gray-600 mb-4">
          Export your workout data to CSV format for backup or analysis.
        </p>
        <a
          href="/history"
          className="btn btn-primary inline-block"
        >
          Go to History to Export
        </a>
      </div>

      {/* Account Actions */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Account</h2>
        <button
          onClick={handleLogout}
          className="btn bg-red-600 text-white hover:bg-red-700"
        >
          Sign Out
        </button>
      </div>

      {/* App Info */}
      <div className="card bg-gray-50">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">About</h2>
        <div className="space-y-2 text-sm text-gray-600">
          <p>
            <strong>Workout Tracker</strong> - Version 1.0.0
          </p>
          <p>
            A simple and effective way to track your workout progress and stay consistent
            with your fitness goals.
          </p>
        </div>
      </div>
    </div>
  );
}
