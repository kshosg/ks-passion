import Link from "next/link";
import type { Metadata } from "next";
import { getAllStories } from "@/lib/stories";
import LevelBadge from "@/components/LevelBadge";

export const metadata: Metadata = {
  title: "Choose Your Own Adventure",
  description: "Interactive stories that put the Diamond Sutra's teachings to work in real conversations.",
};

export default function StoriesIndex() {
  const stories = getAllStories();
  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-serif text-3xl font-bold">Choose your own adventure</h1>
        <p className="mt-2 text-ink/70 max-w-2xl">
          Pick a role. Live a real conversation. Your choices lead to different endings — and some
          of them aren&apos;t the obvious ones. Along the way you&apos;ll be asked to pause and
          reflect before you choose, the same way you would before you speak in real life.
        </p>
      </div>
      <div className="grid gap-5 sm:grid-cols-2">
        {stories.map((s) => (
          <Link
            key={s.id}
            href={`/stories/${s.id}`}
            className="rounded-xl border border-ink/10 bg-white/60 p-6 hover:border-jade hover:shadow-sm transition flex flex-col gap-2"
          >
            <LevelBadge level={s.level} />
            <p className="font-serif text-xl font-bold">{s.title}</p>
            <p className="text-sm font-semibold text-jade">{s.role}</p>
            <p className="mt-1 text-sm text-ink/60">{s.teaser}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
