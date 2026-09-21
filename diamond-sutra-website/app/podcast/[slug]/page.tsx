import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { getAllPodcastEpisodes, getPodcastEpisode } from "@/lib/content";
import LevelBadge from "@/components/LevelBadge";
import ReflectionPrompt from "@/components/ReflectionPrompt";

export function generateStaticParams() {
  return getAllPodcastEpisodes().map((e) => ({ slug: e.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const ep = getPodcastEpisode(slug);
  return { title: ep?.title ?? "Episode not found", description: ep?.summary };
}

export default async function EpisodePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const ep = getPodcastEpisode(slug);
  if (!ep) notFound();

  return (
    <article className="space-y-6 max-w-2xl mx-auto">
      <div>
        <LevelBadge level={ep.level} />
        <h1 className="mt-3 font-serif text-3xl font-bold">{ep.title}</h1>
        <p className="mt-1 text-sm text-ink/50">
          {ep.date}{ep.durationMinutes ? ` · ${ep.durationMinutes} min` : ""}
        </p>
      </div>
      <p className="text-ink/80">{ep.summary}</p>
      <div className="rounded-xl border border-ink/10 bg-white/60 p-6 text-sm text-ink/60">
        {ep.audioUrl ? (
          <audio controls className="w-full">
            <source src={ep.audioUrl} />
          </audio>
        ) : (
          "Audio embed goes here once the episode is published to your podcast host (e.g. Spotify for Podcasters, Podbean)."
        )}
      </div>
      <ReflectionPrompt prompt={`After listening: what's one place this week you could apply "${ep.title}"?`} />
    </article>
  );
}
