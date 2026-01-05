import { Router } from 'express';
import { getPlans, getPlan, assignPlan, getPhase } from '../controllers/plan.controller';
import { authenticate } from '../middleware/auth';

const router = Router();

// All routes require authentication
router.use(authenticate);

router.get('/', getPlans);
router.get('/:id', getPlan);
router.post('/assign', assignPlan);
router.get('/phases/:id', getPhase);

export default router;
