from pathlib import Path

publication = Path('skills/meta/coferlandia-ci-adapter/scripts/coferlandia_ci_adapter_cli/publication.py')
text = publication.read_text(encoding='utf-8')
text = text.replace(
    "matches = re.findall(r'```json\\s*(.+?)\\s*```', tail, re.S)",
    "matches = re.findall(r'```json\\\\s*(.+?)\\\\s*```', tail, re.S)",
    1,
)
text = text.replace(
    "r'[0-9]+\\.[0-9]+\\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?'",
    "r'[0-9]+\\\\.[0-9]+\\\\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\\\\+[0-9A-Za-z.-]+)?'",
    1,
)
publication.write_text(text, encoding='utf-8')

test = Path('skills/meta/coferlandia-ci-adapter/tests/test_publication_no_gh.py')
text = test.read_text(encoding='utf-8')
text = text.replace(
    '        self.assertIn("comment.get(\'id\', 0) < current_id", workflow)\n',
    '        self.assertIn("comment_id >= current_id", workflow)\n'
    '        self.assertIn("permission_for(author) not in {\'admin\', \'maintain\'}", workflow)\n'
    '        self.assertIn("retry requested but no prior authorized valid publication request exists", workflow)\n'
    '        self.assertIn("request_comment_id={request_comment_id}", workflow)\n',
    1,
)
text = text.replace(
    '        self.assertIn("retry requested but no prior publication request exists", workflow)\n',
    '',
)
test.write_text(text, encoding='utf-8')
