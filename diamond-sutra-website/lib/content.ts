import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { remark } from "remark";
import remarkHtml from "remark-html";
import type { AffiliateBook, AffiliateOffer, BlogPost, PodcastEpisode, Webinar } from "./types";

const CONTENT_DIR = path.join(process.cwd(), "content");

export function getAllBlogPosts(): BlogPost[] {
  const dir = path.join(CONTENT_DIR, "blog");
  if (!fs.existsSync(dir)) return [];
  const files = fs.readdirSync(dir).filter((f) => f.endsWith(".md"));
  const posts = files.map((file) => {
    const raw = fs.readFileSync(path.join(dir, file), "utf8");
    const { data, content } = matter(raw);
    const contentHtml = remark().use(remarkHtml).processSync(content).toString();
    return {
      slug: file.replace(/\.md$/, ""),
      title: data.title,
      date: data.date,
      level: data.level,
      excerpt: data.excerpt,
      contentHtml,
    } as BlogPost;
  });
  return posts.sort((a, b) => (a.date < b.date ? 1 : -1));
}

export function getBlogPost(slug: string): BlogPost | undefined {
  return getAllBlogPosts().find((p) => p.slug === slug);
}

function readJson<T>(file: string): T {
  const filePath = path.join(CONTENT_DIR, file);
  const raw = fs.readFileSync(filePath, "utf8");
  return JSON.parse(raw) as T;
}

export function getAllPodcastEpisodes(): PodcastEpisode[] {
  const data = readJson<PodcastEpisode[]>("podcast/episodes.json");
  return data.sort((a, b) => (a.date < b.date ? 1 : -1));
}

export function getPodcastEpisode(slug: string): PodcastEpisode | undefined {
  return getAllPodcastEpisodes().find((e) => e.slug === slug);
}

export function getAllWebinars(): Webinar[] {
  const data = readJson<Webinar[]>("webinars/webinars.json");
  return data.sort((a, b) => (a.date < b.date ? 1 : -1));
}

export function getWebinar(slug: string): Webinar | undefined {
  return getAllWebinars().find((w) => w.slug === slug);
}

export function getAffiliateBooks(): AffiliateBook[] {
  return readJson<AffiliateBook[]>("books.json");
}

export function getAffiliateOffers(): AffiliateOffer[] {
  return readJson<AffiliateOffer[]>("affiliates.json");
}
