# The Diamond Sutra Project

A Next.js site for awareness, content, and education around the Diamond Sutra — for
beginner, intermediate, and advanced audiences, Buddhist or not. Free to use, with a paid
tier ready to switch on.

## What's built

- **`/learn`** — beginner/intermediate/advanced hub, auto-aggregating every piece of tagged content.
- **`/blog`** — weekly "life-feedback" essays. Markdown files with frontmatter in `content/blog/*.md`.
- **`/podcast`** — episode list + detail pages. Data in `content/podcast/episodes.json`.
- **`/webinars`** — upcoming/past webinars. Data in `content/webinars/webinars.json`.
- **`/stories`** — choose-your-own-adventure engine. Each story is a JSON file of branching nodes
  in `content/stories/*.json`, with reflection prompts, secret choices, and multiple endings
  that connect back to the sutra's teaching. Seven roles are seeded (CEO townhall, manager/
  executive, parent/teen, aging parent/child, grandparent/grandchild, boss/employee SME,
  husband/wife) — three fully branching, four with a shorter two-ending arc. Add more by
  dropping in a new JSON file; no code changes needed.
- **`/resources`** — Amazon Associates book list + Clickbank/other affiliate offers, both tagged
  by level, with an affiliate disclosure.
- **`/subscribe`** — free email capture + a paid tier ready for Stripe.
- **`/admin/analytics`** — owner-only traffic & subscriber overview (see below).

## Adding weekly content

- New blog post: add `content/blog/your-slug.md` with frontmatter (`title`, `date`, `level`,
  `excerpt`) — it appears on `/blog` and its level page automatically.
- New podcast episode: add an object to `content/podcast/episodes.json`.
- New webinar: add an object to `content/webinars/webinars.json` (`status: "upcoming"` or `"past"`).
- New story: add `content/stories/your-story.json` following the shape of the existing files
  (`startNode`, a `nodes` map, `choices` with `secret: true` for hidden-path options, and
  `ending: true` + `insight` on terminal nodes).

## Environment variables

Copy `.env.example` to `.env.local` and fill in what you have. Everything works without any of
these set — email signups are just logged instead of sent to a mailing list, and the paid tier
shows a "coming soon" message instead of opening checkout.

| Variable | Purpose | Free option |
|---|---|---|
| `NEXT_PUBLIC_SITE_URL` | Used in the sitemap/robots | — |
| `ADMIN_KEY` | Gates `/admin/analytics?key=...` | — |
| `BUTTONDOWN_API_KEY` | Free-tier email capture | [Buttondown](https://buttondown.email) free plan (up to 100 subscribers) |
| `STRIPE_SECRET_KEY` / `STRIPE_PRICE_ID` | Paid-tier checkout | Stripe has no monthly fee, only per-transaction fees |
| `NEXT_PUBLIC_PLAUSIBLE_DOMAIN` | Optional traffic dashboard embed | Plausible (paid, cheap) or self-hosted |

Visitor/page-view analytics (`/admin/analytics`) use **Vercel Analytics**, already wired into
`app/layout.tsx` — it's free on Vercel's Hobby plan with zero extra setup once deployed there.

## Amazon & affiliate links

`content/books.json` and `content/affiliates.json` ship with placeholder links (a dummy
`tag=YOUR-AMAZON-TAG-20` and Clickbank placeholders). Before launch:

1. Join the [Amazon Associates](https://affiliate-program.amazon.com/) program (free) and swap
   `YOUR-AMAZON-TAG-20` for your real tracking ID, and double-check each ASIN is correct.
2. Join [Clickbank](https://www.clickbank.com/) (free) or another affiliate network, pick offers
   relevant to meditation/mindfulness, and replace the placeholder entries.

## Local development

```bash
npm install
npm run dev
```

## Deploying (free to start)

This is a standard Next.js app — deploys to [Vercel](https://vercel.com)'s free Hobby tier with
zero config (`vercel.com/new`, point it at this repo). Set the environment variables above in
the Vercel project settings as you turn on each feature (mailing list, then Stripe, then a
custom analytics dashboard).

## Roadmap notes for the paid tier

The subscribe page and `/api/checkout` are wired for Stripe Checkout in **subscription** mode.
Once you create a Stripe product/price for the paid tier and set `STRIPE_SECRET_KEY` +
`STRIPE_PRICE_ID`, "Upgrade to paid" will open a real Stripe Checkout session. Gating the actual
paid content (deeper study guides, ad-free audio) isn't built yet — the simplest next step is a
webhook at `/api/stripe/webhook` that marks a subscriber's email as paid in whatever
subscriber store you choose, then checking that flag on the pages you want to restrict.
