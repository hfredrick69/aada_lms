/**
 * Manual payments API hooks (orval didn't generate these)
 */
import { useQuery } from '@tanstack/react-query';
import type { UseQueryOptions } from '@tanstack/react-query';
import { axiosInstance } from './http-client';

// Type definitions matching backend Pydantic models
export interface InvoiceLineItem {
  id: string;
  user_id: string;
  program_id: string | null;
  line_type: string;
  amount_cents: number;
  description: string | null;
  created_at: string | null;
}

export interface StudentBalance {
  user_id: string;
  total_charges_cents: number;
  total_payments_cents: number;
  balance_cents: number;
}

// GET /api/payments/ - List all transactions
export const listPayments = (userId?: string, signal?: AbortSignal) => {
  const params = userId ? { user_id: userId } : {};
  return axiosInstance<InvoiceLineItem[]>({
    url: '/api/payments/',
    method: 'GET',
    params,
    signal,
  });
};

export const useListPayments = (
  userId?: string,
  options?: Partial<UseQueryOptions<InvoiceLineItem[], unknown>>
) => {
  return useQuery<InvoiceLineItem[], unknown>({
    queryKey: ['/api/payments/', userId],
    queryFn: ({ signal }) => listPayments(userId, signal).then((res) => res.data),
    ...options,
  });
};

// GET /api/payments/balance/{user_id} - Get student balance
export const getStudentBalance = (userId: string, signal?: AbortSignal) => {
  return axiosInstance<StudentBalance>({
    url: `/api/payments/balance/${userId}`,
    method: 'GET',
    signal,
  });
};

export const useStudentBalance = (
  userId?: string,
  options?: Partial<UseQueryOptions<StudentBalance, unknown>>
) => {
  return useQuery<StudentBalance, unknown>({
    queryKey: ['/api/payments/balance', userId],
    queryFn: ({ signal }) => {
      if (!userId) throw new Error('User ID required');
      return getStudentBalance(userId, signal).then((res) => res.data);
    },
    enabled: !!userId,
    ...options,
  });
};

// GET /api/payments/history/{user_id} - Get payment history
export const getPaymentHistory = (userId: string, signal?: AbortSignal) => {
  return axiosInstance<InvoiceLineItem[]>({
    url: `/api/payments/history/${userId}`,
    method: 'GET',
    signal,
  });
};

export const usePaymentHistory = (
  userId?: string,
  options?: Partial<UseQueryOptions<InvoiceLineItem[], unknown>>
) => {
  return useQuery<InvoiceLineItem[], unknown>({
    queryKey: ['/api/payments/history', userId],
    queryFn: ({ signal }) => {
      if (!userId) throw new Error('User ID required');
      return getPaymentHistory(userId, signal).then((res) => res.data);
    },
    enabled: !!userId,
    ...options,
  });
};
