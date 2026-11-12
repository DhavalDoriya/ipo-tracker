import type { Ipo } from './data';

export const DASH = '—';

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// Whole rupees print without paise (₹410); anything else with two decimals (₹52.80).
const inrWhole = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
});
const inrPaise = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' });

const updatedFmt = new Intl.DateTimeFormat('en-IN', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  hour: 'numeric',
  minute: '2-digit',
  timeZone: 'Asia/Kolkata',
});

/** '2026-11-12' -> '12 Nov 2026'. Parsed by hand so the build machine's timezone cannot shift the day. */
export function formatDate(date: string | null | undefined): string {
  if (!date) return DASH;
  const [y, m, d] = date.split('-').map(Number);
  if (!y || !m || !d) return DASH;
  return `${d} ${MONTHS[m - 1]} ${y}`;
}

/** '2026-11-12' -> '12 Nov'. For compact timelines where the year is obvious. */
export function formatDayMonth(date: string | null | undefined): string {
  if (!date) return DASH;
  const [, m, d] = date.split('-').map(Number);
  if (!m || !d) return DASH;
  return `${d} ${MONTHS[m - 1]}`;
}

/** Listing gain against the issue price as '+18.2%' / '−20.0%'; null when either is missing. */
export function listingGain(issue: number | null | undefined, listed: number | null | undefined) {
  if (!issue || listed == null) return null;
  const pct = ((listed - issue) / issue) * 100;
  const sign = pct > 0 ? '+' : pct < 0 ? '−' : '';
  return { pct, text: `${sign}${Math.abs(pct).toFixed(1)}%` };
}

export function formatDateRange(from: string | null, to: string | null): string {
  if (!from && !to) return DASH;
  return `${formatDate(from)} – ${formatDate(to)}`;
}

export function formatInr(amount: number | null | undefined): string {
  if (amount == null) return DASH;
  return (Number.isInteger(amount) ? inrWhole : inrPaise).format(amount);
}

export function formatPriceBand(price: Ipo['offer_price']): string {
  if (!price) return DASH;
  return price.min === price.max
    ? formatInr(price.max)
    : `${formatInr(price.min)} – ${formatInr(price.max)}`;
}

export function formatNumber(n: number | null | undefined): string {
  return n == null ? DASH : n.toLocaleString('en-IN');
}

export function orDash(value: string | null | undefined): string {
  return value ? value : DASH;
}

/** ISO timestamp -> '12 Nov 2026, 4:00 pm IST'. */
export function formatUpdated(iso: string): string {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? DASH : `${updatedFmt.format(d)} IST`;
}
