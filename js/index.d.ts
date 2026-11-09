export interface Rates { input: number; cachedInput: number; output: number }
export interface CostOptions { batch?: boolean; on?: string | Date }
export interface Model {
  id: string; provider: "OpenAI" | "Anthropic" | "Google"; name: string; tier: string; status: string;
  standard: Rates; batch: Rates; cacheWrite: number | null;
  longContextThreshold: number | null; longContext: Rates | null;
  scheduledChanges: unknown[]; sourceUrl: string; checked: string;
  rates(opts?: CostOptions): Rates;
  cost(inputTokens: number, outputTokens: number, cachedTokens?: number, opts?: CostOptions): number;
}
export const CHECKED: string;
export function models(opts?: { provider?: string; tier?: string; includeLegacy?: boolean }): Model[];
export function get(id: string): Model;
export function cost(id: string, inputTokens: number, outputTokens: number, cachedTokens?: number, opts?: CostOptions): number;
export function compare(inputTokens: number, outputTokens: number, cachedTokens?: number, opts?: CostOptions & { ids?: string[] }): { model: Model; cost: number }[];
export function changes(): { date: string; provider: string; type: string; title: string; detail: string; source_url: string }[];
