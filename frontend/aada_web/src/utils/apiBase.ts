const sanitizeBase = (url: string) => url.replace(/\/$/, '');

const inferHostedBackendBase = (): string | null => {
  if (typeof window === 'undefined') {
    return null;
  }

  const { origin, hostname, protocol } = window.location;

  // Azure Container Apps: swap student/admin subdomains for backend
  if (origin.includes('aada-student')) {
    return origin.replace('aada-student', 'aada-backend');
  }

  if (origin.includes('aada-admin')) {
    return origin.replace('aada-admin', 'aada-backend');
  }

  // Local dev fallback: reuse protocol + configurable port
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    const apiPort = import.meta.env.VITE_API_PORT || '8000';
    return `${protocol}//${hostname}:${apiPort}`;
  }

  return null;
};

export const resolveApiBaseUrl = (): string => {
  const envValue = import.meta.env.VITE_API_BASE_URL?.trim();
  if (envValue) {
    // Auto-upgrade to HTTPS if the frontend is served securely
    if (typeof window !== 'undefined' && window.location.protocol === 'https:' && envValue.startsWith('http://')) {
      return sanitizeBase(envValue.replace(/^http:/, 'https:'));
    }
    return sanitizeBase(envValue);
  }

  const hostedValue = inferHostedBackendBase();
  if (hostedValue) {
    return sanitizeBase(hostedValue);
  }

  return 'http://localhost:8000';
};
