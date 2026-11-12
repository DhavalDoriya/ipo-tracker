"""Static UI checks: card links are buttons, buttons have every state and a touch-size target."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
CSS = (SRC / "styles/global.css").read_text()


def anchors(component):
    return re.findall(r"<a\b[^>]*>", (SRC / "components" / component).read_text())


class CardLinkTests(unittest.TestCase):
    def test_source_links_are_buttons(self):
        for name in ("IpoCard.astro", "PipelineCard.astro"):
            for tag in anchors(name):
                self.assertIn('class="btn', tag, f"{name}: {tag} is an unstyled text link")

    def test_card_links_do_not_overflow_on_phones(self):
        self.assertRegex(CSS, r"\.links\s*\{[^}]*flex-wrap:\s*wrap")


class ButtonStateTests(unittest.TestCase):
    def block(self, selector):
        m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", CSS)
        self.assertIsNotNone(m, f"missing rule {selector}")
        return m.group(1)

    def test_has_focus_and_disabled_states(self):
        self.assertIn(".btn:focus-visible", CSS)
        self.assertIn(".btn:disabled", CSS)

    def test_touch_target(self):
        self.assertIn("min-height: var(--touch)", self.block(".btn"))

    def test_external_icon_is_decorative(self):
        text = (SRC / "components/PipelineCard.astro").read_text()
        self.assertIn('aria-hidden="true"', text)


if __name__ == "__main__":
    unittest.main()


class ThemeSwitchMotionTests(unittest.TestCase):
    toggle = (SRC / "components/ThemeToggle.astro").read_text()

    def test_theme_switch_animates_as_a_reveal(self):
        self.assertIn("startViewTransition", self.toggle)
        self.assertIn("clipPath", self.toggle)

    def test_theme_switch_respects_reduced_motion(self):
        self.assertIn("prefers-reduced-motion: reduce", self.toggle)

    def test_ambient_glow_is_gone(self):
        self.assertNotIn("glow-drift", CSS)

    def test_motion_is_switched_off_for_reduced_motion(self):
        m = re.search(r"prefers-reduced-motion:\s*reduce\)\s*\{(.*?)\n\}", CSS, re.S)
        self.assertIsNotNone(m)
        self.assertIn("animation: none !important", m.group(1))


class BrandNameTests(unittest.TestCase):
    def test_site_is_called_ipo_tracker(self):
        for path in SRC.rglob("*.astro"):
            self.assertNotIn("IPO Update", path.read_text(), f"{path.name} still uses the old name")
        self.assertIn("IPO Tracker", (SRC / "components/Header.astro").read_text())
