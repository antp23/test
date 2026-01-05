import { Response } from 'express';
import { prisma } from '../server';
import { AuthRequest } from '../middleware/auth';
import { WorkoutStatus } from '@prisma/client';
import { z } from 'zod';

// Validation schema
const createLogSchema = z.object({
  dayTemplateId: z.string().uuid(),
  scheduledDate: z.string().datetime(),
  actualDate: z.string().datetime().optional(),
  status: z.enum(['COMPLETED', 'PARTIAL', 'SKIPPED', 'RESCHEDULED', 'SCHEDULED', 'REST']),
  bodyWeight: z.number().min(0).max(999.9).optional(),
  energy: z.number().int().min(1).max(10).optional(),
  sleepHours: z.number().min(0).max(24).optional(),
  sessionRpe: z.number().int().min(1).max(10).optional(),
  notes: z.string().max(500).optional(),
});

const updateLogSchema = createLogSchema.partial();

export const getLogs = async (req: AuthRequest, res: Response) => {
  try {
    const userId = req.userId!;
    const {
      startDate,
      endDate,
      phaseId,
      status,
      search,
      page = '1',
      limit = '20'
    } = req.query;

    const where: any = { userId };

    if (startDate && endDate) {
      where.scheduledDate = {
        gte: new Date(startDate as string),
        lte: new Date(endDate as string),
      };
    }

    if (status) {
      where.status = status;
    }

    if (search) {
      where.notes = {
        contains: search as string,
        mode: 'insensitive',
      };
    }

    const skip = (parseInt(page as string) - 1) * parseInt(limit as string);
    const take = parseInt(limit as string);

    const [logs, total] = await Promise.all([
      prisma.workoutLog.findMany({
        where,
        include: {
          dayTemplate: {
            include: {
              week: {
                include: {
                  phase: {
                    select: {
                      name: true,
                    },
                  },
                },
              },
            },
          },
        },
        orderBy: { scheduledDate: 'desc' },
        skip,
        take,
      }),
      prisma.workoutLog.count({ where }),
    ]);

    return res.json({
      logs,
      total,
      page: parseInt(page as string),
      totalPages: Math.ceil(total / take),
    });
  } catch (error) {
    console.error('Get logs error:', error);
    return res.status(500).json({ error: 'Failed to get logs' });
  }
};

export const getLog = async (req: AuthRequest, res: Response) => {
  try {
    const userId = req.userId!;
    const { id } = req.params;

    const log = await prisma.workoutLog.findFirst({
      where: {
        id,
        userId,
      },
      include: {
        dayTemplate: {
          include: {
            week: {
              include: {
                phase: true,
              },
            },
          },
        },
      },
    });

    if (!log) {
      return res.status(404).json({ error: 'Log not found' });
    }

    return res.json(log);
  } catch (error) {
    console.error('Get log error:', error);
    return res.status(500).json({ error: 'Failed to get log' });
  }
};

export const createLog = async (req: AuthRequest, res: Response) => {
  try {
    const userId = req.userId!;
    const validated = createLogSchema.parse(req.body);

    const log = await prisma.workoutLog.create({
      data: {
        userId,
        dayTemplateId: validated.dayTemplateId,
        scheduledDate: new Date(validated.scheduledDate),
        actualDate: validated.actualDate ? new Date(validated.actualDate) : null,
        status: validated.status as WorkoutStatus,
        bodyWeight: validated.bodyWeight,
        energy: validated.energy,
        sleepHours: validated.sleepHours,
        sessionRpe: validated.sessionRpe,
        notes: validated.notes,
        loggedAt: new Date(),
      },
      include: {
        dayTemplate: true,
      },
    });

    return res.status(201).json(log);
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({ error: 'Validation failed', details: error.errors });
    }
    console.error('Create log error:', error);
    return res.status(500).json({ error: 'Failed to create log' });
  }
};

export const updateLog = async (req: AuthRequest, res: Response) => {
  try {
    const userId = req.userId!;
    const { id } = req.params;
    const validated = updateLogSchema.parse(req.body);

    // Check if log exists and belongs to user
    const existingLog = await prisma.workoutLog.findFirst({
      where: { id, userId },
    });

    if (!existingLog) {
      return res.status(404).json({ error: 'Log not found' });
    }

    // Check if within 7-day edit window
    const daysSinceLog = Math.floor(
      (Date.now() - existingLog.createdAt.getTime()) / (1000 * 60 * 60 * 24)
    );

    if (daysSinceLog > 7) {
      return res.status(403).json({ error: 'Cannot edit logs older than 7 days' });
    }

    const updateData: any = {};
    if (validated.status) updateData.status = validated.status;
    if (validated.bodyWeight !== undefined) updateData.bodyWeight = validated.bodyWeight;
    if (validated.energy !== undefined) updateData.energy = validated.energy;
    if (validated.sleepHours !== undefined) updateData.sleepHours = validated.sleepHours;
    if (validated.sessionRpe !== undefined) updateData.sessionRpe = validated.sessionRpe;
    if (validated.notes !== undefined) updateData.notes = validated.notes;
    if (validated.actualDate) updateData.actualDate = new Date(validated.actualDate);

    const log = await prisma.workoutLog.update({
      where: { id },
      data: updateData,
      include: {
        dayTemplate: true,
      },
    });

    return res.json(log);
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({ error: 'Validation failed', details: error.errors });
    }
    console.error('Update log error:', error);
    return res.status(500).json({ error: 'Failed to update log' });
  }
};

export const exportLogs = async (req: AuthRequest, res: Response) => {
  try {
    const userId = req.userId!;
    const { startDate, endDate } = req.query;

    const where: any = { userId };

    if (startDate && endDate) {
      where.scheduledDate = {
        gte: new Date(startDate as string),
        lte: new Date(endDate as string),
      };
    }

    const logs = await prisma.workoutLog.findMany({
      where,
      include: {
        dayTemplate: {
          include: {
            week: {
              include: {
                phase: true,
              },
            },
          },
        },
      },
      orderBy: { scheduledDate: 'desc' },
    });

    // Generate CSV
    const headers = [
      'date',
      'phase',
      'week',
      'day_template',
      'status',
      'body_weight',
      'energy',
      'sleep_hours',
      'session_rpe',
      'notes',
    ].join(',');

    const rows = logs.map(log => {
      return [
        log.scheduledDate.toISOString().split('T')[0],
        log.dayTemplate.week.phase.name,
        `Week ${log.dayTemplate.week.weekNumber}`,
        log.dayTemplate.name,
        log.status,
        log.bodyWeight || '',
        log.energy || '',
        log.sleepHours || '',
        log.sessionRpe || '',
        log.notes ? `"${log.notes.replace(/"/g, '""')}"` : '',
      ].join(',');
    });

    const csv = [headers, ...rows].join('\n');
    const filename = `workout_logs_${new Date().toISOString().split('T')[0]}.csv`;

    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    return res.send(csv);
  } catch (error) {
    console.error('Export logs error:', error);
    return res.status(500).json({ error: 'Failed to export logs' });
  }
};

export const getTodayWorkout = async (req: AuthRequest, res: Response) => {
  try {
    const userId = req.userId!;
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Get user's current plan progress
    const progress = await prisma.userPlanProgress.findFirst({
      where: {
        userId,
        isActive: true,
      },
      include: {
        plan: true,
        currentPhase: true,
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
      return res.status(404).json({ error: 'No active plan found' });
    }

    // Get logs for current week to determine next day
    const weekStart = new Date(progress.startDate);
    const daysSinceStart = Math.floor((today.getTime() - weekStart.getTime()) / (1000 * 60 * 60 * 24));

    // Check if there's already a log for today
    const todayLog = await prisma.workoutLog.findFirst({
      where: {
        userId,
        scheduledDate: today,
      },
      include: {
        dayTemplate: true,
      },
    });

    if (todayLog) {
      return res.json({ log: todayLog, dayTemplate: todayLog.dayTemplate });
    }

    // Get the next scheduled workout (first day template from current week that hasn't been logged)
    const currentWeekLogs = await prisma.workoutLog.findMany({
      where: {
        userId,
        dayTemplate: {
          weekId: progress.currentWeekId,
        },
      },
    });

    const loggedDayTemplateIds = new Set(currentWeekLogs.map(log => log.dayTemplateId));
    const nextDayTemplate = progress.currentWeek.dayTemplates.find(
      dt => !loggedDayTemplateIds.has(dt.id)
    );

    if (!nextDayTemplate) {
      return res.status(404).json({ error: 'All workouts for this week are complete' });
    }

    return res.json({
      log: null,
      dayTemplate: nextDayTemplate,
      scheduledDate: today,
    });
  } catch (error) {
    console.error('Get today workout error:', error);
    return res.status(500).json({ error: 'Failed to get today\'s workout' });
  }
};
