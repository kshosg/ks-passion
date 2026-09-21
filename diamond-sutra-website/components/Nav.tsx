import Link from "next/link";

const links = [
  { href: "/learn", label: "Learn" },
  { href: "/stories", label: "Stories" },
  { href: "/blog", label: "Blog" },
  { href: "/podcast", label: "Podcast" },
  { href: "/webinars", label: "Webinars" },
  { href: "/resources", label: "Resources" },
];

export default function Nav() {
  return (
    <header className="border-b border-ink/10 bg-paper/95 backdrop-blur sticky top-0 z-40">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
        <Link href="/" className="font-serif text-lg font-bold tracking-tight text-ink">
          The Diamond Sutra <span className="text-gold">Project</span>
        </Link>
        <nav className="hidden gap-6 text-sm font-medium text-ink/80 md:flex">
          {links.map((l) => (
            <Link key={l.href} href={l.href} className="hover:text-jade transition-colors">
              {l.label}
            </Link>
          ))}
        </nav>
        <Link
          href="/subscribe"
          className="rounded-full bg-jade px-4 py-2 text-sm font-semibold text-paper hover:bg-jade/90 transition-colors"
        >
          Subscribe
        </Link>
      </div>
      <nav className="flex gap-4 overflow-x-auto px-4 pb-3 text-sm font-medium text-ink/80 md:hidden">
        {links.map((l) => (
          <Link key={l.href} href={l.href} className="whitespace-nowrap hover:text-jade">
            {l.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
