import Link from "next/link";
import type { Metadata } from "next";
import { getAllWebinars } from "@/lib/content";
import LevelBadge from "@/components/LevelBadge";

export const metadata: Metadata = {
  title: "Webinars",
  description: "Live and recorded webinars on the Diamond Sutra.",
};

export default function WebinarsIndex() {
  const webinars = getAllWebinars();
  const upcoming = webinars.filter((w) => w.status === "upcoming");
  const past = webinars.filter((w) => w.status === "past");

  return (
    <div className="space-y-10">
      <div>
        <h1 className="font-serif text-3xl font-bold">Webinars</h1>
        <p className="mt-2 text-ink/70 max-w-2xl">Live sessions to go deeper and ask questions directly. Recordings stay up for subscribers.</p>
      </div>
      <Group title="Upcoming" items={upcoming} />
      <Group title="Past recordings" items={past} />
    </div>
  );
}

function Group({ title, items }: { title: string; items: ReturnType<typeof getAllWebinars> }) {
  return (
    <section>
      <h2 className="font-serif text-xl font-bold">{title}</h2>
      {items.length === 0 ? (
        <p className="mt-2 text-sm text-ink/50">Nothing here yet.</p>
      ) : (
        <ul className="mt-4 space-y-4">
          {items.map((w) => (
            <li key={w.slug} className="border-b border-ink/10 pb-4">
              <LevelBadge level={w.level} />
              <h3 className="mt-2 font-semibold text-ink">
                <Link href={`/webinars/${w.slug}`} className="hover:text-jade">{w.title}</Link>
              </h3>
              <p className="text-sm text-ink/50">{w.date}</p>
              <p className="mt-1 text-sm text-ink/70">{w.description}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
