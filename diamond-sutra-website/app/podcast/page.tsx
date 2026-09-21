import Link from "next/link";
import type { Metadata } from "next";
import { getAllPodcastEpisodes } from "@/lib/content";
import LevelBadge from "@/components/LevelBadge";

export const metadata: Metadata = {
  title: "Podcast",
  description: "Weekly podcast on the Diamond Sutra, for beginner through advanced listeners.",
};

export default function PodcastIndex() {
  const episodes = getAllPodcastEpisodes();
  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-serif text-3xl font-bold">The podcast</h1>
        <p className="mt-2 text-ink/70 max-w-2xl">New episode every week. Subscribe on your favourite player, or just read the notes here.</p>
      </div>
      <ul className="space-y-6">
        {episodes.map((ep) => (
          <li key={ep.slug} className="border-b border-ink/10 pb-6">
            <LevelBadge level={ep.level} />
            <h2 className="mt-2 font-serif text-xl font-bold">
              <Link href={`/podcast/${ep.slug}`} className="hover:text-jade">{ep.title}</Link>
            </h2>
            <p className="mt-1 text-sm text-ink/50">{ep.date}{ep.durationMinutes ? ` · ${ep.durationMinutes} min` : ""}</p>
            <p className="mt-2 text-ink/70">{ep.summary}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
