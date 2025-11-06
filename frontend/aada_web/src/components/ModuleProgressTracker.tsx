import { useEffect, useRef, useCallback, useState } from 'react';
import { axiosInstance } from '@/api/http-client';
import { useAuthStore } from '@/stores/auth-store';

/**
 * Progress data structure matching backend API
 */
interface ModuleProgress {
  enrollment_id: string;
  module_id: string;
  scorm_status?: string;
  score?: number;
  progress_pct?: number;
  last_scroll_position?: number;
  active_time_seconds?: number;
  sections_viewed?: string[];
}

interface ModuleProgressResponse extends ModuleProgress {
  id: string;
  module_code: string;
  module_title: string;
  last_activity?: string;
  last_accessed_at?: string;
}

interface ModuleProgressTrackerProps {
  moduleId: string;
  enrollmentId: string;
  /**
   * Selector for sections to track (e.g., 'h2, h3, .section')
   */
  sectionSelector?: string;
  /**
   * Auto-save interval in milliseconds (default: 30 seconds)
   */
  saveInterval?: number;
  /**
   * Enable/disable scroll-to-last-position on mount
   */
  enableResumeScroll?: boolean;
  /**
   * Callback when progress is saved
   */
  onProgressSaved?: (progress: ModuleProgressResponse) => void;
}

/**
 * ModuleProgressTracker Component
 *
 * Tracks student engagement with module content:
 * - Scroll position (for "resume where you left off")
 * - Active time (page focused + user activity)
 * - Sections viewed (using IntersectionObserver)
 *
 * Auto-saves progress every 30 seconds (configurable)
 */
export const ModuleProgressTracker: React.FC<ModuleProgressTrackerProps> = ({
  moduleId,
  enrollmentId,
  sectionSelector = 'h2, h3',
  saveInterval = 30000, // 30 seconds
  enableResumeScroll = true,
  onProgressSaved,
}) => {
  const user = useAuthStore((state) => state.user);
  const userId = user?.id;

  // Tracking state
  const [scrollPosition, setScrollPosition] = useState(0);
  const [activeTimeSeconds, setActiveTimeSeconds] = useState(0);
  const [sectionsViewed, setSectionsViewed] = useState<Set<string>>(new Set());
  const [hasLoadedProgress, setHasLoadedProgress] = useState(false);

  // Refs for intervals and observers
  const activeTimeIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const saveIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastActivityRef = useRef<number>(Date.now());
  const isPageFocusedRef = useRef<boolean>(true);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const hasScrolledToPositionRef = useRef<boolean>(false);

  /**
   * Load existing progress from backend
   */
  const loadProgress = useCallback(async () => {
    if (!userId || !moduleId) return;

    try {
      const response = await axiosInstance<ModuleProgressResponse>({
        method: 'GET',
        url: `/api/progress/${userId}/module/${moduleId}`,
      });

      const progress = response.data;

      // Restore state
      if (progress.last_scroll_position) {
        setScrollPosition(progress.last_scroll_position);
      }
      if (progress.active_time_seconds) {
        setActiveTimeSeconds(progress.active_time_seconds);
      }
      if (progress.sections_viewed) {
        setSectionsViewed(new Set(progress.sections_viewed));
      }

      // Scroll to last position if enabled and not already scrolled
      if (enableResumeScroll && progress.last_scroll_position && !hasScrolledToPositionRef.current) {
        // Use setTimeout to ensure DOM is ready
        setTimeout(() => {
          window.scrollTo({
            top: progress.last_scroll_position,
            behavior: 'smooth',
          });
          hasScrolledToPositionRef.current = true;
        }, 100);
      }

      setHasLoadedProgress(true);
    } catch (error) {
      console.error('Failed to load progress:', error);
      setHasLoadedProgress(true); // Continue even if load fails
    }
  }, [userId, moduleId, enableResumeScroll]);

  /**
   * Save progress to backend
   */
  const saveProgress = useCallback(async () => {
    if (!enrollmentId || !moduleId) {
      console.warn('Cannot save progress: missing enrollmentId or moduleId');
      return;
    }

    const progressData: ModuleProgress = {
      enrollment_id: enrollmentId,
      module_id: moduleId,
      last_scroll_position: scrollPosition,
      active_time_seconds: activeTimeSeconds,
      sections_viewed: Array.from(sectionsViewed),
    };

    try {
      const response = await axiosInstance<ModuleProgressResponse>({
        method: 'POST',
        url: '/api/progress/',
        data: progressData,
      });

      if (onProgressSaved) {
        onProgressSaved(response.data);
      }

      console.log('[ModuleProgressTracker] Progress saved:', response.data);
    } catch (error) {
      console.error('[ModuleProgressTracker] Failed to save progress:', error);
    }
  }, [enrollmentId, moduleId, scrollPosition, activeTimeSeconds, sectionsViewed, onProgressSaved]);

  /**
   * Track scroll position
   */
  useEffect(() => {
    const handleScroll = () => {
      setScrollPosition(window.scrollY);
      lastActivityRef.current = Date.now();
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  /**
   * Track page focus/blur
   */
  useEffect(() => {
    const handleFocus = () => {
      isPageFocusedRef.current = true;
    };

    const handleBlur = () => {
      isPageFocusedRef.current = false;
    };

    window.addEventListener('focus', handleFocus);
    window.addEventListener('blur', handleBlur);

    return () => {
      window.removeEventListener('focus', handleFocus);
      window.removeEventListener('blur', handleBlur);
    };
  }, []);

  /**
   * Track user activity (mouse move, keyboard, clicks)
   */
  useEffect(() => {
    const updateActivity = () => {
      lastActivityRef.current = Date.now();
    };

    window.addEventListener('mousemove', updateActivity, { passive: true });
    window.addEventListener('keydown', updateActivity, { passive: true });
    window.addEventListener('click', updateActivity, { passive: true });

    return () => {
      window.removeEventListener('mousemove', updateActivity);
      window.removeEventListener('keydown', updateActivity);
      window.removeEventListener('click', updateActivity);
    };
  }, []);

  /**
   * Track active time (page focused + recent activity)
   */
  useEffect(() => {
    activeTimeIntervalRef.current = setInterval(() => {
      const timeSinceActivity = Date.now() - lastActivityRef.current;
      const isActive = isPageFocusedRef.current && timeSinceActivity < 5000; // 5 seconds threshold

      if (isActive) {
        setActiveTimeSeconds((prev) => prev + 1);
      }
    }, 1000); // Check every second

    return () => {
      if (activeTimeIntervalRef.current) {
        clearInterval(activeTimeIntervalRef.current);
      }
    };
  }, []);

  /**
   * Track sections viewed using IntersectionObserver
   */
  useEffect(() => {
    if (!hasLoadedProgress) return; // Wait until progress is loaded

    const sections = document.querySelectorAll(sectionSelector);

    if (sections.length === 0) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && entry.target.id) {
            setSectionsViewed((prev) => {
              const updated = new Set(prev);
              updated.add(entry.target.id);
              return updated;
            });
          }
        });
      },
      {
        threshold: 0.5, // Section must be 50% visible
        rootMargin: '-50px 0px', // Offset from viewport edges
      }
    );

    // Observe all sections
    sections.forEach((section) => {
      // Ensure section has an ID
      if (!section.id) {
        section.id = `section-${Math.random().toString(36).substr(2, 9)}`;
      }
      observerRef.current?.observe(section);
    });

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [sectionSelector, hasLoadedProgress]);

  /**
   * Auto-save progress at regular intervals
   */
  useEffect(() => {
    if (!hasLoadedProgress) return; // Don't save until we've loaded initial progress

    saveIntervalRef.current = setInterval(() => {
      saveProgress();
    }, saveInterval);

    return () => {
      if (saveIntervalRef.current) {
        clearInterval(saveIntervalRef.current);
      }
    };
  }, [saveProgress, saveInterval, hasLoadedProgress]);

  /**
   * Load progress on mount
   */
  useEffect(() => {
    loadProgress();
  }, [loadProgress]);

  /**
   * Save progress on unmount
   */
  useEffect(() => {
    return () => {
      if (hasLoadedProgress) {
        // Save one last time before unmounting
        saveProgress();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasLoadedProgress]);

  // This component renders nothing (tracking only)
  return null;
};

export default ModuleProgressTracker;
