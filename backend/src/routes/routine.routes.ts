import { Router } from 'express';
import {
  getRoutines,
  getRoutine,
  createRoutine,
  updateRoutine,
  deleteRoutine,
} from '../controllers/routine.controller';
import { authenticate } from '../middleware/auth';

const router = Router();

// All routes require authentication
router.use(authenticate);

router.get('/', getRoutines);
router.get('/:id', getRoutine);
router.post('/', createRoutine);
router.patch('/:id', updateRoutine);
router.delete('/:id', deleteRoutine);

export default router;
