import { z } from 'zod';

export const programSchema = z.object({
  id: z.string().uuid(),
  code: z.string(),
  name: z.string(),
  credential_level: z.string().optional(),
  total_clock_hours: z.number().int().nonnegative().optional(),
});

export type Program = z.infer<typeof programSchema>;

export const moduleSchema = z.object({
  id: z.string().uuid(),
  program_id: z.string().uuid(),
  code: z.string(),
  title: z.string(),
  delivery_type: z.string().optional(),
  clock_hours: z.number().int().nonnegative().optional(),
  requires_in_person: z.boolean().optional(),
  position: z.number().int().nonnegative().optional(),
});

export type Module = z.infer<typeof moduleSchema>;

export const moduleListSchema = z.array(moduleSchema);
export const programListSchema = z.array(programSchema);
