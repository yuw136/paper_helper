import { FileDirectory } from '../components/FileDirectory';
import { FileNode } from '../types';

interface ApiFile {
  id: string;
  title: string;
  topic: string;
  path: string;
}

export const transformFileTree = (files: ApiFile[]) => {
  //prefix trie basically
  const root: FileNode = {
    id: 'root',
    name: 'root',
    type: 'folder',
    path: '',
    children: new Map<string, FileNode>(),
  };
  //return this lookupTable for "findNodeById"
  const lookupTable = new Map<string, FileNode>();
  lookupTable.set('root', root);

  files.forEach((file) => {
    let currentNode = root;

    const pathParts = file.path.split('/');
    length = pathParts.length;
    if (length === 0 || pathParts[0] === '') {
      return;
    }

    pathParts.forEach((part, index) => {
      const exists = currentNode.children?.has(part);
      if (!exists) {
        const id =
          index === length - 1
            ? file.id
            : pathParts.slice(0, index + 1).join('-');
        const name = part;
        const type = index === length - 1 ? 'file' : 'folder';
        const path = currentNode.path + '/' + part;
        const parentId = currentNode.id;
        const children =
          index === length - 1 ? null : new Map<string, FileNode>();
        const newNode: FileNode = {
          id: id,
          name: name,
          type: type,
          path: path,
          parentId: parentId,
          children: children,
        };
        currentNode.children?.set(part, newNode);
        currentNode = newNode;
        lookupTable.set(currentNode.id, currentNode);
      } else {
        currentNode = currentNode.children.get(part);
      }
    });
  });

  return { root, lookupTable };
};
