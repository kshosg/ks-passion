import Link from "next/link";
import type { Metadata } from "next";
import { LEVELS } from "@/lib/types";
import LevelBadge from "@/components/LevelBadge";

export const metadata: Metadata = {
  title: "Learn the Diamond Sutra",
  description: "Find your starting point — beginner, intermediate, or advanced.",
};

export default function LearnHub() {
  return (
    <div className="space-y-10">
      <div className="space-y-3">
        <h1 className="font-serif text-3xl font-bold">Where should you start?</h1>
        <p className="text-ink/70 max-w-2xl">
          The Diamond Sutra rewards re-reading at every stage of practice. Pick the level that
          matches you today — you can move between them any time, and every piece of content on
          this site is tagged so you always know what you&apos;re getting into.
        </p>
      </div>
      <div className="grid gap-6 sm:grid-cols-3">
        {LEVELS.map((level) => (
          <Link
            key={level.id}
            href={`/learn/${level.id}`}
            className="rounded-xl border border-ink/10 bg-white/60 p-6 hover:border-jade hover:shadow-sm transition flex flex-col gap-3"
          >
            <LevelBadge level={level.id} />
            <p className="font-serif text-xl font-bold">{level.label}</p>
            <p className="text-sm text-ink/60">{level.blurb}</p>
            <span className="mt-auto text-sm font-semibold text-jade">Browse {level.label.toLowerCase()} content →</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
