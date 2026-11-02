#!/usr/bin/env python3
"""Check published repository links without changing documents or Git state.

Examples:
  python tools/docs/check_links.py --worktree
  python tools/docs/check_links.py --ref HEAD --output-dir .local/doc-links

Worktree mode reads tracked files plus explicitly named --include-new files.
It is a publication preflight, not evidence that changes have reached GitHub.
External websites are counted, not fetched. Requires Python 3.9+ and Git.
"""

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass, asdict
import html
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


@dataclass
class Link:
    target: str
    label: str
    syntax: str
    line: int
    start: int
    end: int
    destination_start: int
    destination_end: int


def mask_code(text):
    """Keep offsets while masking fenced/inline code and HTML comments."""
    chars = list(text)
    offset = 0
    fence = None
    for line in text.splitlines(keepends=True):
        opening = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if fence:
            masked = True
            if re.match(r'^ {0,3}' + re.escape(fence[0]) + '{' + str(fence[1]) + r',}\s*$', line):
                fence = None
        elif opening:
            fence = (opening[1][0], len(opening[1]))
            masked = True
        else:
            masked = False
        if masked:
            for n in range(offset, offset + len(line)):
                if chars[n] not in '\r\n':
                    chars[n] = ' '
        offset += len(line)
    masked = ''.join(chars)
    for m in re.finditer(r'<!--.*?(?:-->|\Z)', masked, re.S):
        for n in range(m.start(), m.end()):
            if chars[n] not in '\r\n':
                chars[n] = ' '
    masked = ''.join(chars)
    cursor = 0
    while cursor < len(masked):
        opening = re.search(r'(?<![\\`])(`+)(?!`)', masked[cursor:])
        if not opening:
            break
        start = cursor + opening.start()
        after = cursor + opening.end()
        run = opening[1]
        closing = re.search(r'(?<!`)' + re.escape(run) + r'(?!`)', masked[after:])
        if closing:
            end = after + closing.end()
            for n in range(start, end):
                if chars[n] not in '\r\n':
                    chars[n] = ' '
            cursor = end
        else:
            cursor = after
    return ''.join(chars)


def destination_span(text, start, end):
    while start < end and text[start].isspace():
        start += 1
    if start < end and text[start] == '<':
        close = text.find('>', start + 1, end)
        if close >= 0:
            return start + 1, close
    raw = text[start:end]
    title = re.search(r'\s+[\"\x27]', raw)
    if title:
        end = start + title.start()
    while end > start and text[end - 1].isspace():
        end -= 1
    return start, end


def extract_links(text):
    masked = mask_code(text)
    refs = {}
    for m in re.finditer(r'^ {0,3}\[([^\]\n]+)\]:[ \t]*(.+)$', masked, re.M):
        a, b = destination_span(text, m.start(2), m.end(2))
        refs[' '.join(m[1].split()).casefold()] = (a, b)
    links = []
    reference_ids = set()
    for m in re.finditer(r'(?<!\\)\[', masked):
        start = m.start()
        if start in reference_ids:
            continue
        j = start + 1
        depth = 1
        while j < len(masked) and depth:
            if masked[j] == '\\':
                j += 2
                continue
            if masked[j] == '[':
                depth += 1
            elif masked[j] == ']':
                depth -= 1
            j += 1
        if depth:
            continue
        label = text[start + 1:j - 1]
        image = start > 0 and masked[start - 1] == '!'
        full_start = start - int(image)
        if j < len(masked) and masked[j] == '(':
            k = j + 1
            angle = False
            depth = 1
            while k < len(masked):
                char = masked[k]
                if char == '\\':
                    k += 2
                    continue
                if char == '<' and k == j + 1:
                    angle = True
                elif char == '>' and angle:
                    angle = False
                elif not angle:
                    if char == '(':
                        depth += 1
                    elif char == ')':
                        depth -= 1
                        if not depth:
                            break
                k += 1
            if not depth:
                a, b = destination_span(text, j + 1, k)
                links.append(Link(text[a:b], label, 'image' if image else 'inline',
                                  text.count('\n', 0, full_start) + 1, full_start, k + 1, a, b))
        else:
            key = ' '.join(label.split()).casefold()
            end = j
            if j < len(masked) and masked[j] == '[':
                k = masked.find(']', j + 1)
                if k < 0:
                    continue
                key = ' '.join((text[j + 1:k] or label).split()).casefold()
                end = k + 1
                if key in refs:
                    reference_ids.add(j)
            elif j < len(masked) and masked[j] == ':':
                continue
            if key in refs:
                a, b = refs[key]
                links.append(Link(text[a:b], label, 'image_reference' if image else 'reference',
                                  text.count('\n', 0, full_start) + 1, full_start, end, a, b))
    for m in re.finditer(r'<(?:a|img)\b[^>]*?\b(?:href|src)\s*=\s*([\"\x27])(.+?)\1[^>]*>', masked, re.I | re.S):
        a, b = m.span(2)
        links.append(Link(text[a:b], '', 'html', text.count('\n', 0, m.start()) + 1,
                          m.start(), m.end(), a, b))
    for m in re.finditer(r'<(https?://[^<>\s]+)>', masked):
        a, b = m.span(1)
        links.append(Link(text[a:b], text[a:b], 'autolink', text.count('\n', 0, m.start()) + 1,
                          m.start(), m.end(), a, b))
    return sorted(links, key=lambda x: (x.start, x.end))


def heading_anchors(text):
    visible = mask_code(text)
    anchors = set(re.findall(r'<a\b[^>]*\b(?:id|name)=[\"\x27]([^\"\x27]+)', visible, re.I))
    counts = Counter()
    lines = visible.splitlines()
    originals = text.splitlines()
    for n, line in enumerate(lines):
        match = re.match(r'^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$', line)
        if match:
            # Inline code contributes its text to the heading ID.
            title = re.sub(r'^ {0,3}#{1,6}\s+', '', originals[n]).strip()
            title = re.sub(r'\s+#+\s*$', '', title)
        elif n + 1 < len(lines) and line.strip() and re.fullmatch(r' {0,3}(?:=+|-+)\s*', lines[n + 1]):
            title = originals[n].strip()
        else:
            continue
        title = re.sub(r'!?\[([^\]]+)\]\([^)]*\)', r'\1', title)
        title = html.unescape(re.sub(r'<[^>]*>', '', title)).replace('`', '').strip().lower()
        slug = re.sub(r'[^\w\-\s]', '', title).replace(' ', '-')
        index = counts[slug]
        counts[slug] += 1
        anchors.add(slug + ('-' + str(index) if index else ''))
    return anchors


class GitTree:
    def __init__(self, root, git='git', ref=None, include_new=()):
        self.root = Path(root).resolve()
        self.git = git
        self.ref = ref
        self.commit = self.run('rev-parse', ref or 'HEAD').decode().strip()
        self.new_files = sorted(set(include_new))
        self.texts = {}
        self.objects = {}
        if ref:
            for record in self.run('ls-tree', '-rz', '--full-tree', ref).split(b'\0'):
                if not record:
                    continue
                meta, name = record.split(b'\t', 1)
                _mode, kind, oid = meta.decode().split()
                self.objects[name.decode('utf-8')] = (kind, oid)
            self.files = set(self.objects)
            docs = [p for p in self.files if p.lower().endswith('.md') and self.objects[p][0] == 'blob']
            oids = sorted({self.objects[p][1] for p in docs})
            stream = BytesIO(self.run('cat-file', '--batch', input=''.join(x + '\n' for x in oids).encode()))
            blobs = {}
            for oid in oids:
                header = stream.readline().decode().split()
                if header[:2] != [oid, 'blob']:
                    raise ValueError('Unexpected Git object: ' + repr(header))
                blobs[oid] = stream.read(int(header[2]))
                if stream.read(1) != b'\n':
                    raise ValueError('Truncated Git object')
            self.texts = {p: blobs[self.objects[p][1]].decode('utf-8-sig') for p in docs}
        else:
            tracked = {x.decode('utf-8') for x in self.run('ls-files', '-z', '--cached').split(b'\0') if x}
            self.files = {p for p in tracked if (self.root / p).exists()}
            for path in self.new_files:
                parts = PurePosixPath(path)
                if parts.is_absolute() or '..' in parts.parts or '\\' in path:
                    raise ValueError('--include-new requires repository-relative POSIX paths: ' + path)
                if not (self.root / path).is_file():
                    raise ValueError('Planned new file is absent: ' + path)
                ignored = subprocess.run([git, 'check-ignore', '-q', '--', path], cwd=self.root)
                if ignored.returncode == 0:
                    raise ValueError('Planned new file is still Git-ignored: ' + path)
                if ignored.returncode != 1:
                    raise ValueError('git check-ignore failed: ' + path)
                self.files.add(path)
            for path in self.files:
                if path.lower().endswith('.md'):
                    self.texts[path] = (self.root / path).read_bytes().decode('utf-8-sig')
        self.dirs = {''}
        for path in self.files:
            self.dirs.update(str(p) for p in PurePosixPath(path).parents if str(p) != '.')
        self.folded = defaultdict(list)
        for path in sorted(self.files | self.dirs):
            self.folded[path.casefold()].append(path)
        self.anchors = {p: heading_anchors(t) for p, t in self.texts.items()}

    def run(self, *args, input=None):
        process = subprocess.run([self.git, *args], cwd=self.root, input=input, capture_output=True)
        if process.returncode:
            raise ValueError('Git failed: ' + process.stderr.decode('utf-8', 'replace').strip())
        return process.stdout


def check_link(tree, policy, source, link):
    target = html.unescape(link.target)
    target = re.sub(r'\\([ ()])', r'\1', target)
    record = {'source': source, 'line': link.line, 'target': link.target, 'syntax': link.syntax,
              'protected': source in policy['protected_files']}
    if re.match(r'^[A-Za-z]:[/\\]', target) or target.lower().startswith('file:') or target.startswith('\\\\'):
        return dict(record, status='local_machine_path', resolved_path=target)
    url = urlsplit(target)
    fragment = unquote(url.fragment)
    if url.scheme or url.netloc:
        parts = unquote(url.path).strip('/').split('/')
        own_names = {policy['repository'].lower(), *(x.lower() for x in policy.get('repository_aliases', []))}
        own = len(parts) >= 2 and '/'.join(parts[:2]).lower() in own_names
        host = url.netloc.lower()
        if own and host in ('github.com', 'www.github.com') and len(parts) >= 4 and parts[2] in ('blob', 'tree', 'raw'):
            rest = '/'.join(parts[3:])
        elif own and host == 'raw.githubusercontent.com' and len(parts) >= 4:
            rest = '/'.join(parts[2:])
        else:
            return dict(record, status='external', resolved_path=target)
        refs = {policy['default_branch'], tree.commit}
        if tree.ref:
            refs.add(tree.ref)
        prefix = next((r + '/' for r in sorted(refs, key=len, reverse=True) if rest.startswith(r + '/')), None)
        if prefix is None:
            return dict(record, status='other_git_ref', resolved_path=target)
        path = rest[len(prefix):].rstrip('/')
    else:
        path = unquote(url.path)
        if path.startswith('/'):
            return dict(record, status='github_site_root_path', resolved_path=path)
        path = posixpath.normpath(posixpath.join(posixpath.dirname(source), path)) if path else source
        path = path.rstrip('/')
    record['resolved_path'] = path
    if path in tree.files or path in tree.dirs:
        if fragment and path.lower().endswith('.md') and not re.fullmatch(r'L\d+(?:-L?\d+)?', fragment):
            fragment = fragment.removeprefix('user-content-')
            if fragment not in tree.anchors.get(path, set()):
                return dict(record, status='invalid_anchor', fragment=fragment)
        return dict(record, status='ok')
    if path.casefold() in tree.folded:
        return dict(record, status='case_mismatch', case_candidates=tree.folded[path.casefold()])
    # Local existence is diagnostic only; it never makes a link pass.
    inside = path != '..' and not path.startswith('../')
    local = inside and (tree.root / path).exists()
    return dict(record, status='local_only_not_published' if local else 'target_absent', local_exists=local)


def scan(tree, policy):
    records = [check_link(tree, policy, p, link)
               for p, text in sorted(tree.texts.items()) for link in extract_links(text)]
    issues = [x for x in records if x['status'] not in ('ok', 'external')]
    errors = [x for x in issues if not x['protected']]
    history = [x for x in issues if x['protected']]
    summary = {
        'mode': 'git_ref' if tree.ref else 'worktree_preflight', 'commit': tree.commit,
        'ref': tree.ref, 'files': len(tree.files), 'markdown_documents': len(tree.texts),
        'links': len(records), 'status_counts': dict(Counter(x['status'] for x in records)),
        'maintainable_errors': len(errors), 'maintainable_source_files': len({x['source'] for x in errors}),
        'protected_history_gaps': len(history), 'protected_source_files': len({x['source'] for x in history}),
        'planned_new_files': tree.new_files,
    }
    return summary, issues, records


def validate_output_directory(tree, output):
    """Diagnostic output must not overwrite checked inputs or Git metadata."""
    output = Path(output).resolve()
    try:
        relative = output.relative_to(tree.root).as_posix()
    except ValueError:
        return
    if relative == '.git' or relative.startswith('.git/'):
        raise ValueError('Diagnostic output cannot be written inside .git')
    for name in ('summary.json', 'issues.json', 'issues.csv'):
        target = posixpath.normpath(posixpath.join(relative, name))
        if target in tree.files:
            raise ValueError('Diagnostic output would overwrite a checked input: ' + target)


def write_results(output, summary, issues):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for name, value in [('summary.json', summary), ('issues.json', issues)]:
        (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with (output / 'issues.csv').open('w', encoding='utf-8-sig', newline='') as handle:
        fields = ['source', 'line', 'target', 'resolved_path', 'status', 'protected', 'fragment', 'local_exists']
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(issues)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--worktree', action='store_true', help='Check tracked working files (default)')
    mode.add_argument('--ref', help='Check the exact file tree and text of a Git commit/ref')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--git', default='git', help='Git executable, if not on PATH')
    parser.add_argument('--include-new', action='append', default=[], metavar='PATH',
                        help='Explicit untracked file intended for publication (repeatable; worktree only)')
    parser.add_argument('--output-dir', type=Path, help='Write JSON and CSV diagnostics here')
    args = parser.parse_args(argv)
    if args.ref and args.include_new:
        parser.error('--include-new cannot be used with --ref')
    try:
        policy_path = args.root / 'tools/docs/link_policy.json'
        policy = json.loads(policy_path.read_text(encoding='utf-8'))
        tree = GitTree(args.root, args.git, args.ref, args.include_new)
        summary, issues, _records = scan(tree, policy)
        if args.output_dir:
            validate_output_directory(tree, args.output_dir)
            write_results(args.output_dir, summary, issues)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 1 if summary['maintainable_errors'] else 0
    except (OSError, ValueError, KeyError) as error:
        print('Link check failed: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
