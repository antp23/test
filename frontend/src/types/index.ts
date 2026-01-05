export enum WorkoutStatus {
  SCHEDULED = 'SCHEDULED',
  COMPLETED = 'COMPLETED',
  PARTIAL = 'PARTIAL',
  SKIPPED = 'SKIPPED',
  RESCHEDULED = 'RESCHEDULED',
  REST = 'REST',
}

export enum DayTemplateType {
  STRUCTURED = 'STRUCTURED',
  ROUTINE_BLOCK = 'ROUTINE_BLOCK',
  REST = 'REST',
}

export interface User {
  id: string;
  name: string;
  email: string;
  activePlanId?: string;
}

export interface Plan {
  id: string;
  name: string;
  description?: string;
  version: number;
  createdById: string;
  createdAt: string;
  isArchived: boolean;
  phases?: Phase[];
}

export interface Phase {
  id: string;
  planId: string;
  name: string;
  order: number;
  description?: string;
  weeks?: Week[];
}

export interface Week {
  id: string;
  phaseId: string;
  weekNumber: number;
  isDeload: boolean;
  notes?: string;
  dayTemplates?: DayTemplate[];
}

export interface DayTemplate {
  id: string;
  weekId: string;
  dayNumber: number;
  name: string;
  type: DayTemplateType;
  structuredContent?: any;
  routineTemplateId?: string;
  isOptional: boolean;
  routineTemplate?: RoutineTemplate;
}

export interface RoutineTemplate {
  id: string;
  userId: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  attachment?: Attachment;
}

export interface Attachment {
  id: string;
  routineTemplateId: string;
  filename: string;
  fileType: 'IMAGE' | 'PDF';
  mimeType: string;
  fileSize: number;
  storagePath: string;
  uploadedAt: string;
}

export interface WorkoutLog {
  id: string;
  userId: string;
  dayTemplateId: string;
  scheduledDate: string;
  actualDate?: string;
  status: WorkoutStatus;
  loggedAt?: string;
  bodyWeight?: number;
  energy?: number;
  sleepHours?: number;
  sessionRpe?: number;
  notes?: string;
  createdAt: string;
  updatedAt: string;
  dayTemplate?: DayTemplate;
}

export interface DashboardData {
  hasActivePlan: boolean;
  currentPhase: {
    id: string;
    name: string;
    progress: number;
  } | null;
  currentWeek: {
    id: string;
    weekNumber: number;
    progress: number;
    isDeload: boolean;
  } | null;
  phaseProgress: number;
  weekProgress: number;
  streak: number;
  nextWorkout: DayTemplate | null;
  recentLogs: WorkoutLog[];
}

export interface CreateLogInput {
  dayTemplateId: string;
  scheduledDate: string;
  actualDate?: string;
  status: WorkoutStatus;
  bodyWeight?: number;
  energy?: number;
  sleepHours?: number;
  sessionRpe?: number;
  notes?: string;
}

export interface UpdateLogInput extends Partial<CreateLogInput> {}
