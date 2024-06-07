from src.entity.Change import TreeDifferenceStructureChange
from src.entity.Comparator import Comparator
from src.shared.helpers import find_by_identifier
from bs4 import BeautifulSoup


class TreeComparator(Comparator):

    def check_similarity(self, identifier: str) -> float:
        self.changes_css_paths = []
        r1 = find_by_identifier(self.snap1.static_requests, identifier)
        r2 = find_by_identifier(self.snap2.static_requests, identifier)
        if r1 and r2 is None:
            return

        tree1 = self.parse_html_to_tree(r1.content)
        tree2 = self.parse_html_to_tree(r2.content)
        similarity = self.tree_difference_similarity(tree1, tree2)
        if similarity < 0.99:
            r1.changes.append(TreeDifferenceStructureChange(1 - similarity, '\n' + '\n'.join(self.changes_css_paths)))
        print("HTML page similarity:", similarity)
        return 1

    def parse_html_to_tree(self, html):
        soup = BeautifulSoup(html, 'html.parser').find('body')
        return self.parse_soup_to_tree(soup)

    def parse_soup_to_tree(self, soup):
        if not soup.contents:
            return None

        root = TreeNode(soup.name, soup)
        for child in soup.contents:
            if child.name:
                root.children.append(self.parse_soup_to_tree(child))
        return root

    def tree_difference_similarity(self, root1, root2):
        if not root1 and not root2:
            return 1.0
        elif not root1 or not root2:
            return 0.0

        max_diff = max(count_nodes(root1), count_nodes(root2))
        diff_count = self.count_differences(root1, root2)
        similarity = 1 - (diff_count / max_diff)
        return similarity

    def count_differences(self, node1, node2):
        if not node1 and not node2:
            return 0
        elif not node1 or not node2:
            if node1:
                self.changes_css_paths.append('node not found in snapshot 2:' + self.get_css_path(node1.soup_node))
            if node2:
                self.changes_css_paths.append('node not found in snapshot 1:' + self.get_css_path(node2.soup_node))
            return 1

        diff_count = 0

        if node1.tag != node2.tag:
            diff_count += 1
            self.changes_css_paths.append('different tag: ' + self.get_css_path(node1.soup_node))

        num_children1 = len(node1.children)
        num_children2 = len(node2.children)

        min_children = min(num_children1, num_children2)

        for i in range(min_children):
            diff_count += self.count_differences(node1.children[i], node2.children[i])

        diff_count += abs(num_children1 - num_children2)
        if abs(num_children1 - num_children2) > 0:
            self.changes_css_paths.append(f'children count diff {abs(num_children1 - num_children2)}: ' + self.get_css_path(node1.soup_node))

        return diff_count

    def get_element(self, node):
        if 'id' in node.attrs:
            return '#' + node.attrs['id']
        if 'class' in node.attrs:
            return '.' + '.'.join(node.attrs['class'])
        else:
            return node.name

    def get_css_path(self, node):
        path = [self.get_element(node)]
        for parent in node.parents:
            if parent.name == 'body':
                break
            path.insert(0, self.get_element(parent))
        return ' > '.join(path)


class TreeNode:
    def __init__(self, tag, soup_node):
        self.tag = tag
        self.soup_node = soup_node
        self.children = []


def count_nodes(root):
    if not root:
        return 0
    count = 1
    print(root.children)
    for child in root.children:
        count += count_nodes(child)
    return count
