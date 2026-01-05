import { Response } from 'express';
import { prisma } from '../server';
import { AuthRequest } from '../middleware/auth';

export const getUser = async (req: AuthRequest, res: Response) => {
  try {
    const { id } = req.params;
    const requestingUserId = req.userId!;

    // Users can only view their own profile
    if (id !== requestingUserId) {
      return res.status(403).json({ error: 'Forbidden' });
    }

    const user = await prisma.user.findUnique({
      where: { id },
      select: {
        id: true,
        name: true,
        email: true,
        activePlanId: true,
        createdAt: true,
      },
    });

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    return res.json(user);
  } catch (error) {
    console.error('Get user error:', error);
    return res.status(500).json({ error: 'Failed to get user' });
  }
};

export const updateUser = async (req: AuthRequest, res: Response) => {
  try {
    const { id } = req.params;
    const requestingUserId = req.userId!;

    // Users can only update their own profile
    if (id !== requestingUserId) {
      return res.status(403).json({ error: 'Forbidden' });
    }

    const { name } = req.body;

    const user = await prisma.user.update({
      where: { id },
      data: {
        ...(name && { name }),
      },
      select: {
        id: true,
        name: true,
        email: true,
        activePlanId: true,
      },
    });

    return res.json(user);
  } catch (error) {
    console.error('Update user error:', error);
    return res.status(500).json({ error: 'Failed to update user' });
  }
};
