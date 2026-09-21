import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { getAllWebinars, getWebinar } from "@/lib/content";
import LevelBadge from "@/components/LevelBadge";

export function generateStaticParams() {
  return getAllWebinars().map((w) => ({ slug: w.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const w = getWebinar(slug);
  return { title: w?.title ?? "Webinar not found", description: w?.description };
}

export default async function WebinarPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const w = getWebinar(slug);
  if (!w) notFound();

  return (
    <article className="space-y-6 max-w-2xl mx-auto">
      <div>
        <LevelBadge level={w.level} />
        <h1 className="mt-3 font-serif text-3xl font-bold">{w.title}</h1>
        <p className="mt-1 text-sm text-ink/50">{w.date} · {w.status === "upcoming" ? "Upcoming" : "Recorded"}</p>
      </div>
      <p className="text-ink/80">{w.description}</p>
      {w.status === "upcoming" && w.registerUrl && (
        <Link href={w.registerUrl} className="inline-block rounded-full bg-jade px-6 py-3 font-semibold text-paper hover:bg-jade/90">
          Register free
        </Link>
      )}
      {w.status === "past" && w.recordingUrl && (
        <Link href={w.recordingUrl} className="inline-block rounded-full border border-ink/20 px-6 py-3 font-semibold text-ink hover:border-jade hover:text-jade">
          Watch / listen to the recording
        </Link>
      )}
    </article>
  );
}
