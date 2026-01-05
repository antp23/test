import { Response } from 'express';
import { prisma } from '../server';
import { AuthRequest } from '../middleware/auth';

export const getDashboard = async (req: AuthRequest, res: Response) => {
  try {
    const userId = req.userId!;

    // Get user's active plan progress
    const progress = await prisma.userPlanProgress.findFirst({
      where: {
        userId,
        isActive: true,
      },
      include: {
        plan: true,
        currentPhase: {
          include: {
            weeks: {
              orderBy: { weekNumber: 'asc' },
            },
          },
        },
        currentWeek: {
          include: {
            dayTemplates: {
              orderBy: { dayNumber: 'asc' },
            },
          },
        },
      },
    });

    if (!progress) {
      return res.json({
        hasActivePlan: false,
        currentPhase: null,
        currentWeek: null,
        phaseProgress: 0,
        weekProgress: 0,
        streak: 0,
        nextWorkout: null,
        recentLogs: [],
      });
    }

    // Calculate phase progress
    const phaseWeeks = progress.currentPhase.weeks;
    const phaseDayTemplates = await prisma.dayTemplate.findMany({
      where: {
        week: {
          phaseId: progress.currentPhaseId,
        },
        type: { not: 'REST' },
        isOptional: false,
      },
    });

    const phaseLogs = await prisma.workoutLog.findMany({
      where: {
        userId,
        dayTemplateId: {
          in: phaseDayTemplates.map(dt => dt.id),
        },
        status: {
          in: ['COMPLETED', 'PARTIAL'],
        },
      },
    });

    const phaseProgress = phaseDayTemplates.length > 0
      ? Math.round((phaseLogs.length / phaseDayTemplates.length) * 100)
      : 0;

    // Calculate week progress
    const weekDayTemplates = progress.currentWeek.dayTemplates.filter(
      dt => dt.type !== 'REST' && !dt.isOptional
    );

    const weekLogs = await prisma.workoutLog.findMany({
      where: {
        userId,
        dayTemplateId: {
          in: weekDayTemplates.map(dt => dt.id),
        },
        status: {
          in: ['COMPLETED', 'PARTIAL'],
        },
      },
    });

    const weekProgress = weekDayTemplates.length > 0
      ? Math.round((weekLogs.length / weekDayTemplates.length) * 100)
      : 0;

    // Calculate streak
    const allLogs = await prisma.workoutLog.findMany({
      where: { userId },
      orderBy: { scheduledDate: 'desc' },
    });

    let streak = 0;
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (const log of allLogs) {
      const logDate = new Date(log.scheduledDate);
      logDate.setHours(0, 0, 0, 0);

      if (logDate > today) continue;

      if (log.status === 'COMPLETED' || log.status === 'PARTIAL') {
        streak++;
      } else if (log.status === 'SKIPPED') {
        break;
      }
      // REST and RESCHEDULED don't break streak
    }

    // Get next workout
    const loggedDayTemplateIds = new Set(weekLogs.map(log => log.dayTemplateId));
    const nextDayTemplate = progress.currentWeek.dayTemplates.find(
      dt => !loggedDayTemplateIds.has(dt.id)
    );

    // Get recent logs (last 28 days for mini calendar)
    const twentyEightDaysAgo = new Date();
    twentyEightDaysAgo.setDate(twentyEightDaysAgo.getDate() - 28);

    const recentLogs = await prisma.workoutLog.findMany({
      where: {
        userId,
        scheduledDate: {
          gte: twentyEightDaysAgo,
        },
      },
      orderBy: { scheduledDate: 'desc' },
      include: {
        dayTemplate: true,
      },
    });

    return res.json({
      hasActivePlan: true,
      currentPhase: {
        id: progress.currentPhase.id,
        name: progress.currentPhase.name,
        progress: phaseProgress,
      },
      currentWeek: {
        id: progress.currentWeek.id,
        weekNumber: progress.currentWeek.weekNumber,
        progress: weekProgress,
        isDeload: progress.currentWeek.isDeload,
      },
      phaseProgress,
      weekProgress,
      streak,
      nextWorkout: nextDayTemplate,
      recentLogs,
    });
  } catch (error) {
    console.error('Get dashboard error:', error);
    return res.status(500).json({ error: 'Failed to get dashboard data' });
  }
};
