const MODELING_STORAGE_PREFIXES = [
  "modeling-draft:",
  "modeling-agent-dock:",
  "modeling-validation-position:",
  "uc5.1.3:erd-layout:v1:",
] as const;

/** Removes only user-scoped modeling state, preserving language and theme preferences. */
export function clearUserModelingDrafts(storage: Storage = window.localStorage): void {
  const matchingKeys = Array.from({ length: storage.length }, (_, index) => storage.key(index))
    .filter((key): key is string => Boolean(key))
    .filter((key) => MODELING_STORAGE_PREFIXES.some((prefix) => key.startsWith(prefix)));
  matchingKeys.forEach((key) => storage.removeItem(key));
}
