import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function main() {
  console.log('Starting seed...');

  // Create users
  const anthonyPassword = await bcrypt.hash('password123', 10);
  const saksheePassword = await bcrypt.hash('password123', 10);

  const anthony = await prisma.user.upsert({
    where: { email: 'anthony@workout.app' },
    update: {},
    create: {
      name: 'Anthony',
      email: 'anthony@workout.app',
      passwordHash: anthonyPassword,
    },
  });

  const sakshee = await prisma.user.upsert({
    where: { email: 'sakshee@workout.app' },
    update: {},
    create: {
      name: 'Sakshee',
      email: 'sakshee@workout.app',
      passwordHash: saksheePassword,
    },
  });

  console.log('Created users:', { anthony: anthony.id, sakshee: sakshee.id });

  // Create Anthony's Plan
  const anthonyPlan = await prisma.plan.create({
    data: {
      name: 'Anthony – Full Body Strength & Conditioning (12 Weeks)',
      description: 'Full-body circuits, high intensity, mobility-focused training',
      version: 1,
      createdById: anthony.id,
      phases: {
        create: [
          {
            name: 'Phase 1 - Recomposition & Conditioning Base',
            order: 1,
            description: 'Building foundational strength and conditioning',
            weeks: {
              create: [
                {
                  weekNumber: 1,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Full Body (Lower Emphasis)',
                        type: 'ROUTINE_BLOCK',
                        structuredContent: null,
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Full Body (Functional Power)',
                        type: 'ROUTINE_BLOCK',
                        structuredContent: null,
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Full Body (Upper + Posterior)',
                        type: 'ROUTINE_BLOCK',
                        structuredContent: null,
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Mobility + Conditioning',
                        type: 'ROUTINE_BLOCK',
                        structuredContent: null,
                        isOptional: true,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 2,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Full Body (Lower Emphasis)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Full Body (Functional Power)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Full Body (Upper + Posterior)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Mobility + Conditioning',
                        type: 'ROUTINE_BLOCK',
                        isOptional: true,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 3,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Full Body (Lower Emphasis)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Full Body (Functional Power)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Full Body (Upper + Posterior)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Mobility + Conditioning',
                        type: 'ROUTINE_BLOCK',
                        isOptional: true,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 4,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Full Body (Lower Emphasis)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Full Body (Functional Power)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Full Body (Upper + Posterior)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Mobility + Conditioning',
                        type: 'ROUTINE_BLOCK',
                        isOptional: true,
                      },
                    ],
                  },
                },
              ],
            },
          },
          {
            name: 'Phase 2 - Strength & Stamina',
            order: 2,
            description: 'Building strength and stamina',
            weeks: {
              create: [
                {
                  weekNumber: 1,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Strength Foundations',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Power & Grip',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Push/Pull Balance',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Mobility + Recovery',
                        type: 'ROUTINE_BLOCK',
                        isOptional: true,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 2,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Strength Foundations',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Power & Grip',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Push/Pull Balance',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Mobility + Recovery',
                        type: 'ROUTINE_BLOCK',
                        isOptional: true,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 3,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Strength Foundations',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Power & Grip',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Push/Pull Balance',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Mobility + Recovery',
                        type: 'ROUTINE_BLOCK',
                        isOptional: true,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 4,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Strength Foundations',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Power & Grip',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Push/Pull Balance',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Mobility + Recovery',
                        type: 'ROUTINE_BLOCK',
                        isOptional: true,
                      },
                    ],
                  },
                },
              ],
            },
          },
          {
            name: 'Phase 3 - Power, Endurance & Performance',
            order: 3,
            description: 'Peak performance and power development',
            weeks: {
              create: [
                {
                  weekNumber: 1,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Explosive Strength',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Hybrid Conditioning',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Functional Endurance',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Yoga Flow + Recovery',
                        type: 'ROUTINE_BLOCK',
                        isOptional: true,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 2,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Explosive Strength',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Hybrid Conditioning',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Functional Endurance',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Yoga Flow + Recovery',
                        type: 'ROUTINE_BLOCK',
                        isOptional: true,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 3,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Explosive Strength',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Hybrid Conditioning',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Functional Endurance',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Yoga Flow + Recovery',
                        type: 'ROUTINE_BLOCK',
                        isOptional: true,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 4,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Explosive Strength',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Hybrid Conditioning',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Functional Endurance',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Yoga Flow + Recovery',
                        type: 'ROUTINE_BLOCK',
                        isOptional: true,
                      },
                    ],
                  },
                },
              ],
            },
          },
        ],
      },
    },
  });

  console.log('Created Anthony\'s plan:', anthonyPlan.id);

  // Create Sakshee's Plan
  const saksheePlan = await prisma.plan.create({
    data: {
      name: 'Sakshee – Postpartum Rebuild to Sculpt (12 Weeks)',
      description: 'Postpartum rebuild to sculpt training program',
      version: 1,
      createdById: sakshee.id,
      phases: {
        create: [
          {
            name: 'Phase 1 - Rebuild & Consistency',
            order: 1,
            description: 'Building consistency and foundational strength',
            weeks: {
              create: [
                {
                  weekNumber: 1,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Strength Day A – Full Body + Core',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Mobility / Fun Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Strength Day B – Lower Body Focus',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Mobility / Fun Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 2,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Strength Day A – Full Body + Core',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Mobility / Fun Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Strength Day B – Lower Body Focus',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Mobility / Fun Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 3,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Strength Day A – Full Body + Core',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Mobility / Fun Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Strength Day B – Lower Body Focus',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Mobility / Fun Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 4,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Strength Day A – Full Body + Core',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Mobility / Fun Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Strength Day B – Lower Body Focus',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Mobility / Fun Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                    ],
                  },
                },
              ],
            },
          },
          {
            name: 'Phase 2 - Fat Loss & Strength Foundation',
            order: 2,
            description: 'Building strength foundation and fat loss',
            weeks: {
              create: [
                {
                  weekNumber: 1,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Strength Day A – Full Body',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Cardio Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Strength Day B – Lower Supersets',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Cardio Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 5,
                        name: 'Stretch / Fun Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 2,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Strength Day A – Full Body',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Cardio Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Strength Day B – Lower Supersets',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Cardio Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 5,
                        name: 'Stretch / Fun Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 3,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Strength Day A – Full Body',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Cardio Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Strength Day B – Lower Supersets',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Cardio Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 5,
                        name: 'Stretch / Fun Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 4,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Strength Day A – Full Body',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Cardio Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Strength Day B – Lower Supersets',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Cardio Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 5,
                        name: 'Stretch / Fun Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                    ],
                  },
                },
              ],
            },
          },
          {
            name: 'Phase 3 - Sculpt & Endurance',
            order: 3,
            description: 'Sculpting and endurance development',
            weeks: {
              create: [
                {
                  weekNumber: 1,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Strength Day A – Upper Sculpt',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Cardio Day (Steady-State)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Strength Day B – Lower Sculpt',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Cardio Day (Intervals)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 5,
                        name: 'Stretch / Recovery Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 2,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Strength Day A – Upper Sculpt',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Cardio Day (Steady-State)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Strength Day B – Lower Sculpt',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Cardio Day (Intervals)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 5,
                        name: 'Stretch / Recovery Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 3,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Strength Day A – Upper Sculpt',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Cardio Day (Steady-State)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Strength Day B – Lower Sculpt',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Cardio Day (Intervals)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 5,
                        name: 'Stretch / Recovery Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                    ],
                  },
                },
                {
                  weekNumber: 4,
                  isDeload: false,
                  dayTemplates: {
                    create: [
                      {
                        dayNumber: 1,
                        name: 'Strength Day A – Upper Sculpt',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 2,
                        name: 'Cardio Day (Steady-State)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 3,
                        name: 'Strength Day B – Lower Sculpt',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 4,
                        name: 'Cardio Day (Intervals)',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                      {
                        dayNumber: 5,
                        name: 'Stretch / Recovery Day',
                        type: 'ROUTINE_BLOCK',
                        isOptional: false,
                      },
                    ],
                  },
                },
              ],
            },
          },
        ],
      },
    },
  });

  console.log('Created Sakshee\'s plan:', saksheePlan.id);

  // Get first phase and week for each plan
  const anthonyFirstPhase = await prisma.phase.findFirst({
    where: { planId: anthonyPlan.id },
    orderBy: { order: 'asc' },
    include: {
      weeks: {
        orderBy: { weekNumber: 'asc' },
        take: 1,
      },
    },
  });

  const saksheeFirstPhase = await prisma.phase.findFirst({
    where: { planId: saksheePlan.id },
    orderBy: { order: 'asc' },
    include: {
      weeks: {
        orderBy: { weekNumber: 'asc' },
        take: 1,
      },
    },
  });

  // Create plan progress for both users
  if (anthonyFirstPhase && anthonyFirstPhase.weeks[0]) {
    await prisma.userPlanProgress.create({
      data: {
        userId: anthony.id,
        planId: anthonyPlan.id,
        currentPhaseId: anthonyFirstPhase.id,
        currentWeekId: anthonyFirstPhase.weeks[0].id,
        startDate: new Date(),
        isActive: true,
      },
    });

    // Update user's active plan
    await prisma.user.update({
      where: { id: anthony.id },
      data: { activePlanId: anthonyPlan.id },
    });

    console.log('Created plan progress for Anthony');
  }

  if (saksheeFirstPhase && saksheeFirstPhase.weeks[0]) {
    await prisma.userPlanProgress.create({
      data: {
        userId: sakshee.id,
        planId: saksheePlan.id,
        currentPhaseId: saksheeFirstPhase.id,
        currentWeekId: saksheeFirstPhase.weeks[0].id,
        startDate: new Date(),
        isActive: true,
      },
    });

    // Update user's active plan
    await prisma.user.update({
      where: { id: sakshee.id },
      data: { activePlanId: saksheePlan.id },
    });

    console.log('Created plan progress for Sakshee');
  }

  console.log('Seed completed successfully!');
  console.log('\nLogin credentials:');
  console.log('Anthony: anthony@workout.app / password123');
  console.log('Sakshee: sakshee@workout.app / password123');
}

main()
  .catch((e) => {
    console.error('Seed failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
