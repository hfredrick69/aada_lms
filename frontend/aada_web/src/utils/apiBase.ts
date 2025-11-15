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
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === 'host.docker.internal') {
    const apiPort = import.meta.env.VITE_API_PORT || '8000';
    return `${protocol}//${hostname}:${apiPort}`;
  }

  return null;
};

export const resolveApiBaseUrl = (): string => {
  const envValue = import.meta.env.VITE_API_BASE_URL?.trim();
  if (envValue) {
    let normalized = sanitizeBase(envValue);

    if (typeof window !== 'undefined') {
      try {
        const parsed = new URL(normalized);
        const dockerHost = window.location.hostname === 'host.docker.internal';
        const localhostAlias = ['localhost', '127.0.0.1'].includes(parsed.hostname);
        if (dockerHost && localhostAlias) {
          parsed.hostname = window.location.hostname;
          parsed.protocol = window.location.protocol;
          normalized = sanitizeBase(parsed.toString());
        }
      } catch {
        // Ignore malformed URLs and fall through to the existing value
      }

      if (window.location.protocol === 'https:' && normalized.startsWith('http://')) {
        normalized = sanitizeBase(normalized.replace(/^http:/, 'https:'));
      }
    }

    return normalized;
  }

  const hostedValue = inferHostedBackendBase();
  if (hostedValue) {
    return sanitizeBase(hostedValue);
  }

  return 'http://localhost:8000';
};
