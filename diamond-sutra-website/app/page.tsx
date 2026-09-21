import Link from "next/link";
import { LEVELS } from "@/lib/types";
import { getAllBlogPosts, getAllPodcastEpisodes, getAllWebinars } from "@/lib/content";
import { getAllStories } from "@/lib/stories";
import LevelBadge from "@/components/LevelBadge";

export default function HomePage() {
  const posts = getAllBlogPosts().slice(0, 3);
  const episodes = getAllPodcastEpisodes().slice(0, 2);
  const webinars = getAllWebinars().filter((w) => w.status === "upcoming").slice(0, 2);
  const stories = getAllStories().slice(0, 3);

  return (
    <div className="space-y-20">
      <section className="text-center space-y-6 py-8">
        <p className="text-sm font-semibold uppercase tracking-widest text-gold">
          Awareness · Content · Education
        </p>
        <h1 className="font-serif text-4xl sm:text-5xl font-bold leading-tight text-ink">
          The Diamond Sutra, made practical —
          <br className="hidden sm:block" /> whoever you are.
        </h1>
        <p className="mx-auto max-w-2xl text-lg text-ink/70">
          You don&apos;t need to be Buddhist to use the Diamond Sutra&apos;s teaching on letting go
          of fixed views. This is a home for beginners, intermediate students, and advanced
          practitioners alike — through weekly podcasts, webinars, a life-feedback blog, and
          interactive stories that put the teaching to work in ordinary conversations.
        </p>
        <div className="flex flex-wrap justify-center gap-3 pt-2">
          <Link href="/learn" className="rounded-full bg-jade px-6 py-3 font-semibold text-paper hover:bg-jade/90">
            Find your starting point
          </Link>
          <Link href="/stories" className="rounded-full border border-ink/20 px-6 py-3 font-semibold text-ink hover:border-jade hover:text-jade">
            Try a choose-your-own-adventure
          </Link>
        </div>
      </section>

      <section>
        <h2 className="font-serif text-2xl font-bold">Start where you are</h2>
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          {LEVELS.map((level) => (
            <Link
              key={level.id}
              href={`/learn/${level.id}`}
              className="rounded-xl border border-ink/10 bg-white/60 p-5 hover:border-jade hover:shadow-sm transition"
            >
              <LevelBadge level={level.id} />
              <p className="mt-3 font-semibold text-ink">{level.label}</p>
              <p className="mt-1 text-sm text-ink/60">{level.blurb}</p>
            </Link>
          ))}
        </div>
      </section>

      {stories.length > 0 && (
        <section>
          <div className="flex items-baseline justify-between">
            <h2 className="font-serif text-2xl font-bold">Live the teaching: choose your own adventure</h2>
            <Link href="/stories" className="text-sm font-semibold text-jade hover:underline">See all stories →</Link>
          </div>
          <p className="mt-2 text-ink/70">
            Step into a real conversation — a townhall Q&amp;A, a hard talk with your teenager, a
            negotiation with your boss — and see how the sutra&apos;s teaching on non-attachment
            changes what you&apos;d say next. Some choices lead to endings you won&apos;t expect.
          </p>
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            {stories.map((s) => (
              <Link key={s.id} href={`/stories/${s.id}`} className="rounded-xl border border-ink/10 bg-white/60 p-5 hover:border-jade hover:shadow-sm transition">
                <LevelBadge level={s.level} />
                <p className="mt-3 font-semibold text-ink">{s.title}</p>
                <p className="mt-1 text-sm text-ink/60">{s.role}</p>
              </Link>
            ))}
          </div>
        </section>
      )}

      <section className="grid gap-10 sm:grid-cols-2">
        <div>
          <div className="flex items-baseline justify-between">
            <h2 className="font-serif text-2xl font-bold">From the blog</h2>
            <Link href="/blog" className="text-sm font-semibold text-jade hover:underline">All posts →</Link>
          </div>
          <ul className="mt-4 space-y-4">
            {posts.map((p) => (
              <li key={p.slug}>
                <Link href={`/blog/${p.slug}`} className="font-semibold text-ink hover:text-jade">{p.title}</Link>
                <p className="text-sm text-ink/60">{p.excerpt}</p>
              </li>
            ))}
            {posts.length === 0 && <p className="text-sm text-ink/50">New posts coming soon.</p>}
          </ul>
        </div>
        <div>
          <div className="flex items-baseline justify-between">
            <h2 className="font-serif text-2xl font-bold">Podcast &amp; webinars</h2>
            <Link href="/podcast" className="text-sm font-semibold text-jade hover:underline">All episodes →</Link>
          </div>
          <ul className="mt-4 space-y-4">
            {episodes.map((e) => (
              <li key={e.slug}>
                <Link href={`/podcast/${e.slug}`} className="font-semibold text-ink hover:text-jade">{e.title}</Link>
                <p className="text-sm text-ink/60">{e.summary}</p>
              </li>
            ))}
            {webinars.map((w) => (
              <li key={w.slug}>
                <Link href={`/webinars/${w.slug}`} className="font-semibold text-ink hover:text-jade">
                  Webinar: {w.title}
                </Link>
                <p className="text-sm text-ink/60">{w.date}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="rounded-2xl bg-jade text-paper p-8 text-center space-y-3">
        <h2 className="font-serif text-2xl font-bold">Free to start. Support the work when you&apos;re ready.</h2>
        <p className="text-paper/80 max-w-xl mx-auto">
          Every core teaching stays free — weekly podcast, blog, webinars, and stories. A paid tier
          is coming for deeper study material, ad-free listening, and direct Q&amp;A.
        </p>
        <Link href="/subscribe" className="inline-block rounded-full bg-gold px-6 py-3 font-semibold text-ink">
          Join the free list
        </Link>
      </section>
    </div>
  );
}
