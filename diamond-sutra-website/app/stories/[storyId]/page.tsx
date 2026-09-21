import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { getAllStories, getStory } from "@/lib/stories";
import LevelBadge from "@/components/LevelBadge";
import StoryNode from "@/components/StoryNode";

export function generateStaticParams() {
  return getAllStories().map((s) => ({ storyId: s.id }));
}

export async function generateMetadata({ params }: { params: Promise<{ storyId: string }> }): Promise<Metadata> {
  const { storyId } = await params;
  const story = getStory(storyId);
  return { title: story?.title ?? "Story not found", description: story?.teaser };
}

export default async function StoryPage({
  params,
  searchParams,
}: {
  params: Promise<{ storyId: string }>;
  searchParams: Promise<{ node?: string }>;
}) {
  const { storyId } = await params;
  const { node: requestedNode } = await searchParams;
  const story = getStory(storyId);
  if (!story) notFound();

  const nodeId = requestedNode && story.nodes[requestedNode] ? requestedNode : story.startNode;
  const node = story.nodes[nodeId];
  if (!node) notFound();

  const isStart = nodeId === story.startNode;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <LevelBadge level={story.level} />
        <h1 className="mt-3 font-serif text-3xl font-bold">{story.title}</h1>
        <p className="mt-1 text-sm font-semibold text-jade">{story.role}</p>
        {isStart && <p className="mt-3 text-ink/70">{story.teaser}</p>}
      </div>

      <StoryNode story={story} node={node} nodeId={nodeId} />

      {!isStart && (
        <p className="text-xs text-ink/40">
          <Link href={`/stories/${story.id}`} className="hover:text-jade">Start this story over</Link>
        </p>
      )}
    </div>
  );
}
