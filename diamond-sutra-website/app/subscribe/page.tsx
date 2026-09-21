import type { Metadata } from "next";
import SubscribeForm from "@/components/SubscribeForm";
import UpgradeButton from "@/components/UpgradeButton";

export const metadata: Metadata = {
  title: "Subscribe",
  description: "Join free, or upgrade for deeper study material and ad-free listening.",
};

export default function SubscribePage() {
  return (
    <div className="space-y-10 max-w-2xl mx-auto">
      <div className="text-center space-y-3">
        <h1 className="font-serif text-3xl font-bold">Join the Diamond Sutra Project</h1>
        <p className="text-ink/70">Everything core stays free. Upgrade any time to support the work.</p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <div className="rounded-2xl border border-ink/10 bg-white/60 p-6 space-y-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-jade">Free</p>
            <p className="mt-1 font-serif text-2xl font-bold">$0</p>
          </div>
          <ul className="space-y-2 text-sm text-ink/70">
            <li>Weekly podcast episode</li>
            <li>Weekly life-feedback blog post</li>
            <li>All choose-your-own-adventure stories</li>
            <li>Live webinars + recordings</li>
          </ul>
          <SubscribeForm />
        </div>

        <div className="rounded-2xl border border-gold/40 bg-gold/5 p-6 space-y-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-gold">Paid — coming soon</p>
            <p className="mt-1 font-serif text-2xl font-bold">A few dollars / month</p>
          </div>
          <ul className="space-y-2 text-sm text-ink/70">
            <li>Everything in Free</li>
            <li>Ad-free podcast listening</li>
            <li>Deeper study guides per episode</li>
            <li>Monthly live Q&amp;A with direct access</li>
          </ul>
          <UpgradeButton />
        </div>
      </div>
    </div>
  );
}
