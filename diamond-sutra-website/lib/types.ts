export type Level = "beginner" | "intermediate" | "advanced";

export const LEVELS: { id: Level; label: string; blurb: string }[] = [
  {
    id: "beginner",
    label: "Beginner",
    blurb: "New to the Diamond Sutra, or to Buddhism entirely. Start here.",
  },
  {
    id: "intermediate",
    label: "Intermediate",
    blurb: "You know the core ideas — non-attachment, emptiness, impermanence — and want to apply them.",
  },
  {
    id: "advanced",
    label: "Advanced",
    blurb: "You've studied the sutra closely and want depth, commentary, and harder questions.",
  },
];

export interface BlogPost {
  slug: string;
  title: string;
  date: string;
  level: Level;
  excerpt: string;
  contentHtml: string;
}

export interface PodcastEpisode {
  slug: string;
  title: string;
  date: string;
  level: Level;
  summary: string;
  audioUrl?: string;
  durationMinutes?: number;
}

export interface Webinar {
  slug: string;
  title: string;
  date: string;
  level: Level;
  description: string;
  status: "upcoming" | "past";
  registerUrl?: string;
  recordingUrl?: string;
}

export interface AffiliateBook {
  title: string;
  author: string;
  level: Level;
  blurb: string;
  amazonUrl: string;
}

export interface AffiliateOffer {
  name: string;
  network: "clickbank" | "other";
  level: Level;
  blurb: string;
  url: string;
}
