// src/utils/date.ts
// LOCAL TIME VERSION (no UTC conversions)
// Uses browser's local timezone consistently

/**
 * Format for Analyze page
 * Examples:
 *  - "Just now"
 *  - "5 minutes ago"
 *  - "Yesterday at 11:20 PM"
 *  - "Mar 15 at 10:15 AM"
 */
export function formatCallDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();

  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  const diffHour = Math.floor(diffMin / 60);
  const diffDays = Math.floor(diffHour / 24);

  if (diffMin < 1) return "Just now";

  if (diffMin < 60) {
    return `${diffMin} minute${diffMin > 1 ? "s" : ""} ago`;
  }

  if (diffHour < 24) {
    return `${diffHour} hour${diffHour > 1 ? "s" : ""} ago`;
  }

  if (diffDays === 1) {
    return `Yesterday at ${date.toLocaleTimeString([], {
      hour: "numeric",
      minute: "2-digit",
    })}`;
  }

  if (diffDays < 7) {
    return `${diffDays} days ago`;
  }

  return date.toLocaleDateString([], {
    month: "short",
    day: "numeric",
    year:
      date.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
    hour: "numeric",
    minute: "2-digit",
  });
}

/**
 * History page full formatted date
 * Example:
 *  "Mon, Feb 12, 2026 at 11:21 PM"
 */
export function formatHistoryDate(dateString: string): string {
  const date = new Date(dateString);

  return date.toLocaleDateString([], {
    weekday: "short",
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "numeric",
    minute: "2-digit",
  });
}

/**
 * Relative badge for History page
 * Example:
 *  "Today"
 *  "Yesterday"
 *  "2 days ago"
 */
export function formatRelativeDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();

  const startOfToday = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate()
  );

  const startOfGiven = new Date(
    date.getFullYear(),
    date.getMonth(),
    date.getDate()
  );

  const diffDays = Math.floor(
    (startOfToday.getTime() - startOfGiven.getTime()) /
      (1000 * 60 * 60 * 24)
  );

  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;

  return date.toLocaleDateString([], {
    month: "short",
    day: "numeric",
    year:
      date.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
  });
}

/**
 * Only time (local)
 * Example: "11:21 PM"
 */
export function formatTimeOnly(dateString: string): string {
  const date = new Date(dateString);

  return date.toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
  });
}

/**
 * Precise relative time
 * Example:
 *  "3 minutes ago"
 *  "2 hours ago"
 *  "4 days ago"
 */
export function getRelativeTimeString(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();

  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDays = Math.floor(diffHour / 24);
  const diffWeeks = Math.floor(diffDays / 7);
  const diffMonths = Math.floor(diffDays / 30);
  const diffYears = Math.floor(diffDays / 365);

  if (diffYears > 0)
    return `${diffYears} year${diffYears > 1 ? "s" : ""} ago`;
  if (diffMonths > 0)
    return `${diffMonths} month${diffMonths > 1 ? "s" : ""} ago`;
  if (diffWeeks > 0)
    return `${diffWeeks} week${diffWeeks > 1 ? "s" : ""} ago`;
  if (diffDays > 0)
    return `${diffDays} day${diffDays > 1 ? "s" : ""} ago`;
  if (diffHour > 0)
    return `${diffHour} hour${diffHour > 1 ? "s" : ""} ago`;
  if (diffMin > 0)
    return `${diffMin} minute${diffMin > 1 ? "s" : ""} ago`;

  return "Just now";
}

/**
 * Parse filter date (YYYY-MM-DD) in LOCAL time
 */
export function parseFilterDate(dateString: string): Date {
  const [year, month, day] = dateString.split("-").map(Number);
  return new Date(year, month - 1, day);
}
