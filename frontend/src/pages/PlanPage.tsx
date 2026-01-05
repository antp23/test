import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '../store/authStore';
import { plansApi } from '../api';

export default function PlanPage() {
  const { user } = useAuthStore();

  const { data: plan, isLoading } = useQuery({
    queryKey: ['plan', user?.activePlanId],
    queryFn: () => plansApi.getPlan(user!.activePlanId!),
    enabled: !!user?.activePlanId,
  });

  if (!user?.activePlanId) {
    return (
      <div className="card text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">No Active Plan</h2>
        <p className="text-gray-600">You don't have an active workout plan.</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!plan) {
    return (
      <div className="card text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Plan Not Found</h2>
        <p className="text-gray-600">Unable to load your workout plan.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">{plan.name}</h1>
        {plan.description && (
          <p className="text-gray-600 mt-2">{plan.description}</p>
        )}
      </div>

      {/* Phases */}
      <div className="space-y-6">
        {plan.phases?.map((phase) => (
          <div key={phase.id} className="card">
            <div className="mb-4">
              <h2 className="text-xl font-bold text-gray-900">{phase.name}</h2>
              {phase.description && (
                <p className="text-gray-600 text-sm mt-1">{phase.description}</p>
              )}
            </div>

            {/* Weeks */}
            <div className="space-y-4">
              {phase.weeks?.map((week) => (
                <div key={week.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="font-semibold text-gray-900">
                      Week {week.weekNumber}
                      {week.isDeload && (
                        <span className="ml-2 text-sm font-normal text-warning">
                          (Deload)
                        </span>
                      )}
                    </h3>
                  </div>

                  {/* Day Templates */}
                  <div className="space-y-2">
                    {week.dayTemplates?.map((dayTemplate) => (
                      <div
                        key={dayTemplate.id}
                        className="flex justify-between items-center p-3 bg-gray-50 rounded"
                      >
                        <div>
                          <p className="font-medium text-gray-900">
                            Day {dayTemplate.dayNumber}: {dayTemplate.name}
                          </p>
                          {dayTemplate.isOptional && (
                            <span className="text-xs text-gray-500">(Optional)</span>
                          )}
                        </div>
                        <span
                          className={`px-2 py-1 text-xs rounded ${
                            dayTemplate.type === 'REST'
                              ? 'bg-gray-200 text-gray-700'
                              : 'bg-primary text-white'
                          }`}
                        >
                          {dayTemplate.type.replace('_', ' ')}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
