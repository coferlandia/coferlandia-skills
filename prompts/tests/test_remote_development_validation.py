import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPT = ROOT / "prompts" / "chat-coder.md"
PROTOCOL = ROOT / "_protocol" / "delivery" / "DEVELOPMENT_VALIDATION.md"
READY = ROOT / "_protocol" / "delivery" / "READY_FOR_CI.md"


class ChatCoderRemoteDevelopmentTests(unittest.TestCase):
    def test_chat_coder_prefers_local_then_repository_owned_remote_development(self):
        text = PROMPT.read_text(encoding="utf-8")
        self.assertIn("### Execution backends for Development validation", text)
        self.assertIn("Prefer direct execution", text)
        self.assertIn(".coferlandia/development/validation.json", text)
        self.assertIn("coferlandia-ci-adapter", text)
        self.assertIn("delegate only the minimum bootstrap", text)
        self.assertIn("exact current PR head SHA", text)
        self.assertIn("current Development contract fingerprint", text)
        self.assertIn("Block only when no authorized Development execution backend", text)

    def test_remote_development_never_substitutes_for_qualification(self):
        text = PROMPT.read_text(encoding="utf-8")
        protocol = PROTOCOL.read_text(encoding="utf-8")
        ready = READY.read_text(encoding="utf-8")
        self.assertIn("Remote Development validation is still **Development**", text)
        self.assertIn("must not invoke or reuse Qualification merely as a workaround", text)
        self.assertIn("It is **not Qualification**", protocol)
        self.assertIn("Remote Development validation", ready)
        self.assertIn("exact Candidate SHA", ready)

    def test_remote_workflow_authority_is_fail_closed(self):
        protocol = PROTOCOL.read_text(encoding="utf-8")
        for token in (
            "github.event.pull_request.head.sha",
            "contents: read",
            "never writes the durable `READY_FOR_CI`",
            "stale",
            "superseded",
            "Development fingerprint",
            "self-hosted runners",
        ):
            self.assertIn(token, protocol)


if __name__ == "__main__":
    unittest.main()
