"use client";

import { useEffect, useState } from "react";

export default function ReflectionPrompt({ prompt, storageKey }: { prompt: string; storageKey?: string }) {
  const key = storageKey ?? `reflection:${prompt.slice(0, 40)}`;
  const [value, setValue] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    try {
      const existing = window.localStorage.getItem(key);
      if (existing) setValue(existing);
    } catch {
      // localStorage unavailable — reflection just won't persist
    }
  }, [key]);

  function save() {
    try {
      window.localStorage.setItem(key, value);
      setSaved(true);
      setTimeout(() => setSaved(false), 1500);
    } catch {
      // ignore — nothing to persist to
    }
  }

  return (
    <aside className="rounded-xl border border-gold/40 bg-gold/5 p-5">
      <p className="text-sm font-semibold uppercase tracking-wide text-gold">Pause and reflect</p>
      <p className="mt-2 text-ink/80">{prompt}</p>
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Write a few words — this stays on your device, only visible to you."
        className="mt-3 w-full rounded-lg border border-ink/15 bg-white p-3 text-sm text-ink focus:border-jade focus:outline-none"
        rows={3}
      />
      <button
        onClick={save}
        className="mt-2 rounded-full bg-jade px-4 py-1.5 text-sm font-semibold text-paper hover:bg-jade/90"
      >
        {saved ? "Saved" : "Keep this note"}
      </button>
    </aside>
  );
}
