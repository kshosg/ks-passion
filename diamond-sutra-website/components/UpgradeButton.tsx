"use client";

import { useState } from "react";

export default function UpgradeButton() {
  const [status, setStatus] = useState<"idle" | "loading" | "error">("idle");
  const [message, setMessage] = useState("");

  async function handleClick() {
    setStatus("loading");
    try {
      const res = await fetch("/api/checkout", { method: "POST" });
      const data = await res.json();
      if (!res.ok || !data.url) throw new Error(data.error || "Checkout isn't available yet.");
      window.location.href = data.url;
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : "Checkout isn't available yet.");
    }
  }

  return (
    <div>
      <button
        onClick={handleClick}
        disabled={status === "loading"}
        className="rounded-full bg-gold px-6 py-3 font-semibold text-ink hover:bg-gold/90 disabled:opacity-60"
      >
        {status === "loading" ? "Starting checkout..." : "Upgrade to paid"}
      </button>
      {status === "error" && <p className="mt-2 text-sm text-rose max-w-sm">{message}</p>}
    </div>
  );
}
