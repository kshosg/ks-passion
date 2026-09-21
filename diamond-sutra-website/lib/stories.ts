import fs from "fs";
import path from "path";
import type { Level } from "./types";

export interface StoryChoice {
  label: string;
  next: string;
  secret?: boolean;
}

export interface StoryNode {
  text: string;
  reflection?: string;
  insight?: string;
  ending?: boolean;
  choices?: StoryChoice[];
}

export interface Story {
  id: string;
  title: string;
  role: string;
  level: Level;
  teaser: string;
  concept: string;
  startNode: string;
  nodes: Record<string, StoryNode>;
}

const STORIES_DIR = path.join(process.cwd(), "content", "stories");

export function getAllStories(): Story[] {
  if (!fs.existsSync(STORIES_DIR)) return [];
  const files = fs.readdirSync(STORIES_DIR).filter((f) => f.endsWith(".json"));
  return files
    .map((file) => JSON.parse(fs.readFileSync(path.join(STORIES_DIR, file), "utf8")) as Story)
    .sort((a, b) => a.title.localeCompare(b.title));
}

export function getStory(id: string): Story | undefined {
  const filePath = path.join(STORIES_DIR, `${id}.json`);
  if (!fs.existsSync(filePath)) return undefined;
  return JSON.parse(fs.readFileSync(filePath, "utf8")) as Story;
}
