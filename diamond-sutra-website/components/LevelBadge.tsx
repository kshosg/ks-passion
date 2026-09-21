import type { Level } from "@/lib/types";

const STYLES: Record<Level, string> = {
  beginner: "bg-jade/10 text-jade",
  intermediate: "bg-gold/10 text-gold",
  advanced: "bg-rose/10 text-rose",
};

const LABELS: Record<Level, string> = {
  beginner: "Beginner",
  intermediate: "Intermediate",
  advanced: "Advanced",
};

export default function LevelBadge({ level }: { level: Level }) {
  return (
    <span className={`inline-block rounded-full px-2.5 py-1 text-xs font-semibold ${STYLES[level]}`}>
      {LABELS[level]}
    </span>
  );
}
