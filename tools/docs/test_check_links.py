"""Behavior checks for link publication, Markdown syntax, and frozen scope."""

from collections import defaultdict
from pathlib import Path, PurePosixPath
import unittest

import check_links as checker


class TreeFixture:
    def __init__(self, root, texts, extra=()):
        self.root = Path(root)
        self.texts = texts
        self.files = set(texts) | set(extra)
        self.dirs = {''}
        for p in self.files:
            self.dirs.update(str(x) for x in PurePosixPath(p).parents if str(x) != '.')
        self.folded = defaultdict(list)
        for p in self.files | self.dirs:
            self.folded[p.casefold()].append(p)
        self.anchors = {p: checker.heading_anchors(t) for p, t in texts.items()}
        self.ref = None
        self.commit = 'a' * 40
        self.new_files = []


class PublicationLinks(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2]
        self.policy = {'repository': 'cenyongdong/See-You-In-WiFi',
                       'repository_aliases': ['cenyongdong/FPGACompetitionProject'],
                       'default_branch': 'master', 'protected_files': []}

    def status(self, text, target='Docs/中文 文档.md', target_text='# 当前标题\n'):
        tree = TreeFixture(self.root, {'README.md': text, target: target_text})
        return checker.scan(tree, self.policy)

    def test_chinese_percent_encoded_space_and_escaped_parentheses(self):
        summary, _issues, _ = self.status('[中文](Docs/%E4%B8%AD%E6%96%87%20%E6%96%87%E6%A1%A3.md#当前标题)')
        self.assertEqual(summary['maintainable_errors'], 0)
        summary, _, _ = self.status('[x](Docs/a\\(b\\).md)', 'Docs/a(b).md')
        self.assertEqual(summary['maintainable_errors'], 0)

    def test_target_case_is_exact_and_old_anchor_is_rejected(self):
        summary, issues, _ = self.status('[错大小写](docs/中文%20文档.md)\n[旧标题](Docs/中文%20文档.md#旧标题)')
        self.assertEqual(summary['maintainable_errors'], 2)
        self.assertEqual({x['status'] for x in issues}, {'case_mismatch', 'invalid_anchor'})

    def test_repeated_and_code_heading_ids(self):
        self.assertEqual(checker.heading_anchors('# `API` 配置\n# 当前标题\n# 当前标题\n'),
                         {'api-配置', '当前标题', '当前标题-1'})

    def test_unpublished_local_file_never_passes(self):
        # This file exists, but is intentionally omitted from the fixture's Git file set.
        summary, issues, _ = self.status('[本机文件](tools/docs/test_check_links.py)')
        self.assertEqual(summary['maintainable_errors'], 1)
        self.assertEqual(issues[0]['status'], 'local_only_not_published')

    def test_published_evidence_copy_and_missing_image(self):
        tree = TreeFixture(self.root, {'README.md': '![好](evidence/图.png)\n![坏](missing.png)'},
                           ['evidence/图.png'])
        summary, issues, _ = checker.scan(tree, self.policy)
        self.assertEqual(summary['maintainable_errors'], 1)
        self.assertEqual(issues[0]['target'], 'missing.png')

    def test_machine_paths_and_file_uri_are_not_web_links(self):
        summary, issues, _ = self.status('[a](D:/FPGACompetitionProject/README.md)\n[b](file:///C:/a.md)')
        self.assertEqual(summary['maintainable_errors'], 2)
        self.assertTrue(all(x['status'] == 'local_machine_path' for x in issues))

    def test_reference_image_reference_html_and_same_repository_url(self):
        text = ('[文档][guide]\n![图片][pic]\n<a href="Docs/a.md#标题">a</a>\n'
                '<https://github.com/cenyongdong/FPGACompetitionProject/blob/master/Docs/a.md>\n'
                '[guide]: Docs/a.md "说明"\n[pic]: assets/p.png\n')
        tree = TreeFixture(self.root, {'README.md': text, 'Docs/a.md': '# 标题'}, ['assets/p.png'])
        summary, issues, records = checker.scan(tree, self.policy)
        self.assertEqual(summary['maintainable_errors'], 0, issues)
        self.assertEqual(len(records), 4)
        self.assertEqual({x['syntax'] for x in records}, {'reference', 'image_reference', 'html', 'autolink'})

    def test_fences_inline_code_and_comments_are_not_checked(self):
        text = ('```md\n[not a link](missing1)\n```\n'
                '``[literal](missing2)``\n<!-- [hidden](missing3) -->\n'
                '~~~text\n![hidden](missing4)\n~~~\n[visible](missing5)')
        links = checker.extract_links(text)
        self.assertEqual([x.target for x in links], ['missing5'])
        self.assertEqual(links[0].line, 9)

    def test_nested_badge_destinations_preserve_offsets(self):
        text = '[![徽章](assets/badge.png)](README.md)'
        links = checker.extract_links(text)
        self.assertEqual(len(links), 2)
        for link in links:
            self.assertEqual(text[link.destination_start:link.destination_end], link.target)

    def test_explicit_frozen_list_does_not_exempt_new_history_files(self):
        self.policy['protected_files'] = ['history/old.md']
        tree = TreeFixture(self.root, {'history/old.md': '[old](missing)',
                                           'history/new.md': '[new](missing)'})
        summary, _, _ = checker.scan(tree, self.policy)
        self.assertEqual(summary['maintainable_errors'], 1)
        self.assertEqual(summary['protected_history_gaps'], 1)

    def test_external_links_are_counted_without_fetching(self):
        summary, issues, _ = self.status('[external](https://example.invalid/doc)')
        self.assertEqual(summary['status_counts']['external'], 1)
        self.assertFalse(issues)

    def test_diagnostic_output_cannot_overwrite_inputs_or_git_metadata(self):
        tree = TreeFixture(self.root, {}, ['results/summary.json'])
        with self.assertRaises(ValueError):
            checker.validate_output_directory(tree, self.root / 'results')
        with self.assertRaises(ValueError):
            checker.validate_output_directory(tree, self.root / '.git')


if __name__ == '__main__':
    unittest.main()
