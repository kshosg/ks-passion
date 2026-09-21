import Link from "next/link";
import type { Metadata } from "next";
import { getAllBlogPosts } from "@/lib/content";
import LevelBadge from "@/components/LevelBadge";

export const metadata: Metadata = {
  title: "Blog",
  description: "Life-feedback essays applying the Diamond Sutra to everyday situations.",
};

export default function BlogIndex() {
  const posts = getAllBlogPosts();
  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-serif text-3xl font-bold">The life-feedback blog</h1>
        <p className="mt-2 text-ink/70 max-w-2xl">
          Real situations, run through the lens of the Diamond Sutra. New posts every week.
        </p>
      </div>
      <ul className="space-y-6">
        {posts.map((post) => (
          <li key={post.slug} className="border-b border-ink/10 pb-6">
            <LevelBadge level={post.level} />
            <h2 className="mt-2 font-serif text-xl font-bold">
              <Link href={`/blog/${post.slug}`} className="hover:text-jade">{post.title}</Link>
            </h2>
            <p className="mt-1 text-sm text-ink/50">{post.date}</p>
            <p className="mt-2 text-ink/70">{post.excerpt}</p>
          </li>
        ))}
        {posts.length === 0 && <p className="text-ink/50">First post coming soon.</p>}
      </ul>
    </div>
  );
}
