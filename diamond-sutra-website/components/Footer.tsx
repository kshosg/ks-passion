import Link from "next/link";

export default function Footer() {
  return (
    <footer className="mt-24 border-t border-ink/10 bg-ink text-paper/80">
      <div className="mx-auto max-w-5xl px-4 py-12 grid gap-8 sm:grid-cols-3">
        <div>
          <p className="font-serif text-lg font-bold text-paper">The Diamond Sutra Project</p>
          <p className="mt-2 text-sm">
            Practical study of the Diamond Sutra for beginners through advanced practitioners —
            not only for Buddhists.
          </p>
        </div>
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-paper">Explore</p>
          <ul className="mt-2 space-y-1 text-sm">
            <li><Link href="/learn" className="hover:text-gold">Learn by level</Link></li>
            <li><Link href="/stories" className="hover:text-gold">Choose-your-own-adventure</Link></li>
            <li><Link href="/resources" className="hover:text-gold">Books &amp; resources</Link></li>
          </ul>
        </div>
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-paper">Stay in touch</p>
          <p className="mt-2 text-sm">New content weekly — podcast, webinar, and a life-feedback blog post.</p>
          <Link
            href="/subscribe"
            className="mt-3 inline-block rounded-full bg-gold px-4 py-2 text-sm font-semibold text-ink"
          >
            Join free
          </Link>
        </div>
      </div>
      <div className="border-t border-paper/10 px-4 py-4 text-center text-xs text-paper/50">
        Some links are affiliate links (Amazon Associates and other partners). If you buy through
        them, this site may earn a small commission at no extra cost to you. See our{" "}
        <Link href="/resources" className="underline">disclosure</Link>.
      </div>
    </footer>
  );
}
