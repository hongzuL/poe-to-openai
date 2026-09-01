import asyncio
import json
import os
import sys
import unittest

sys.path.insert(0, ".")

from api import poe_api


class AnnounceOnlyPatternTests(unittest.TestCase):
    def test_positive_cases(self):
        cases = [
            "I am about to read the paper-writing-prompt.md file in the workspace to analyze its structure and content.",
            "I'm about to read the paper-writing-prompt.md file.",
            "I’m about to check the source code.",
            "I am going to check the configuration file.",
            "I will execute the bash command now.",
            "I'll search for the function definition.",
            "Let me check the logs first.",
            "我将读取 paper-writing-prompt.md 文件。",
            "我会先查看当前的日志配置。",
            "我先看一下这个文件。",
            "我来执行这条命令。",
            "接下来我将开始重构代码。",
            "首先我需要检查现有的实现。",
            "Now I will fetch the project dependencies.",
            "First I will read the file.",
            "I intend to examine the implementation.",
            "I plan to inspect the logs.",
        ]
        for text in cases:
            with self.subTest(text=text):
                self.assertTrue(
                    poe_api._is_announce_only(text),
                    f"Expected announce-only detection for: {text!r}",
                )

    def test_negative_cases_and_false_positives(self):
        cases = [
            "This will work as expected.",
            "I am ill today, so I cannot attend.",
            "Let me know if you need more details about the setup.",
            "Please tell me what you think.",
            "The file contains: I will write a test.",
            "All tasks are complete.",
            "Here is the final summary of the changes.",
        ]
        for text in cases:
            with self.subTest(text=text):
                self.assertFalse(
                    poe_api._is_announce_only(text),
                    f"Did not expect announce-only detection for: {text!r}",
                )

    def test_length_boundary(self):
        long_announcement = "I am about to check " + ("x" * 650)
        self.assertFalse(poe_api._is_announce_only(long_announcement))


class TransientErrorClassificationTests(unittest.TestCase):
    def test_timeout_error_without_message_is_transient(self):
        err = asyncio.TimeoutError()
        self.assertTrue(poe_api._is_transient_error(err))

    def test_custom_timeout_error_is_transient(self):
        err = poe_api.PoeStreamTimeoutError("idle", 30)
        self.assertTrue(poe_api._is_transient_error(err))

    def test_tool_rejection_detection(self):
        cases = [
            RuntimeError("Bot does not support tools"),
            Exception("Tool calls are not supported for this bot"),
            Exception("Invalid tool definition: this bot does not accept tools"),
        ]
        for err in cases:
            with self.subTest(err=err):
                self.assertTrue(poe_api._is_tool_rejection(err))

    def test_general_error_not_tool_rejection(self):
        self.assertFalse(poe_api._is_tool_rejection(ValueError("bad value")))
        self.assertFalse(poe_api._is_tool_rejection(RuntimeError("Rate limit exceeded")))


class EmulatedEventsStateMachineTests(unittest.IsolatedAsyncioTestCase):
    async def test_announce_then_tool_call_auto_continues(self):
        original_native = poe_api._native_stream

        calls = 0

        async def fake_native(api_key, messages, model, tools=None, tool_choice=None,
                             temperature=None, stop_sequences=None, session=None):
            nonlocal calls
            calls += 1
            if calls == 1:
                yield {
                    "kind": "text",
                    "text": "I am about to read the paper-writing-prompt.md file in the workspace to analyze its structure and content.",
                }
            else:
                yield {
                    "kind": "text",
                    "text": "<<<tool_call>>>\nname: Read\narg:file_path: paper-writing-prompt.md\n<<<end>>>",
                }

        poe_api._native_stream = fake_native
        try:
            events = []
            async for event in poe_api._emulated_events(
                api_key="test",
                messages=[{"role": "user", "content": "read the file"}],
                model="gemini-3.7-flash",
                tools=[{"type": "function", "function": {"name": "Read"}}],
                tool_choice="auto",
                temperature=None,
                stop_sequences=None,
                session=None,
            ):
                events.append(event)

            self.assertEqual(calls, 2)
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["kind"], "tool_calls")
            self.assertEqual(events[0]["tool_calls"][0]["function"]["name"], "Read")
        finally:
            poe_api._native_stream = original_native

    async def test_exhausted_announcements_raise_error(self):
        original_native = poe_api._native_stream

        async def fake_native(*args, **kwargs):
            yield {
                "kind": "text",
                "text": "I will read the file.",
            }

        poe_api._native_stream = fake_native
        try:
            with self.assertRaises(poe_api.IncompleteToolActionError):
                async for _ in poe_api._emulated_events(
                    api_key="test",
                    messages=[{"role": "user", "content": "read the file"}],
                    model="gemini-3.7-flash",
                    tools=[{"type": "function", "function": {"name": "Read"}}],
                    tool_choice="auto",
                    temperature=None,
                    stop_sequences=None,
                    session=None,
                ):
                    pass
        finally:
            poe_api._native_stream = original_native


if __name__ == "__main__":
    unittest.main()
