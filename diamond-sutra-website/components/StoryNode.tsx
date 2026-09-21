import Link from "next/link";
import type { Story, StoryNode as StoryNodeType } from "@/lib/stories";
import ReflectionPrompt from "@/components/ReflectionPrompt";

export default function StoryNode({
  story,
  node,
  nodeId,
}: {
  story: Story;
  node: StoryNodeType;
  nodeId: string;
}) {
  return (
    <div className="space-y-6">
      <p className="text-lg leading-relaxed text-ink/90">{node.text}</p>

      {node.reflection && !node.ending && (
        <ReflectionPrompt
          storageKey={`story:${story.id}:${nodeId}`}
          prompt={node.reflection}
        />
      )}

      {node.ending ? (
        <div className="space-y-4">
          <div className="rounded-xl border border-jade/30 bg-jade/5 p-5">
            <p className="text-sm font-semibold uppercase tracking-wide text-jade">
              Where the Diamond Sutra connects
            </p>
            <p className="mt-2 text-ink/80">{node.insight}</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link
              href={`/stories/${story.id}`}
              className="rounded-full bg-jade px-5 py-2.5 text-sm font-semibold text-paper hover:bg-jade/90"
            >
              Play this story again
            </Link>
            <Link
              href="/stories"
              className="rounded-full border border-ink/20 px-5 py-2.5 text-sm font-semibold text-ink hover:border-jade hover:text-jade"
            >
              Try a different story
            </Link>
          </div>
        </div>
      ) : (
        <div className="space-y-2">
          {node.choices?.map((choice, i) => (
            <Link
              key={i}
              href={`/stories/${story.id}?node=${encodeURIComponent(choice.next)}`}
              className={
                choice.secret
                  ? "block text-sm text-ink/40 hover:text-ink/70 italic pl-1 py-1 transition-colors"
                  : "block rounded-lg border border-ink/15 bg-white/70 px-4 py-3 font-medium text-ink hover:border-jade hover:bg-jade/5 transition"
              }
            >
              {choice.label}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
