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

// Epoch-ms timestamp for midnight of a "YYYY-MM-DD" date in the given IANA
// time zone, correctly accounting for CET/CEST DST offset.
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

// "YYYY-MM-DD" for "today" in the given IANA time zone.
export function todayDateString(timeZone: string): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone }).format(new Date());
}

export function todayParts(timeZone: string): { year: number; month: string; day: string } {
  const parts = new Intl.DateTimeFormat("en-CA", { timeZone, year: "numeric", month: "2-digit", day: "2-digit" })
    .formatToParts(new Date())
    .reduce<Record<string, string>>((acc, p) => ({ ...acc, [p.type]: p.value }), {});
  return { year: Number(parts.year), month: parts.month ?? "01", day: parts.day ?? "01" };
}

// Monday (ISO week start) of the current week, as a "YYYY-MM-DD" string.
export function mondayOfThisWeek(timeZone: string): string {
  const { year, month, day } = todayParts(timeZone);
  const asUtc = new Date(Date.UTC(year, Number(month) - 1, Number(day)));
  const daysSinceMonday = (asUtc.getUTCDay() + 6) % 7; // getUTCDay: Sun=0..Sat=6 -> Mon=0
  asUtc.setUTCDate(asUtc.getUTCDate() - daysSinceMonday);
  return new Intl.DateTimeFormat("en-CA", { timeZone: "UTC" }).format(asUtc);
}
