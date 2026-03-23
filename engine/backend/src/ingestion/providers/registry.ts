// src/ingestion/providers/registry.ts
import type { BaseProvider } from "./baseProvider.ts";
import { sofascoreProvider } from "./sofascoreProvider.ts";

const providers: Record<string, BaseProvider> = {};

// --- Register providers here ---
registerProvider("sofascore", sofascoreProvider);

// --- Registry API ---
export function registerProvider(name: string, provider: BaseProvider) {
  providers[name] = provider;
}

export function getProvider(name: string): BaseProvider | undefined {
  return providers[name];
}

export function listProviders(): string[] {
  return Object.keys(providers);
}
