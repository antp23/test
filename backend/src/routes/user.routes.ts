import { Router } from 'express';
import { getUser, updateUser } from '../controllers/user.controller';
import { authenticate } from '../middleware/auth';

const router = Router();

// All routes require authentication
router.use(authenticate);

router.get('/:id', getUser);
router.patch('/:id', updateUser);

export default router;
