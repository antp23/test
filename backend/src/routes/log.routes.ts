import { Router } from 'express';
import {
  getLogs,
  getLog,
  createLog,
  updateLog,
  exportLogs,
  getTodayWorkout,
} from '../controllers/log.controller';
import { authenticate } from '../middleware/auth';

const router = Router();

// All routes require authentication
router.use(authenticate);

router.get('/', getLogs);
router.get('/today', getTodayWorkout);
router.get('/export', exportLogs);
router.get('/:id', getLog);
router.post('/', createLog);
router.patch('/:id', updateLog);

export default router;
