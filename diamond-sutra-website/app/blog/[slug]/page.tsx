import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { getAllBlogPosts, getBlogPost } from "@/lib/content";
import LevelBadge from "@/components/LevelBadge";
import ReflectionPrompt from "@/components/ReflectionPrompt";

export function generateStaticParams() {
  return getAllBlogPosts().map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const post = getBlogPost(slug);
  return { title: post?.title ?? "Post not found", description: post?.excerpt };
}

export default async function BlogPostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = getBlogPost(slug);
  if (!post) notFound();

  return (
    <article className="space-y-6 max-w-2xl mx-auto">
      <div>
        <LevelBadge level={post.level} />
        <h1 className="mt-3 font-serif text-3xl font-bold">{post.title}</h1>
        <p className="mt-1 text-sm text-ink/50">{post.date}</p>
      </div>
      <div className="prose-diamond" dangerouslySetInnerHTML={{ __html: post.contentHtml }} />
      <ReflectionPrompt prompt="Before you move on: where in your own life this week could you hold your opinion a little less tightly?" />
    </article>
  );
}
