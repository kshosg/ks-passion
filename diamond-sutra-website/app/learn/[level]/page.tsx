import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { LEVELS, type Level } from "@/lib/types";
import { getAllBlogPosts, getAllPodcastEpisodes, getAllWebinars } from "@/lib/content";
import { getAllStories } from "@/lib/stories";
import LevelBadge from "@/components/LevelBadge";

export function generateStaticParams() {
  return LEVELS.map((l) => ({ level: l.id }));
}

export async function generateMetadata({ params }: { params: Promise<{ level: string }> }): Promise<Metadata> {
  const { level: levelParam } = await params;
  const level = LEVELS.find((l) => l.id === levelParam);
  return { title: level ? `${level.label} content` : "Learn" };
}

export default async function LevelPage({ params }: { params: Promise<{ level: string }> }) {
  const { level: levelParam } = await params;
  const level = LEVELS.find((l) => l.id === levelParam);
  if (!level) notFound();
  const levelId = level.id as Level;

  const posts = getAllBlogPosts().filter((p) => p.level === levelId);
  const episodes = getAllPodcastEpisodes().filter((e) => e.level === levelId);
  const webinars = getAllWebinars().filter((w) => w.level === levelId);
  const stories = getAllStories().filter((s) => s.level === levelId);

  return (
    <div className="space-y-10">
      <div className="space-y-3">
        <LevelBadge level={levelId} />
        <h1 className="font-serif text-3xl font-bold">{level.label} track</h1>
        <p className="text-ink/70 max-w-2xl">{level.blurb}</p>
      </div>

      <Section title="Stories to try" items={stories.map((s) => ({ href: `/stories/${s.id}`, label: s.title, sub: s.role }))} empty="No stories at this level yet — check back weekly." />
      <Section title="Blog posts" items={posts.map((p) => ({ href: `/blog/${p.slug}`, label: p.title, sub: p.excerpt }))} empty="No posts at this level yet — check back weekly." />
      <Section title="Podcast episodes" items={episodes.map((e) => ({ href: `/podcast/${e.slug}`, label: e.title, sub: e.summary }))} empty="No episodes at this level yet — check back weekly." />
      <Section title="Webinars" items={webinars.map((w) => ({ href: `/webinars/${w.slug}`, label: w.title, sub: w.date }))} empty="No webinars at this level yet." />
    </div>
  );
}

function Section({
  title,
  items,
  empty,
}: {
  title: string;
  items: { href: string; label: string; sub?: string }[];
  empty: string;
}) {
  return (
    <section>
      <h2 className="font-serif text-xl font-bold">{title}</h2>
      {items.length === 0 ? (
        <p className="mt-2 text-sm text-ink/50">{empty}</p>
      ) : (
        <ul className="mt-4 space-y-3">
          {items.map((item) => (
            <li key={item.href}>
              <Link href={item.href} className="font-semibold text-ink hover:text-jade">
                {item.label}
              </Link>
              {item.sub && <p className="text-sm text-ink/60">{item.sub}</p>}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
