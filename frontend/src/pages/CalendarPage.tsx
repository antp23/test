import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { logsApi } from '../api';
import { WorkoutStatus } from '../types';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday } from 'date-fns';

export default function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date());

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);

  const { data, isLoading } = useQuery({
    queryKey: ['logs', format(monthStart, 'yyyy-MM-dd'), format(monthEnd, 'yyyy-MM-dd')],
    queryFn: () =>
      logsApi.getLogs({
        startDate: format(monthStart, 'yyyy-MM-dd'),
        endDate: format(monthEnd, 'yyyy-MM-dd'),
      }),
  });

  const days = eachDayOfInterval({ start: monthStart, end: monthEnd });

  const getStatusColor = (status: WorkoutStatus) => {
    switch (status) {
      case WorkoutStatus.COMPLETED:
        return 'bg-success text-white';
      case WorkoutStatus.PARTIAL:
        return 'bg-warning text-white';
      case WorkoutStatus.SKIPPED:
        return 'bg-error text-white';
      case WorkoutStatus.REST:
        return 'bg-gray-200 text-gray-600';
      default:
        return 'bg-gray-100 text-gray-400';
    }
  };

  const getLogForDate = (date: Date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    return data?.logs.find(
      (log) => format(new Date(log.scheduledDate), 'yyyy-MM-dd') === dateStr
    );
  };

  const previousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Calendar</h1>
      </div>

      {/* Calendar */}
      <div className="card">
        <div className="flex justify-between items-center mb-6">
          <button onClick={previousMonth} className="btn btn-secondary">
            ← Previous
          </button>
          <h2 className="text-xl font-bold text-gray-900">
            {format(currentDate, 'MMMM yyyy')}
          </h2>
          <button onClick={nextMonth} className="btn btn-secondary">
            Next →
          </button>
        </div>

        {/* Day Headers */}
        <div className="grid grid-cols-7 gap-2 mb-2">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
            <div key={day} className="text-center font-medium text-gray-600 text-sm">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-2">
          {/* Empty cells for days before month starts */}
          {Array.from({ length: monthStart.getDay() }).map((_, index) => (
            <div key={`empty-${index}`} className="aspect-square" />
          ))}

          {/* Month days */}
          {days.map((day) => {
            const log = getLogForDate(day);
            const isCurrentDay = isToday(day);

            return (
              <div
                key={day.toString()}
                className={`aspect-square rounded-lg p-2 ${
                  log ? getStatusColor(log.status) : 'bg-gray-50'
                } ${isCurrentDay ? 'ring-2 ring-primary' : ''}`}
              >
                <div className="text-sm font-medium">{format(day, 'd')}</div>
                {log && (
                  <div className="text-xs mt-1 truncate" title={log.dayTemplate?.name}>
                    {log.dayTemplate?.name}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div className="mt-6 flex flex-wrap justify-center gap-4 text-sm">
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
            <div className="w-4 h-4 bg-gray-50 rounded border border-gray-200" />
            <span>No workout</span>
          </div>
        </div>
      </div>
    </div>
  );
}
