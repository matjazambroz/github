function getUtcOffsetMs(atUtcMs: number, timeZone: string): number {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone,
    timeZoneName: "longOffset",
    hour: "2-digit",
  }).formatToParts(new Date(atUtcMs));

  const offsetPart = parts.find((p) => p.type === "timeZoneName")?.value ?? "GMT+00:00";
  const match = offsetPart.match(/GMT([+-])(\d{2}):(\d{2})/);
  if (!match) {
    return 0;
  }

  const sign = match[1] === "-" ? -1 : 1;
  const hours = Number(match[2]);
  const minutes = Number(match[3]);
  return sign * (hours * 60 + minutes) * 60 * 1000;
}

/**
 * Converts a "YYYY-MM-DD" date to the epoch-ms timestamp for midnight of
 * that date in the given IANA time zone (e.g. "Europe/Ljubljana"),
 * correctly accounting for CET/CEST DST offset.
 */
export function dateOnlyToEpochMs(dateStr: string, timeZone: string): number {
  const match = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) {
    throw new Error(`Invalid date "${dateStr}", expected YYYY-MM-DD`);
  }

  const [, y, m, d] = match;
  const utcGuess = Date.UTC(Number(y), Number(m) - 1, Number(d), 0, 0, 0);
  const offsetMs = getUtcOffsetMs(utcGuess, timeZone);
  return utcGuess - offsetMs;
}
