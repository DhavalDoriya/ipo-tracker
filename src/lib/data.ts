// The only module that reads data/. Schema: docs/DATABASE.md.
import fs from 'node:fs';
import path from 'node:path';

const DATA_DIR = path.resolve(process.cwd(), 'data');

export type IpoType = 'mainboard' | 'sme';
export type IpoStatus = 'upcoming' | 'open' | 'closed' | 'listed';

export interface Ipo {
  id: string;
  name: string;
  type: IpoType;
  exchange: string;
  status: IpoStatus;
  open_date: string | null;
  close_date: string | null;
  listing_date: string | null;
  offer_price: { min: number; max: number } | null;
  list_price: number | null;
  lot_size: number | null;
  issue_size: string | null;
  subscription: string | null;
  subscription_breakup: { retail: string | null; hni: string | null; qib: string | null } | null;
  gmp: number | null;
  source_url: string | null;
}

export interface IpoWithGmp extends Ipo {
  gmp_percent: string | null;
}

export interface IposFile {
  updated_at: string;
  source: string;
  sample?: boolean;
  ipos: Ipo[];
}

export interface ComingSoonIpo {
  id: string;
  name: string;
  type: IpoType;
  exchange: string;
  expected: string | null;
  source_url: string | null;
}

export interface Buyback {
  id: string;
  name: string;
  type: 'tender' | 'open_market';
  record_date: string | null;
  open_date: string | null;
  close_date: string | null;
  buyback_price: number | null;
  status: 'upcoming' | 'open' | 'closed';
}

export interface BuybacksFile {
  updated_at: string;
  buybacks: Buyback[];
}

interface GmpFile {
  updated_at: string;
  note: string;
  entries: { id: string; gmp: number; percent: string | null }[];
}

export interface ChecklistParameter {
  name: string;
  meaning: string;
  positive: string;
  negative: string;
  analysis: string | null;
}

export interface Checklist {
  slug: string;
  company: string;
  ipo_id?: string;
  sections: { title: string; parameters: ChecklistParameter[] }[];
}

function readJson<T>(file: string): T {
  const full = path.join(DATA_DIR, file);
  try {
    return JSON.parse(fs.readFileSync(full, 'utf-8')) as T;
  } catch (err) {
    throw new Error(`Cannot load data/${file}: ${(err as Error).message}`);
  }
}

export function loadIposFile(): IposFile {
  return readJson<IposFile>('ipos.json');
}

/** IPOs with GMP from gmp.json joined by id. */
export function loadIpos(): IpoWithGmp[] {
  const gmp = new Map(readJson<GmpFile>('gmp.json').entries.map((e) => [e.id, e]));
  return loadIposFile().ipos.map((ipo) => {
    const entry = gmp.get(ipo.id);
    return { ...ipo, gmp: entry?.gmp ?? ipo.gmp, gmp_percent: entry?.percent ?? null };
  });
}

export function loadComingSoon(): ComingSoonIpo[] {
  return readJson<{ ipos: ComingSoonIpo[] }>('coming_soon.json').ipos;
}

export function loadBuybacks(): BuybacksFile {
  return readJson<BuybacksFile>('buybacks.json');
}

export function loadChecklists(): Checklist[] {
  return fs
    .readdirSync(path.join(DATA_DIR, 'checklists'))
    .filter((f) => f.endsWith('.json'))
    .sort()
    .map((f) => ({
      ...readJson<Omit<Checklist, 'slug'>>(path.join('checklists', f)),
      slug: f.replace(/\.json$/, ''),
    }));
}

/** ipo id -> checklist slug, for linking cards to their checklist. */
export function checklistSlugsByIpo(): Map<string, string> {
  const map = new Map<string, string>();
  for (const c of loadChecklists()) if (c.ipo_id) map.set(c.ipo_id, c.slug);
  return map;
}
