import { FileNode } from '../types';

const YEAR_PATTERN = /^(19|20)\d{2}$/;

function parseYear(value: string): number | null {
  const trimmed = value.trim();
  if (!YEAR_PATTERN.test(trimmed)) {
    return null;
  }

  return Number(trimmed);
}

export function compareFileNodes(a: FileNode, b: FileNode): number {
  const yearA = parseYear(a.name);
  const yearB = parseYear(b.name);

  if (yearA !== null && yearB !== null && yearA !== yearB) {
    // Newer year first, e.g. 2025 before 2024
    return yearB - yearA;
  }

  if (yearA !== null && yearB === null) {
    return -1;
  }

  if (yearA === null && yearB !== null) {
    return 1;
  }

  if (a.type !== b.type) {
    return a.type === 'folder' ? -1 : 1;
  }

  return a.name.localeCompare(b.name, undefined, {
    numeric: true,
    sensitivity: 'base',
  });
}

export function sortFileNodes(nodes: FileNode[]): FileNode[] {
  return [...nodes].sort(compareFileNodes);
}
