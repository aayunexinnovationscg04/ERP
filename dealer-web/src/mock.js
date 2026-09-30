// Shared, deterministic mock data for the new preview pages (Trip Management,
// ERP & Billing, AI Analytics, and the new Fleet/Fuel/Driver sub-pages) that
// don't have a real backend endpoint yet. Kept in one place so the same
// fleet/pilot names show up consistently across every mock page instead of
// each view inventing its own cast of trucks and drivers.
//
// Numbers are generated with a tiny seeded PRNG (not Math.random()) so they
// look organic but are stable across reloads/hot-reloads instead of jumping
// around every time a component remounts.

export const MOCK_VEHICLES = [
  { id: 1, name: 'Highway King', reg: 'CG04 AB 1234' },
  { id: 2, name: 'Steel Runner', reg: 'CG04 AC 5567' },
  { id: 3, name: 'Desert Eagle', reg: 'CG07 BD 8890' },
  { id: 4, name: 'Iron Horse', reg: 'CG04 AK 2211' },
  { id: 5, name: 'Night Rider', reg: 'CG09 CF 3345' },
  { id: 6, name: 'Thunder Bull', reg: 'CG04 AB 7781' },
  { id: 7, name: 'Golden Arrow', reg: 'CG07 BE 4432' },
  { id: 8, name: 'Silver Streak', reg: 'CG04 AJ 9098' },
]

export const MOCK_PILOTS = [
  'Ramesh Kumar', 'Suresh Yadav', 'Anil Verma', 'Vikram Singh',
  'Deepak Sharma', 'Manoj Tiwari', 'Rajesh Patel', 'Sanjay Gupta',
]

export const MOCK_CUSTOMERS = [
  'Shree Balaji Traders', 'Om Sai Petroleum', 'Raipur Steel Works', 'Bhilai Logistics Co.',
  'Chhattisgarh Agro Mills', 'Durg Cement Suppliers', 'Vindhya Transport', 'Mahanadi Warehousing',
]

// Mulberry32 — small, fast, seedable PRNG. Good enough for "plausible-looking
// mock numbers", not for anything cryptographic.
function mulberry32(seed) {
  let a = seed
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

export function seededRandom(seed) { return mulberry32(seed) }
export function pick(rng, arr) { return arr[Math.floor(rng() * arr.length)] }
export function range(rng, min, max) { return min + rng() * (max - min) }
export function rangeInt(rng, min, max) { return Math.floor(range(rng, min, max + 1)) }

export function fmtDate(d) {
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}

export function addDays(base, n) {
  const d = new Date(base)
  d.setDate(d.getDate() + n)
  return d
}
