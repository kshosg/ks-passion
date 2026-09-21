import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";

export async function POST(req: NextRequest) {
  const secretKey = process.env.STRIPE_SECRET_KEY;
  const priceId = process.env.STRIPE_PRICE_ID;

  if (!secretKey || !priceId) {
    return NextResponse.json(
      {
        error:
          "The paid tier isn't live yet — Stripe isn't configured. Set STRIPE_SECRET_KEY and STRIPE_PRICE_ID to enable checkout.",
      },
      { status: 503 }
    );
  }

  const stripe = new Stripe(secretKey);
  const origin = req.headers.get("origin") ?? new URL(req.url).origin;

  try {
    const session = await stripe.checkout.sessions.create({
      mode: "subscription",
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${origin}/subscribe?checkout=success`,
      cancel_url: `${origin}/subscribe?checkout=cancelled`,
    });

    return NextResponse.json({ url: session.url });
  } catch (err) {
    console.error("Stripe checkout session failed", err);
    return NextResponse.json({ error: "Could not start checkout. Please try again shortly." }, { status: 502 });
  }
}
