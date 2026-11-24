"""Check guest process selection without starting firmware."""
import os
from pathlib import Path
import subprocess
import sys
import unittest
from uuid import uuid4


@unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux procfs")
class GuestProcesses(unittest.TestCase):
    def test_boot_menu_session_keeps_its_unit(self):
        helper = Path(__file__).resolve().parents[1] / "scripts/guest-pids.sh"
        tag = "test-" + uuid4().hex
        env = dict(os.environ, DJSDEV_TAG=tag, DJSDEV_UNIT="djs1000")
        cases = (
            ("sp16", ["-E", "DJSDEV_UNIT=sp16"], env),
            ("sp16", [], dict(env, DJSDEV_UNIT="sp16")),
            ("djs1000", [], env),
        )
        for expected, args, child_env in cases:
            with subprocess.Popen(
                [sys.executable, "-c", "import time; time.sleep(30)", "/opt/djsemu/init.sh", *args],
                env=child_env,
            ) as child:
                try:
                    output = subprocess.check_output(
                        ["bash", "-c", 'source "$1"; guest_init_unit', "test", str(helper)],
                        env=env,
                        text=True,
                    )
                    self.assertEqual(output.strip(), expected)
                finally:
                    child.terminate()

    def test_slot_and_exact_argument(self):
        helper = Path(__file__).resolve().parents[1] / "scripts/guest-pids.sh"
        target = "/root/pdj/test-" + uuid4().hex
        children = []
        try:
            for tag, arg in [("", target), ("s1", target), ("s10", target),
                             ("", "diagnostic " + target)]:
                env = dict(os.environ)
                env.pop("DJSDEV_TAG", None)
                if tag:
                    env["DJSDEV_TAG"] = tag
                children.append(subprocess.Popen(
                    [sys.executable, "-c", "import time; time.sleep(30)", arg],
                    env=env))
            for i, tag in enumerate(["", "s1", "s10"]):
                result = subprocess.check_output(
                    ["bash", "-c", 'source "$1"; pids_of "$2"', "test",
                     str(helper), target], env=dict(os.environ, DJSDEV_TAG=tag),
                    text=True)
                self.assertEqual(result.split(), [str(children[i].pid)])
        finally:
            for child in children:
                child.terminate()
                child.wait()


if __name__ == "__main__":
    unittest.main()
