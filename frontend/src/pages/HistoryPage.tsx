import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { logsApi } from '../api';
import { WorkoutStatus } from '../types';
import { format } from 'date-fns';

export default function HistoryPage() {
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    status: '',
  });

  const { data, isLoading } = useQuery({
    queryKey: ['logs', filters],
    queryFn: () =>
      logsApi.getLogs({
        startDate: filters.startDate || undefined,
        endDate: filters.endDate || undefined,
        status: filters.status || undefined,
      }),
  });

  const handleExport = async () => {
    try {
      const blob = await logsApi.exportLogs({
        startDate: filters.startDate || undefined,
        endDate: filters.endDate || undefined,
      });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `workout_logs_${format(new Date(), 'yyyy-MM-dd')}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const getStatusBadge = (status: WorkoutStatus) => {
    const colors = {
      COMPLETED: 'bg-success text-white',
      PARTIAL: 'bg-warning text-white',
      SKIPPED: 'bg-error text-white',
      RESCHEDULED: 'bg-gray-400 text-white',
      SCHEDULED: 'bg-gray-200 text-gray-700',
      REST: 'bg-gray-200 text-gray-700',
    };

    return (
      <span className={`px-2 py-1 text-xs rounded ${colors[status]}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Workout History</h1>
        <button onClick={handleExport} className="btn btn-primary">
          Export CSV
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="label">Start Date</label>
            <input
              type="date"
              value={filters.startDate}
              onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
              className="input"
            />
          </div>
          <div>
            <label className="label">End Date</label>
            <input
              type="date"
              value={filters.endDate}
              onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
              className="input"
            />
          </div>
          <div>
            <label className="label">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="input"
            >
              <option value="">All</option>
              <option value="COMPLETED">Completed</option>
              <option value="PARTIAL">Partial</option>
              <option value="SKIPPED">Skipped</option>
              <option value="RESCHEDULED">Rescheduled</option>
            </select>
          </div>
        </div>
        {(filters.startDate || filters.endDate || filters.status) && (
          <button
            onClick={() => setFilters({ startDate: '', endDate: '', status: '' })}
            className="mt-4 text-sm text-primary hover:underline"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Logs List */}
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      ) : data?.logs.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-600">No workout logs found.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {data?.logs.map((log) => (
            <div key={log.id} className="card">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-gray-900">
                      {log.dayTemplate?.name || 'Workout'}
                    </h3>
                    {getStatusBadge(log.status)}
                  </div>
                  <p className="text-sm text-gray-600">
                    {format(new Date(log.scheduledDate), 'EEEE, MMMM d, yyyy')}
                  </p>

                  {/* Metrics */}
                  {(log.bodyWeight || log.energy || log.sleepHours || log.sessionRpe) && (
                    <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                      {log.bodyWeight && (
                        <div>
                          <span className="text-gray-500">Weight:</span>{' '}
                          <span className="font-medium">{log.bodyWeight} lbs</span>
                        </div>
                      )}
                      {log.energy && (
                        <div>
                          <span className="text-gray-500">Energy:</span>{' '}
                          <span className="font-medium">{log.energy}/10</span>
                        </div>
                      )}
                      {log.sleepHours && (
                        <div>
                          <span className="text-gray-500">Sleep:</span>{' '}
                          <span className="font-medium">{log.sleepHours}h</span>
                        </div>
                      )}
                      {log.sessionRpe && (
                        <div>
                          <span className="text-gray-500">RPE:</span>{' '}
                          <span className="font-medium">{log.sessionRpe}/10</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Notes */}
                  {log.notes && (
                    <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                      <p className="text-gray-700">{log.notes}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination info */}
      {data && data.total > 0 && (
        <div className="text-center text-sm text-gray-600">
          Showing {data.logs.length} of {data.total} workouts
        </div>
      )}
    </div>
  );
}
