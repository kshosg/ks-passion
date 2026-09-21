import type { Metadata } from "next";
import { getAffiliateBooks, getAffiliateOffers } from "@/lib/content";
import { LEVELS } from "@/lib/types";
import LevelBadge from "@/components/LevelBadge";
import AffiliateDisclosure from "@/components/AffiliateDisclosure";

export const metadata: Metadata = {
  title: "Books & Resources",
  description: "Recommended Diamond Sutra books and practice resources, organized by level.",
};

export default function ResourcesPage() {
  const books = getAffiliateBooks();
  const offers = getAffiliateOffers();

  return (
    <div className="space-y-10">
      <div>
        <h1 className="font-serif text-3xl font-bold">Books &amp; resources</h1>
        <p className="mt-2 text-ink/70 max-w-2xl">
          The translations and companion books we actually reference on the podcast and blog,
          plus a few practice resources — organized by level.
        </p>
      </div>

      <AffiliateDisclosure />

      <section>
        <h2 className="font-serif text-xl font-bold">Books</h2>
        <div className="mt-4 space-y-8">
          {LEVELS.map((level) => {
            const items = books.filter((b) => b.level === level.id);
            if (items.length === 0) return null;
            return (
              <div key={level.id}>
                <LevelBadge level={level.id} />
                <ul className="mt-3 space-y-3">
                  {items.map((book) => (
                    <li key={book.title} className="rounded-lg border border-ink/10 bg-white/60 p-4">
                      <a
                        href={book.amazonUrl}
                        target="_blank"
                        rel="noopener noreferrer sponsored"
                        className="font-semibold text-ink hover:text-jade"
                      >
                        {book.title}
                      </a>
                      <p className="text-sm text-ink/50">{book.author}</p>
                      <p className="mt-1 text-sm text-ink/70">{book.blurb}</p>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      </section>

      <section>
        <h2 className="font-serif text-xl font-bold">Other resources</h2>
        <ul className="mt-4 space-y-3">
          {offers.map((offer) => (
            <li key={offer.name} className="rounded-lg border border-ink/10 bg-white/60 p-4">
              <a
                href={offer.url}
                target="_blank"
                rel="noopener noreferrer sponsored"
                className="font-semibold text-ink hover:text-jade"
              >
                {offer.name}
              </a>
              <p className="mt-1 text-sm text-ink/70">{offer.blurb}</p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
