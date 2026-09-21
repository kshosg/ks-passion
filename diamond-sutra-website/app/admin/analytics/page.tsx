import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Traffic & Subscribers",
  robots: { index: false, follow: false },
};

export default async function AdminAnalyticsPage({
  searchParams,
}: {
  searchParams: Promise<{ key?: string }>;
}) {
  const { key } = await searchParams;
  const adminKey = process.env.ADMIN_KEY;
  const authorized = Boolean(adminKey) && key === adminKey;
  const plausibleDomain = process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN;

  if (!authorized) {
    return (
      <div className="max-w-xl mx-auto space-y-4">
        <h1 className="font-serif text-2xl font-bold">Traffic &amp; subscribers</h1>
        <p className="text-ink/70">
          This page is restricted to the site owner. Set an <code>ADMIN_KEY</code> environment
          variable, then visit this page with <code>?key=your-admin-key</code> to view it.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h1 className="font-serif text-2xl font-bold">Traffic &amp; subscribers</h1>

      <section className="rounded-xl border border-ink/10 bg-white/60 p-5 space-y-2">
        <h2 className="font-semibold text-ink">Visitors &amp; page views</h2>
        <p className="text-sm text-ink/70">
          This site ships with <strong>Vercel Analytics</strong> already wired in (see{" "}
          <code>app/layout.tsx</code>) — it&apos;s free on Vercel&apos;s Hobby plan with no extra
          setup once deployed. View live numbers in your Vercel dashboard under
          Project → Analytics.
        </p>
        {plausibleDomain ? (
          <div className="mt-3 overflow-hidden rounded-lg border border-ink/10">
            <iframe
              title="Plausible analytics"
              src={`https://plausible.io/share/${plausibleDomain}?embed=true&theme=light`}
              className="w-full h-[600px]"
            />
          </div>
        ) : (
          <p className="text-sm text-ink/50">
            Optional: add a free/low-cost <strong>Plausible</strong> site, set{" "}
            <code>NEXT_PUBLIC_PLAUSIBLE_DOMAIN</code>, and a shared dashboard will embed here too.
          </p>
        )}
      </section>

      <section className="rounded-xl border border-ink/10 bg-white/60 p-5 space-y-2">
        <h2 className="font-semibold text-ink">Subscribers</h2>
        <p className="text-sm text-ink/70">
          Free-tier signups go to your ESP once <code>BUTTONDOWN_API_KEY</code> is set (see{" "}
          <code>app/api/subscribe/route.ts</code>) — view your subscriber count and list in your
          Buttondown dashboard. Paid subscribers appear in your Stripe dashboard once{" "}
          <code>STRIPE_SECRET_KEY</code> and <code>STRIPE_PRICE_ID</code> are set.
        </p>
      </section>
    </div>
  );
}
