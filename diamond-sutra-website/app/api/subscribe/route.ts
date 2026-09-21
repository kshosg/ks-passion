import { NextRequest, NextResponse } from "next/server";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function POST(req: NextRequest) {
  let body: { email?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid request body" }, { status: 400 });
  }

  const email = body.email?.trim();
  if (!email || !EMAIL_RE.test(email)) {
    return NextResponse.json({ error: "Enter a valid email address" }, { status: 400 });
  }

  const buttondownKey = process.env.BUTTONDOWN_API_KEY;

  if (buttondownKey) {
    const res = await fetch("https://api.buttondown.email/v1/subscribers", {
      method: "POST",
      headers: {
        Authorization: `Token ${buttondownKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email }),
    });

    if (res.ok || res.status === 409) {
      return NextResponse.json({ message: "You're on the list — check your inbox to confirm." });
    }

    const errorBody = await res.text();
    console.error("Buttondown subscribe failed", res.status, errorBody);
    return NextResponse.json({ error: "Could not subscribe right now. Please try again shortly." }, { status: 502 });
  }

  // No email service provider configured yet — log it so the owner doesn't lose the signup,
  // and set BUTTONDOWN_API_KEY (or swap in your own ESP integration here) to go live.
  console.log("New subscriber (no ESP configured):", email);
  return NextResponse.json({
    message: "Thanks! Email signup isn't fully wired up to a mailing list yet — you've been logged and won't be lost.",
  });
}
