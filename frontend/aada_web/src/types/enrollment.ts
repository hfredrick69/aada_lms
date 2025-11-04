import { z } from 'zod';

export const enrollmentSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  program_id: z.string().uuid(),
  start_date: z.string(),
  expected_end_date: z.string().nullable().optional(),
  status: z.string(),
});

export type Enrollment = z.infer<typeof enrollmentSchema>;
export const enrollmentListSchema = z.array(enrollmentSchema);
