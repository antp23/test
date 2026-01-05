import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { dashboardApi } from '../api';
import { WorkoutStatus } from '../types';
import { format } from 'date-fns';

export default function DashboardPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.getDashboard,
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        Failed to load dashboard
      </div>
    );
  }

  if (!data?.hasActivePlan) {
    return (
      <div className="card text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Welcome to Workout Tracker!</h2>
        <p className="text-gray-600 mb-6">You don't have an active plan yet.</p>
        <Link to="/plan" className="btn btn-primary">
          View Available Plans
        </Link>
      </div>
    );
  }

  const getStatusColor = (status: WorkoutStatus) => {
    switch (status) {
      case WorkoutStatus.COMPLETED:
        return 'bg-success';
      case WorkoutStatus.PARTIAL:
        return 'bg-warning';
      case WorkoutStatus.SKIPPED:
        return 'bg-error';
      case WorkoutStatus.REST:
        return 'bg-gray-200';
      default:
        return 'bg-gray-100';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Track your progress and stay consistent</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Current Phase */}
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Current Phase</h3>
          <p className="text-2xl font-bold text-gray-900 mb-2">
            {data.currentPhase?.name}
          </p>
          <div className="mt-4">
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Progress</span>
              <span className="font-medium">{data.phaseProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary h-2 rounded-full transition-all"
                style={{ width: `${data.phaseProgress}%` }}
              />
            </div>
          </div>
        </div>

        {/* Current Week */}
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Current Week</h3>
          <p className="text-2xl font-bold text-gray-900 mb-2">
            Week {data.currentWeek?.weekNumber}
            {data.currentWeek?.isDeload && (
              <span className="text-sm font-normal text-warning ml-2">(Deload)</span>
            )}
          </p>
          <div className="mt-4">
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">This Week</span>
              <span className="font-medium">{data.weekProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-success h-2 rounded-full transition-all"
                style={{ width: `${data.weekProgress}%` }}
              />
            </div>
          </div>
        </div>

        {/* Streak */}
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Current Streak</h3>
          <p className="text-2xl font-bold text-gray-900 mb-2">{data.streak} days</p>
          <p className="text-sm text-gray-600 mt-4">
            {data.streak > 0
              ? 'Great job! Keep it up!'
              : 'Start your streak today!'}
          </p>
        </div>
      </div>

      {/* Next Workout */}
      {data.nextWorkout && (
        <div className="card bg-primary text-white">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-sm font-medium opacity-90 mb-2">Next Workout</h3>
              <p className="text-2xl font-bold mb-1">{data.nextWorkout.name}</p>
              {data.nextWorkout.isOptional && (
                <span className="text-sm opacity-75">(Optional)</span>
              )}
            </div>
            <Link
              to="/today"
              className="bg-white text-primary px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors"
            >
              Log Workout
            </Link>
          </div>
        </div>
      )}

      {/* Mini Calendar Heatmap */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Last 28 Days</h3>
        <div className="grid grid-cols-7 gap-2">
          {Array.from({ length: 28 }).map((_, index) => {
            const date = new Date();
            date.setDate(date.getDate() - (27 - index));
            const dateStr = format(date, 'yyyy-MM-dd');

            const log = data.recentLogs.find(
              (l) => format(new Date(l.scheduledDate), 'yyyy-MM-dd') === dateStr
            );

            return (
              <div key={index} className="text-center">
                <div
                  className={`w-full aspect-square rounded ${
                    log ? getStatusColor(log.status) : 'bg-gray-100'
                  }`}
                  title={`${dateStr}${log ? ` - ${log.status}` : ''}`}
                />
                <p className="text-xs text-gray-500 mt-1">{format(date, 'd')}</p>
              </div>
            );
          })}
        </div>
        <div className="mt-4 flex justify-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-success rounded" />
            <span>Completed</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-warning rounded" />
            <span>Partial</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-error rounded" />
            <span>Skipped</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-gray-100 rounded" />
            <span>None</span>
          </div>
        </div>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Link to="/calendar" className="card hover:shadow-md transition-shadow text-center">
          <svg
            className="w-8 h-8 mx-auto text-primary mb-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <p className="font-medium">Calendar</p>
        </Link>
        <Link to="/plan" className="card hover:shadow-md transition-shadow text-center">
          <svg
            className="w-8 h-8 mx-auto text-primary mb-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
          <p className="font-medium">View Plan</p>
        </Link>
        <Link to="/history" className="card hover:shadow-md transition-shadow text-center">
          <svg
            className="w-8 h-8 mx-auto text-primary mb-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="font-medium">History</p>
        </Link>
        <Link to="/settings" className="card hover:shadow-md transition-shadow text-center">
          <svg
            className="w-8 h-8 mx-auto text-primary mb-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
          <p className="font-medium">Settings</p>
        </Link>
      </div>
    </div>
  );
}
