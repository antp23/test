# Workout Tracker App

A lightweight web application for tracking workout adherence and progress through structured workout programs. Built for Anthony and Sakshee to track their multi-phase training programs.

## Features

- **Daily Workout Logging**: Quick and easy workout completion tracking (Completed, Partial, Skipped)
- **Optional Metrics**: Track body weight, energy levels (1-10), sleep hours, session RPE (1-10), and notes
- **Dashboard**: Visual progress tracking with phase/week progress bars and calendar heatmap
- **Calendar View**: Monthly heatmap visualization of workout consistency
- **Plan Management**: View structured multi-phase workout plans
- **History & Export**: Review past workouts with filtering and CSV export functionality
- **Mobile-Optimized**: Responsive design for one-handed mobile use

## Tech Stack

### Backend
- Node.js + Express + TypeScript
- PostgreSQL database
- Prisma ORM
- JWT authentication
- bcrypt for password hashing

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- React Query (server state)
- Zustand (client state)
- React Router v6 (routing)
- date-fns (date utilities)

## Prerequisites

- Node.js 18+ and npm
- PostgreSQL 15+ database

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd workout-tracker
```

### 2. Install dependencies

```bash
# Install root dependencies
npm install

# Install backend dependencies
cd backend
npm install

# Install frontend dependencies
cd ../frontend
npm install

cd ..
```

### 3. Set up PostgreSQL database

Create a PostgreSQL database for the application:

```sql
CREATE DATABASE workout_tracker;
```

### 4. Configure environment variables

Create a `.env` file in the `backend` directory:

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` with your database credentials:

```env
# Database
DATABASE_URL="postgresql://username:password@localhost:5432/workout_tracker?schema=public"

# JWT
JWT_SECRET="your-secret-key-change-in-production"
JWT_EXPIRES_IN="7d"

# Server
PORT=3001
NODE_ENV="development"

# CORS
FRONTEND_URL="http://localhost:5173"
```

### 5. Run database migrations

```bash
cd backend
npm run generate  # Generate Prisma Client
npm run migrate   # Run database migrations
```

### 6. Seed the database

This will create:
- Two users (Anthony and Sakshee)
- Their complete 12-week workout plans
- Initial plan progress tracking

```bash
npm run seed
```

### 7. Start the development servers

From the root directory:

```bash
# Start both frontend and backend
npm run dev
```

Or run them separately:

```bash
# Terminal 1 - Backend
cd backend
npm run dev

# Terminal 2 - Frontend
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:3001

## Default Login Credentials

After seeding, you can log in with:

**Anthony:**
- Email: `anthony@workout.app`
- Password: `password123`

**Sakshee:**
- Email: `sakshee@workout.app`
- Password: `password123`

## Project Structure

```
workout-tracker/
├── backend/
│   ├── prisma/
│   │   └── schema.prisma      # Database schema
│   ├── src/
│   │   ├── controllers/       # Route controllers
│   │   ├── middleware/        # Express middleware
│   │   ├── routes/           # API routes
│   │   ├── types/            # TypeScript types
│   │   ├── utils/            # Utility functions
│   │   ├── server.ts         # Express server setup
│   │   └── seed.ts           # Database seed script
│   ├── package.json
│   └── tsconfig.json
├── frontend/
│   ├── src/
│   │   ├── api/              # API client and services
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── store/            # Zustand stores
│   │   ├── types/            # TypeScript types
│   │   ├── App.tsx           # Main app component
│   │   ├── main.tsx          # Entry point
│   │   └── index.css         # Global styles
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
└── package.json              # Root workspace config
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Plans
- `GET /api/plans` - List all plans
- `GET /api/plans/:id` - Get plan details
- `POST /api/plans/assign` - Assign plan to user
- `GET /api/plans/phases/:id` - Get phase details

### Workout Logs
- `GET /api/logs` - List logs (with filters)
- `GET /api/logs/today` - Get today's workout
- `GET /api/logs/:id` - Get log details
- `POST /api/logs` - Create new log
- `PATCH /api/logs/:id` - Update log (within 7 days)
- `GET /api/logs/export` - Export logs to CSV

### Dashboard
- `GET /api/dashboard` - Get dashboard data

### Users
- `GET /api/users/:id` - Get user profile
- `PATCH /api/users/:id` - Update user

### Routines (v1.1 feature)
- `GET /api/routines` - List routines
- `GET /api/routines/:id` - Get routine
- `POST /api/routines` - Create routine
- `PATCH /api/routines/:id` - Update routine
- `DELETE /api/routines/:id` - Delete routine

## Key Features Implementation

### Workout Status Types
- `COMPLETED` - Full workout completed
- `PARTIAL` - Some portion completed
- `SKIPPED` - Workout not performed (breaks streak)
- `RESCHEDULED` - Moved to different date (neutral for streak)
- `SCHEDULED` - Future workout
- `REST` - Designated rest day

### Streak Calculation
- Counts consecutive days with COMPLETED or PARTIAL logs
- REST days don't break streak
- RESCHEDULED days don't break streak
- SKIPPED days break streak

### Phase Progress
- Calculated as: (Completed + Partial Days) / Total Required Days × 100
- Only counts non-REST, non-optional day templates

## Database Schema

Key entities:
- **Users** - User accounts
- **Plans** - Workout plans
- **Phases** - Major training blocks (4 weeks each)
- **Weeks** - Weekly schedules
- **DayTemplates** - Workout templates for each day
- **WorkoutLogs** - Logged workout data
- **UserPlanProgress** - Current progress tracking
- **RoutineTemplates** - Custom user routines (v1.1)
- **Attachments** - Files for routines (v1.1)

## Development

### Backend Development

```bash
cd backend

# Watch mode
npm run dev

# Build
npm run build

# Prisma Studio (database GUI)
npm run studio

# Create migration
npm run migrate

# Generate Prisma Client
npm run generate
```

### Frontend Development

```bash
cd frontend

# Dev server
npm run dev

# Build
npm run build

# Preview production build
npm run preview
```

## Production Build

```bash
# Build both frontend and backend
npm run build

# Start production server
cd backend
npm start
```

## Deployment Recommendations

### Backend
- Deploy to Railway, Render, or similar Node.js hosting
- Use managed PostgreSQL (Railway, Render, Supabase)
- Set environment variables in hosting platform
- Run migrations: `npm run migrate:deploy`
- Run seed (first deployment only): `npm run seed`

### Frontend
- Deploy to Vercel, Netlify, or similar
- Build command: `npm run build`
- Output directory: `dist`
- Set `VITE_API_URL` environment variable if backend is on different domain

## Future Enhancements (v1.1+)

- [ ] Custom routine templates with attachments
- [ ] Reschedule workout functionality
- [ ] Notes search in history
- [ ] Weekly email summaries
- [ ] OAuth login (Google)
- [ ] Push notifications
- [ ] Exercise-level tracking (sets/reps/weight)
- [ ] Progress photos
- [ ] Wearable integrations

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check DATABASE_URL in `.env`
- Ensure database exists

### Port Already in Use
- Backend default: 3001
- Frontend default: 5173
- Change in `.env` (backend) or `vite.config.ts` (frontend)

### Prisma Issues
```bash
cd backend
npm run generate  # Regenerate Prisma Client
npx prisma db push  # Push schema changes without migration
```

## License

Private - For personal use by Anthony and Sakshee