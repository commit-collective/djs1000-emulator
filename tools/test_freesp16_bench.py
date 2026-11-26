#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""freesp16_bench.py picks its bench sources as freesp16's scripts/emulator-bench.sh does: a file stem takes every
BENCH of the matching files with no filter, a BENCH name takes the file that defines it and filters on that name, the
harness folder is never searched, and a name that matches nothing, or files without a BENCH, is refused.

    python tools/test_freesp16_bench.py       (no emulator, no freesp16 checkout)
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from freesp16_bench import sources_for  # noqa: E402


def tree(files):
    root = tempfile.mkdtemp()
    for path, text in files.items():
        full = os.path.join(root, "tests", "bench", *path.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)
    return root


class Sources(unittest.TestCase):
    def setUp(self):
        self.root = tree({
            "bench_mixer.cpp": "BENCH(mixer_strips, 45000) { }\nBENCH(mixer_meters, 9000) { }\n",
            "bench_mixer_sends.cpp": "  BENCH( mixer_sends , 12000) { }\n",
            "bench_voice.cpp": "BENCH(voice_one, 3000) { }\n",
            "bench_catch.cpp": "TEST_CASE(\"only Catch2\") { }\n",
            "harness/Bench.cpp": "BENCH(harness_only, 1) { }\n",
        })

    def test_a_stem_takes_every_matching_file_with_no_filter(self):
        self.assertEqual(sources_for(self.root, "mixer"),
                         (["tests/bench/bench_mixer.cpp", "tests/bench/bench_mixer_sends.cpp"], ""))
        self.assertEqual(sources_for(self.root, "bench_voice"), (["tests/bench/bench_voice.cpp"], ""))

    def test_a_bench_name_takes_its_file_and_filters_on_it(self):
        self.assertEqual(sources_for(self.root, "mixer_meters"), (["tests/bench/bench_mixer.cpp"], "mixer_meters"))
        self.assertEqual(sources_for(self.root, "voice_one"), (["tests/bench/bench_voice.cpp"], "voice_one"))

    def test_a_file_name_wins_over_a_bench_name(self):
        # bench_mixer_sends*.cpp matches first, as in freesp16's script: the whole file, no filter
        self.assertEqual(sources_for(self.root, "mixer_sends"), (["tests/bench/bench_mixer_sends.cpp"], ""))

    def test_the_harness_is_not_searched(self):
        with self.assertRaises(SystemExit):
            sources_for(self.root, "harness_only")

    def test_nothing_matching_or_no_bench_is_refused(self):
        with self.assertRaises(SystemExit):
            sources_for(self.root, "nothing_like_this")
        with self.assertRaises(SystemExit):
            sources_for(self.root, "catch")


if __name__ == "__main__":
    unittest.main()
