import type { MetadataRoute } from "next";
import { getAllBlogPosts, getAllPodcastEpisodes, getAllWebinars } from "@/lib/content";
import { getAllStories } from "@/lib/stories";
import { LEVELS } from "@/lib/types";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://example.com";

export default function sitemap(): MetadataRoute.Sitemap {
  const staticRoutes = ["", "/learn", "/stories", "/blog", "/podcast", "/webinars", "/resources", "/subscribe"].map(
    (route) => ({ url: `${SITE_URL}${route}`, lastModified: new Date() })
  );

  const levelRoutes = LEVELS.map((l) => ({ url: `${SITE_URL}/learn/${l.id}`, lastModified: new Date() }));
  const blogRoutes = getAllBlogPosts().map((p) => ({ url: `${SITE_URL}/blog/${p.slug}`, lastModified: p.date }));
  const podcastRoutes = getAllPodcastEpisodes().map((e) => ({ url: `${SITE_URL}/podcast/${e.slug}`, lastModified: e.date }));
  const webinarRoutes = getAllWebinars().map((w) => ({ url: `${SITE_URL}/webinars/${w.slug}`, lastModified: w.date }));
  const storyRoutes = getAllStories().map((s) => ({ url: `${SITE_URL}/stories/${s.id}`, lastModified: new Date() }));

  return [...staticRoutes, ...levelRoutes, ...blogRoutes, ...podcastRoutes, ...webinarRoutes, ...storyRoutes];
}
