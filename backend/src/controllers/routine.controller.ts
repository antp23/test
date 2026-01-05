import { Response } from 'express';
import { prisma } from '../server';
import { AuthRequest } from '../middleware/auth';

export const getRoutines = async (req: AuthRequest, res: Response) => {
  try {
    const userId = req.userId!;

    const routines = await prisma.routineTemplate.findMany({
      where: { userId },
      include: {
        attachment: true,
      },
      orderBy: { createdAt: 'desc' },
    });

    return res.json(routines);
  } catch (error) {
    console.error('Get routines error:', error);
    return res.status(500).json({ error: 'Failed to get routines' });
  }
};

export const getRoutine = async (req: AuthRequest, res: Response) => {
  try {
    const userId = req.userId!;
    const { id } = req.params;

    const routine = await prisma.routineTemplate.findFirst({
      where: {
        id,
        userId,
      },
      include: {
        attachment: true,
      },
    });

    if (!routine) {
      return res.status(404).json({ error: 'Routine not found' });
    }

    return res.json(routine);
  } catch (error) {
    console.error('Get routine error:', error);
    return res.status(500).json({ error: 'Failed to get routine' });
  }
};

export const createRoutine = async (req: AuthRequest, res: Response) => {
  try {
    const userId = req.userId!;
    const { name, description } = req.body;

    if (!name) {
      return res.status(400).json({ error: 'Name is required' });
    }

    const routine = await prisma.routineTemplate.create({
      data: {
        userId,
        name,
        description,
      },
    });

    return res.status(201).json(routine);
  } catch (error) {
    console.error('Create routine error:', error);
    return res.status(500).json({ error: 'Failed to create routine' });
  }
};

export const updateRoutine = async (req: AuthRequest, res: Response) => {
  try {
    const userId = req.userId!;
    const { id } = req.params;
    const { name, description } = req.body;

    // Check if routine exists and belongs to user
    const existingRoutine = await prisma.routineTemplate.findFirst({
      where: { id, userId },
    });

    if (!existingRoutine) {
      return res.status(404).json({ error: 'Routine not found' });
    }

    const routine = await prisma.routineTemplate.update({
      where: { id },
      data: {
        ...(name && { name }),
        ...(description !== undefined && { description }),
      },
    });

    return res.json(routine);
  } catch (error) {
    console.error('Update routine error:', error);
    return res.status(500).json({ error: 'Failed to update routine' });
  }
};

export const deleteRoutine = async (req: AuthRequest, res: Response) => {
  try {
    const userId = req.userId!;
    const { id } = req.params;

    // Check if routine exists and belongs to user
    const existingRoutine = await prisma.routineTemplate.findFirst({
      where: { id, userId },
    });

    if (!existingRoutine) {
      return res.status(404).json({ error: 'Routine not found' });
    }

    await prisma.routineTemplate.delete({
      where: { id },
    });

    return res.json({ message: 'Routine deleted successfully' });
  } catch (error) {
    console.error('Delete routine error:', error);
    return res.status(500).json({ error: 'Failed to delete routine' });
  }
};
