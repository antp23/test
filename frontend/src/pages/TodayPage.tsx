import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tantml:invoke name="@tanstack/react-query">
<parameter name="logsApi">
import { WorkoutStatus, CreateLogInput } from '../types';
import { format } from 'date-fns';

export default function TodayPage() {
  const queryClient = useQueryClient();
  const [showMetrics, setShowMetrics] = useState(false);
  const [formData, setFormData] = useState<Partial<CreateLogInput>>({
    status: WorkoutStatus.COMPLETED,
    bodyWeight: undefined,
    energy: undefined,
    sleepHours: undefined,
    sessionRpe: undefined,
    notes: '',
  });

  const { data, isLoading } = useQuery({
    queryKey: ['todayWorkout'],
    queryFn: logsApi.getTodayWorkout,
  });

  const createLogMutation = useMutation({
    mutationFn: logsApi.createLog,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todayWorkout'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      // Reset form
      setFormData({
        status: WorkoutStatus.COMPLETED,
        bodyWeight: undefined,
        energy: undefined,
        sleepHours: undefined,
        sessionRpe: undefined,
        notes: '',
      });
      setShowMetrics(false);
    },
  });

  const updateLogMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => logsApi.updateLog(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todayWorkout'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const handleQuickLog = (status: WorkoutStatus) => {
    if (!data?.dayTemplate) return;

    const logData: CreateLogInput = {
      dayTemplateId: data.dayTemplate.id,
      scheduledDate: data.scheduledDate,
      status,
    };

    createLogMutation.mutate(logData);
  };

  const handleFullLog = () => {
    if (!data?.dayTemplate) return;

    const logData: CreateLogInput = {
      dayTemplateId: data.dayTemplate.id,
      scheduledDate: data.scheduledDate,
      status: formData.status || WorkoutStatus.COMPLETED,
      bodyWeight: formData.bodyWeight,
      energy: formData.energy,
      sleepHours: formData.sleepHours,
      sessionRpe: formData.sessionRpe,
      notes: formData.notes,
    };

    createLogMutation.mutate(logData);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (data?.log) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="card text-center py-12">
          <svg
            className="w-16 h-16 mx-auto text-success mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Workout Logged!</h2>
          <p className="text-gray-600 mb-6">
            You've already logged today's workout as <strong>{data.log.status}</strong>
          </p>
          <div className="bg-gray-50 rounded-lg p-4 text-left max-w-md mx-auto">
            <h3 className="font-semibold mb-2">{data.dayTemplate.name}</h3>
            {data.log.bodyWeight && (
              <p className="text-sm text-gray-600">Weight: {data.log.bodyWeight} lbs</p>
            )}
            {data.log.energy && (
              <p className="text-sm text-gray-600">Energy: {data.log.energy}/10</p>
            )}
            {data.log.sleepHours && (
              <p className="text-sm text-gray-600">Sleep: {data.log.sleepHours} hours</p>
            )}
            {data.log.sessionRpe && (
              <p className="text-sm text-gray-600">RPE: {data.log.sessionRpe}/10</p>
            )}
            {data.log.notes && (
              <p className="text-sm text-gray-600 mt-2">Notes: {data.log.notes}</p>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (!data?.dayTemplate) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="card text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Workout Scheduled</h2>
          <p className="text-gray-600">
            You don't have a workout scheduled for today or all workouts are complete.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-sm text-gray-500">
              {format(new Date(data.scheduledDate), 'EEEE, MMMM d, yyyy')}
            </p>
            <h1 className="text-2xl font-bold text-gray-900 mt-1">
              {data.dayTemplate.name}
            </h1>
            {data.dayTemplate.isOptional && (
              <span className="inline-block mt-2 px-2 py-1 bg-gray-100 text-gray-600 text-sm rounded">
                Optional
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Quick Log Buttons */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-4">Quick Log</h3>
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => handleQuickLog(WorkoutStatus.COMPLETED)}
            disabled={createLogMutation.isPending}
            className="btn bg-success text-white hover:bg-green-600 disabled:opacity-50"
          >
            Completed
          </button>
          <button
            onClick={() => handleQuickLog(WorkoutStatus.PARTIAL)}
            disabled={createLogMutation.isPending}
            className="btn bg-warning text-white hover:bg-yellow-500 disabled:opacity-50"
          >
            Partial
          </button>
          <button
            onClick={() => handleQuickLog(WorkoutStatus.SKIPPED)}
            disabled={createLogMutation.isPending}
            className="btn bg-error text-white hover:bg-red-500 disabled:opacity-50"
          >
            Skipped
          </button>
          <button
            onClick={() => setShowMetrics(!showMetrics)}
            className="btn btn-secondary"
          >
            {showMetrics ? 'Hide Details' : 'Add Details'}
          </button>
        </div>
      </div>

      {/* Detailed Metrics */}
      {showMetrics && (
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4">Log with Details</h3>

          <div className="space-y-4">
            {/* Status */}
            <div>
              <label className="label">Status</label>
              <select
                value={formData.status}
                onChange={(e) =>
                  setFormData({ ...formData, status: e.target.value as WorkoutStatus })
                }
                className="input"
              >
                <option value={WorkoutStatus.COMPLETED}>Completed</option>
                <option value={WorkoutStatus.PARTIAL}>Partial</option>
                <option value={WorkoutStatus.SKIPPED}>Skipped</option>
              </select>
            </div>

            {/* Body Weight */}
            <div>
              <label className="label">Body Weight (lbs)</label>
              <input
                type="number"
                step="0.1"
                value={formData.bodyWeight || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    bodyWeight: e.target.value ? parseFloat(e.target.value) : undefined,
                  })
                }
                className="input"
                placeholder="150.0"
              />
            </div>

            {/* Energy */}
            <div>
              <label className="label">Energy Level (1-10)</label>
              <input
                type="range"
                min="1"
                max="10"
                value={formData.energy || 5}
                onChange={(e) =>
                  setFormData({ ...formData, energy: parseInt(e.target.value) })
                }
                className="w-full"
              />
              <div className="flex justify-between text-sm text-gray-600 mt-1">
                <span>1</span>
                <span className="font-medium">{formData.energy || 5}</span>
                <span>10</span>
              </div>
            </div>

            {/* Sleep Hours */}
            <div>
              <label className="label">Sleep (hours)</label>
              <input
                type="number"
                step="0.5"
                value={formData.sleepHours || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    sleepHours: e.target.value ? parseFloat(e.target.value) : undefined,
                  })
                }
                className="input"
                placeholder="7.5"
              />
            </div>

            {/* Session RPE */}
            <div>
              <label className="label">Session RPE (1-10)</label>
              <input
                type="range"
                min="1"
                max="10"
                value={formData.sessionRpe || 5}
                onChange={(e) =>
                  setFormData({ ...formData, sessionRpe: parseInt(e.target.value) })
                }
                className="w-full"
              />
              <div className="flex justify-between text-sm text-gray-600 mt-1">
                <span>1</span>
                <span className="font-medium">{formData.sessionRpe || 5}</span>
                <span>10</span>
              </div>
            </div>

            {/* Notes */}
            <div>
              <label className="label">Notes</label>
              <textarea
                value={formData.notes || ''}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="input"
                rows={3}
                maxLength={500}
                placeholder="Any observations or notes about this workout..."
              />
              <p className="text-xs text-gray-500 mt-1">
                {(formData.notes || '').length}/500 characters
              </p>
            </div>

            {/* Submit */}
            <button
              onClick={handleFullLog}
              disabled={createLogMutation.isPending}
              className="w-full btn btn-primary disabled:opacity-50"
            >
              {createLogMutation.isPending ? 'Logging...' : 'Log Workout'}
            </button>
          </div>
        </div>
      )}

      {/* Error Display */}
      {createLogMutation.isError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          Failed to log workout. Please try again.
        </div>
      )}
    </div>
  );
}
