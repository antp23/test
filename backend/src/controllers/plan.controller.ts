import { Response } from 'express';
import { prisma } from '../server';
import { AuthRequest } from '../middleware/auth';

export const getPlans = async (req: AuthRequest, res: Response) => {
  try {
    const plans = await prisma.plan.findMany({
      where: { isArchived: false },
      include: {
        phases: {
          orderBy: { order: 'asc' },
          include: {
            weeks: {
              orderBy: { weekNumber: 'asc' },
            },
          },
        },
      },
    });

    return res.json(plans);
  } catch (error) {
    console.error('Get plans error:', error);
    return res.status(500).json({ error: 'Failed to get plans' });
  }
};

export const getPlan = async (req: AuthRequest, res: Response) => {
  try {
    const { id } = req.params;

    const plan = await prisma.plan.findUnique({
      where: { id },
      include: {
        phases: {
          orderBy: { order: 'asc' },
          include: {
            weeks: {
              orderBy: { weekNumber: 'asc' },
              include: {
                dayTemplates: {
                  orderBy: { dayNumber: 'asc' },
                  include: {
                    routineTemplate: true,
                  },
                },
              },
            },
          },
        },
      },
    });

    if (!plan) {
      return res.status(404).json({ error: 'Plan not found' });
    }

    return res.json(plan);
  } catch (error) {
    console.error('Get plan error:', error);
    return res.status(500).json({ error: 'Failed to get plan' });
  }
};

export const assignPlan = async (req: AuthRequest, res: Response) => {
  try {
    const userId = req.userId!;
    const { planId } = req.body;

    if (!planId) {
      return res.status(400).json({ error: 'Plan ID is required' });
    }

    // Get plan with first phase and week
    const plan = await prisma.plan.findUnique({
      where: { id: planId },
      include: {
        phases: {
          orderBy: { order: 'asc' },
          take: 1,
          include: {
            weeks: {
              orderBy: { weekNumber: 'asc' },
              take: 1,
            },
          },
        },
      },
    });

    if (!plan) {
      return res.status(404).json({ error: 'Plan not found' });
    }

    if (plan.phases.length === 0 || plan.phases[0].weeks.length === 0) {
      return res.status(400).json({ error: 'Plan has no phases or weeks' });
    }

    const firstPhase = plan.phases[0];
    const firstWeek = firstPhase.weeks[0];

    // Deactivate any existing plan progress
    await prisma.userPlanProgress.updateMany({
      where: { userId },
      data: { isActive: false },
    });

    // Create new plan progress
    const progress = await prisma.userPlanProgress.create({
      data: {
        userId,
        planId,
        currentPhaseId: firstPhase.id,
        currentWeekId: firstWeek.id,
        startDate: new Date(),
        isActive: true,
      },
    });

    // Update user's active plan
    await prisma.user.update({
      where: { id: userId },
      data: { activePlanId: planId },
    });

    return res.json(progress);
  } catch (error) {
    console.error('Assign plan error:', error);
    return res.status(500).json({ error: 'Failed to assign plan' });
  }
};

export const getPhase = async (req: AuthRequest, res: Response) => {
  try {
    const { id } = req.params;
    const userId = req.userId!;

    const phase = await prisma.phase.findUnique({
      where: { id },
      include: {
        weeks: {
          orderBy: { weekNumber: 'asc' },
          include: {
            dayTemplates: {
              orderBy: { dayNumber: 'asc' },
            },
          },
        },
      },
    });

    if (!phase) {
      return res.status(404).json({ error: 'Phase not found' });
    }

    // Get logs for this phase to calculate progress
    const logs = await prisma.workoutLog.findMany({
      where: {
        userId,
        dayTemplate: {
          week: {
            phaseId: id,
          },
        },
      },
    });

    return res.json({
      phase,
      logs,
    });
  } catch (error) {
    console.error('Get phase error:', error);
    return res.status(500).json({ error: 'Failed to get phase' });
  }
};
