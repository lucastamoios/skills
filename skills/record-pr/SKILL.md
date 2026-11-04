---
name: record-pr
description: Record reviewer-facing media for a PR using Playwright. By default it produces a "before/after" walkthrough video pair (narrated mp4 for browser drag-drop into a PR description); when the user also asks for screenshots, prints, or before/after images, it additionally captures a before/after PNG pair from the same scenes. With --lighthouse, Lighthouse runs it headlessly to start an isolated the configured organization stack at a PR head and take "after" screenshots of the changed screens. Trigger when the user asks to record a PR video, demo a fix, capture a UI walkthrough, take before/after screenshots of a change, or produce reviewer-facing media for a frontend or workflow change. Follows the team visual standard.
user_invocable: true
allowed-tools: Bash(git *), Bash(gh api *), Bash(docker *), Bash(just *), Bash(./dev_compose.sh *), Bash(curl *), Bash(lsof *), Bash(python3 *), Bash(ffmpeg *), Bash(brew *), Bash(uv *), Bash(.venv/bin/*), Read, Edit, Write, Grep, Glob, AskUserQuestion
argument-hint: "<ISSUE-ID> (e.g. <PREFIX>-<number>); add 'screenshots' to also capture a before/after PNG pair; or '<PR number> --lighthouse --url <lighthouse url>' for the headless Lighthouse mode"
---

# Record PR walkthrough

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. For shell examples, set `SKILL_CONFIG` to the installed `skill-config/scripts/config.py` absolute path. The examples query the private profile at runtime; verify required fields before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Produces a narrated Playwright walkthrough showing the change in action. For bug fixes, produces **two** videos - the bug repro (with the fix temporarily reverted) and the fix-applied case. Same scenario, same data, same camera, only the code changes. The output is intended to be embedded in the PR description via the `/create-pr` skill.

Video is the default and only output. When the user also asks for screenshots (prints, stills, a before/after image pair), additionally capture the before/after PNG pair described in **Screenshots mode**; it rides on the same script and recording passes, never on a separate ad-hoc flow.

When the arguments contain `--lighthouse`, skip everything else in this file and follow only **Lighthouse mode** at the end. The default behavior below does not apply to that mode, and that mode does not change the default behavior.

## When to use

- The diff touches frontend or workflow code and the change is **interactive** (multi-step, before/after comparison, bug repro). For a single static state, prefer the screenshot path in `/create-pr` instead.
- The user explicitly asks for a walkthrough, demo, "show me the bug", a video, or before/after screenshots of a change.

If the diff is purely backend with no observable UI flow, do not run this skill.

## Output

All artifacts go to `profile.paths.artifacts/<ISSUE-ID>/`:

- `record_qa.py` - the Playwright script (re-runnable)
- `reset_workflow.py` (or equivalent) - small Django shell script that resets test data between recordings, run inside the app-server container
- `bug-before-fix.mp4` and `fix-applied.mp4` (or single `walkthrough.mp4` for non-bug changes) - encoded videos
- `before.png` and `after.png` - only when screenshots were requested (see **Screenshots mode**)
- `.venv/` - Python venv with playwright + chromium

## Visual standard (non-negotiable)

Do not improvise alternatives to any of these. If a scene cannot meet a rule, drop the scene.

- **One pulse style only**: a pulsing red aura, **1 second per pulse cycle**.
- **A single pulse per highlight.** One 1-second pulse cycle draws attention, both for "look at this" moments and before a click (the element pulses once *before* the click happens). Keep the overview tight; if the viewer needs more time on a scene (a dense table, a subtle difference), hold the caption on screen after the pulse instead of adding pulse cycles.
- **Only one element pulses at a time** on a given screen.
- **Every application scene must have at least one pulse**. The opening title card is exempt and stays static. If an application scene has nothing worth pulsing, drop the scene.
- **Persistent narration banner** fixed at the **bottom** of the viewport, so it never covers the app's top navbar or page headers (if a scene's subject sits at the very bottom edge, scroll it toward the middle before pulsing rather than moving the banner). It is a single flex row: a blue pill step chip (`2/4`) followed by a one-sentence description, on a dark gradient with white bold text. It must set `pointer-events: none` (so it never intercepts clicks), max `z-index`, and be appended to `document.documentElement` rather than `body` (so HTMX body/table swaps cannot destroy it). Only its inner text updates between scenes; never remove and re-add it (avoid flicker and viewport jumps).
- **The video opens on a title card, not a blank frame**: `page.set_content(...)` a full-viewport dark card with the feature title, issue id, and a one-line summary, hold it ~1.5s without selecting text, focusing the title, or applying any pulse/highlight, and `page.screenshot` it as `splash.png` for the encode step (Step 7 prepends it to the mp4 so the PR thumbnail is branded).
- **The login screen never appears in the video.** Authenticate off camera: create a throwaway context with no `record_video_dir`, log in there, capture `context.storage_state()`, close it, and create the recording context with `storage_state=state`. The video then cuts from the title card straight to the feature page.
- **Missing data is shown explicitly**: where the change is *removal* or absence, show a red `"<thing> should be here →"` badge that **floats next to** the spot and points at it with the arrow. The badge must be out of flow (`position: fixed`, coordinates from the anchor's `getBoundingClientRect()`, appended to `document.documentElement`): never insert it *into* the anchor, because an in-flow marker shifts or overlaps the surrounding content instead of pointing at the gap. Place it to the left of the anchor with a trailing `→`; if there is no room on the left, flip it to the right side with a leading `←`. Do not scroll while it is up (fixed coordinates do not track scrolling). Anchoring "before" and "after" highlights to the same DOM ancestor keeps the spatial location identical across scenes.
- **Banners and pulses are CSS injected by the script**, not native browser/OS overlays.
- **Highlights must preserve the element's own CSS.** Never animate `background-color` (or any property the element already uses for its normal look): a CSS animation overrides the element's declared style for the entire animation, so a blue button pulses red-and-white and effectively disappears. Tint with an inset `box-shadow` overlay instead - it paints on top of the element's own background and leaves it visible underneath, and at the transparent keyframes the element renders exactly as the app styles it.
- **Highlights must stay inside the element's bounding box.** Outward `box-shadow` is clipped to broken-looking corner fragments by table containers, modals, or any `overflow: hidden`/`auto` ancestor. The inset tint plus a negative-`outline-offset` border render entirely within the element:
  ```css
  @keyframes pw-pulse-red {
    0%, 100% {
      box-shadow: inset 0 0 0 9999px rgba(220, 38, 38, 0);
      outline: 0 solid rgba(220, 38, 38, 0);
      outline-offset: -2px;
    }
    50% {
      box-shadow: inset 0 0 0 9999px rgba(220, 38, 38, 0.25);
      outline: 3px solid #dc2626;
      outline-offset: -3px;
    }
  }
  ```
  Known trade-off: an element that uses its own `box-shadow` loses it while pulsing, which is far less jarring than losing its background. Inset shadows work on `tr`/`td` in Chromium, so table rows pulse fine.

## Workflow

### Step 1: Confirm preconditions

Use the repository's documented isolated development setup and the relevant adapter in `profile.contexts.record-pr`. Confirm the application URL, disposable test data and authentication method before recording. Never assume a framework, Compose service, seeded database, model or account from another project. Use a synthetic test account and generated temporary credentials. Keep login and credential values off camera. Prepare Playwright and ffmpeg locally when needed.

### Step 2: Map the scenario

Before writing any code, list the static opening title card, then every application scene and the single element to pulse on each. Do not assign a pulse target to the title card. If you cannot enumerate the application scenes, the scenario isn't ready.

A typical bug-fix walkthrough has four scenes:

1. **Before**: source state on the auth/entity detail page; pulse the field that will be affected.
2. **Workflow / interaction**: the page where the user triggers the change; pulse the rows or selection.
3. **Action**: the button about to be clicked; one pulse before the click.
4. **After**: same field as Scene 1, anchored to the same DOM ancestor; one pulse on either the missing-data marker (bug) or the preserved/changed value (fix), then hold the caption briefly so the verdict lands.

Scene 1 and Scene 4 must point at the same place. If you cannot anchor them to the same DOM ancestor (e.g. because the page navigates and the field moves), pick a different "place" both scenes can share - usually a table row or a dedicated detail section, never the page subheader for a "draft" version that doesn't render in the subheader.

**Add a hover scene when the change lives in hover-revealed UI.** If the diff touches a tooltip, a hover popover, row-hover action buttons, or hover-only styling, a static screenshot or a plain click never shows it, so map a scene that moves the mouse onto the trigger and pulses what the hover reveals (the tooltip or popover, not the trigger). The verdict for these changes is the revealed content, so that is what gets the pulse and the held caption. When the change is hover behavior itself (the element only changes on hover), the before/after pair is the same element hovered in both videos. Skip a hover scene when the change is not observable on hover; do not add one just to have one.

### Step 3: Write the Playwright script

Save to `profile.paths.artifacts/<ISSUE-ID>/record_qa.py`. Use `playwright.sync_api`. Inject the CSS standard at the top of the script. Drive the page with semantic locators (`get_by_role`, `get_by_text`, or specific CSS) - inferred selectors that are robust against minor template changes.

Helpers the script needs:

- `set_banner(page, step, text)` - one idempotent create-or-update call (reference implementation below). Call it after every navigation and at the start of every scene: it creates the banner when the page does not have one yet, otherwise it only updates the chip and the text. There is no separate "install" helper to forget.
- `install_pulse_css(page)` - injects the `pw-pulse-red` keyframes once per page (guard with an id, same pattern as the banner).
- `pulse_locator(page, locator, pulses)` - adds a `pw-pulse-red` class for `pulses` seconds, removes it.
- `pulse_text(page, text, pulses)` and `pulse_missing(page, anchor, label, pulses)` - text-based and "should be here" variants. `pulse_missing` creates the floating badge described in the visual standard (reference implementation below) and removes it afterwards; pass the label without the arrow, the helper adds `→`/`←` based on which side it lands on.
- `hover_and_pulse(page, trigger, revealed, pulses)` - for hover scenes. Call `trigger.hover()`, wait for the revealed element to be visible (`revealed.wait_for(state="visible")`), then pulse `revealed` while the mouse stays on the trigger. Do not move the mouse off the trigger until the pulse finishes, or the revealed element disappears mid-pulse. Two caveats specific to hover: Playwright does not render a cursor in the recording, so a tooltip that just pops up looks unexplained, the banner caption must say the hover is happening (e.g. "hovering the status chip reveals the rejection reason"); and a hover that only restyles the element still follows the box-shadow inset rule from the visual standard (never animate the property the hover itself changes, or the pulse and the hover fight over the same style). When the revealed element overlaps the bottom banner, pulse it and hold the caption, then read it before the hover ends rather than scrolling.

`pulse_missing` badge reference implementation (evaluate on the anchor locator with the label as argument):

```js
(el, label) => {
  const r = el.getBoundingClientRect();
  const m = document.createElement('div');
  m.id = '__qa_missing_marker__';
  m.className = 'pw-pulse-red';
  m.style.cssText =
    'position:fixed;z-index:2147483646;pointer-events:none;' +
    'background:#fff;border:2px solid #dc2626;border-radius:6px;' +
    'color:#dc2626;font:700 13px/1 -apple-system,"Segoe UI",Roboto,sans-serif;' +
    'padding:6px 10px;white-space:nowrap';
  m.textContent = label + ' →';
  document.documentElement.appendChild(m);
  let left = r.left - m.getBoundingClientRect().width - 10;
  if (left < 4) {  // no room on the left: flip to the right side
    m.textContent = '← ' + label;
    left = r.right + 10;
  }
  m.style.left = left + 'px';
  m.style.top = (r.top + r.height / 2 - m.getBoundingClientRect().height / 2) + 'px';
}
```

Banner reference implementation, called via `page.evaluate(js, {"chip": "2/4", "text": "..."})`:

```js
(p) => {
  const ID = '__qa_banner__';
  let bar = document.getElementById(ID);
  if (!bar) {
    bar = document.createElement('div');
    bar.id = ID;
    bar.style.cssText =
      'position:fixed;left:0;right:0;bottom:0;z-index:2147483647;' +
      'pointer-events:none;box-sizing:border-box;padding:20px 28px;' +
      'background:linear-gradient(0deg, rgba(15,23,42,.95), rgba(15,23,42,.82));' +
      'color:#fff;font:600 24px/1.35 -apple-system,"Segoe UI",Roboto,sans-serif;' +
      'text-shadow:0 1px 3px rgba(0,0,0,.7);display:flex;align-items:center;gap:16px';
    bar.innerHTML =
      '<span id="' + ID + '_chip" style="flex:none;background:#2563eb;color:#fff;' +
      'border-radius:999px;padding:5px 14px;font-size:15px;font-weight:700;' +
      'line-height:1;white-space:nowrap"></span><span id="' + ID + '_text"></span>';
    document.documentElement.appendChild(bar);  // survives HTMX body swaps
  }
  document.getElementById(ID + '_chip').textContent = p.chip;
  document.getElementById(ID + '_text').textContent = p.text;
}
```

Caption timing: update the banner **as** the action fires (no pre-pause), then hold 1.5-2s afterwards so it can be read. For `goto`, navigate first and set the banner right after (navigation wipes the DOM anyway).

The video size must be `1440 x 900`; output goes through `record_video_dir` and `record_video_size` on the browser context. Log in with a separate non-recorded context first and pass its `storage_state()` to the recording context, so the login screen is never on camera (see the visual standard).

### Step 4: Write the reset script

If the recording involves stateful workflow data (decisions, drafts, etc.), write a small `reset_workflow.py` (or analogous Django shell file) that resets the data to a clean known state between recordings. The script must be deterministic - sort by uid or similar so cert / version numbering doesn't drift between runs.

Run the reset before each recording:

```bash
docker compose -f docker-compose-development.yaml exec -T app-server \
  python manage.py shell < "$(python3 "$SKILL_CONFIG" get paths.artifacts --path)/<ISSUE-ID>/reset_workflow.py"
```

### Step 5: Record the bug video

For bug fixes, the bug video is recorded against the **bug code**, not the fix:

```bash
git stash push -m "tmp: revert for video" <files-with-the-fix>
sleep 4    # let Django runserver autoreload
.venv/bin/python record_qa.py . bug-before-fix bug
git stash pop
sleep 2    # let runserver reload again
```

Verify the bug behavior was actually captured by checking the DB after recording (e.g. the affected field is empty / wrong / different as expected).

### Step 6: Record the fix video

```bash
docker compose ... exec -T app-server python manage.py shell < reset_workflow.py
.venv/bin/python record_qa.py . fix-applied fix
```

Verify the fix behavior in the DB (the affected field is correct).

### Step 7: Encode

Each `.webm` produces an `.mp4` (for browser drag-drop into the PR description). mp4 only - do not generate a gif:

```bash
# mp4 - small, smooth playback, controls in any player
ffmpeg -y -i <label>.webm \
  -c:v libx264 -preset slow -crf 28 -pix_fmt yuv420p -movflags +faststart \
  -vf "scale=1280:-2" <label>.mp4

# mp4 with the title card prepended (preferred when splash.png exists): GitHub
# uses the literal first frame as the inline player thumbnail, so this makes
# the PR show a branded card instead of a half-loaded page.
ffmpeg -y -loop 1 -t 1.5 -i splash.png -i <label>.webm \
  -filter_complex "[0:v]scale=1280:-2,setsar=1,fps=30,format=yuv420p[i];[1:v]scale=1280:-2,setsar=1,fps=30,format=yuv420p[m];[i][m]concat=n=2:v=1:a=0[v]" \
  -map "[v]" -c:v libx264 -preset slow -crf 28 -movflags +faststart <label>.mp4
```

Target size for a ~30-second clip: mp4 around 800 KB.

### Step 8: Verify and report

- Open the mp4 and watch it through. Specifically check: the opening title card stays static with no text selection, focus outline, or pulse; each banner is readable, each pulse lands inside its element bounds, the pulsed element keeps its own colors before and after the pulse (a styled button must still look like itself, only tinted at the pulse peak), and scenes 1 and 4 point at the same place. For a hover scene, confirm the revealed element (tooltip/popover) is actually on screen while it pulses and that the caption explains the hover, since the cursor is not visible.
- If anything is off, iterate on the script and re-record. Do not deliver media that doesn't meet the standard.
- Report the file paths and sizes for the next step (`/create-pr` will reference them).

## Screenshots mode (on request)

Run this only when the user asked for screenshots (prints, stills, a before/after image pair) in addition to the videos. The pair comes from the same script, scenes, and recording passes as the videos, so both artifacts always show the same data and the same place:

- `before.png` is captured during the before pass (the bug pass of Step 5; for non-bug changes, run one extra pass with the change stashed, using the same stash mechanics as Step 5). `after.png` is captured during the fix pass of Step 6.
- Capture at the **verdict moment of the final scene**: the same element that scenes 1 and 4 anchor to, with the banner caption on screen. Viewport-sized at 1440 x 900, not `full_page`.
- A pulse cannot be trusted to be mid-cycle in a still, so freeze the highlight instead: apply the pulse's peak styles statically with a `pw-still` class, take the shot, then remove the class.
  ```css
  .pw-still {
    box-shadow: inset 0 0 0 9999px rgba(220, 38, 38, 0.25);
    outline: 3px solid #dc2626;
    outline-offset: -3px;
  }
  ```
- The floating `"<thing> should be here →"` badge from the visual standard works in stills too; keep it up during the shot for missing-data cases.
- The whole visual standard still applies: one highlighted element per shot, banner at the bottom, no login screen, element keeps its own CSS under the static tint.

## Embedding into a PR

For a **public repo**, you have a workable no-browser fallback. For a **private repo** like profile.work.github_repository, the browser drag-drop is unavoidable - I (or the team) verified this against the real PR endpoint. Don't promise a no-browser path that doesn't exist.

### Public repos

- **Browser drag-drop.** Open the PR, edit the description, drag each `.mp4` into the body, save. GitHub auto-uploads to its `user-attachments` CDN and inserts a `github.com/.../assets/<uuid>` URL that renders inline as a `<video>` tag with controls.

### Private repos (the honest answer)

**Browser drag-drop is the only reliable path.** The reasons, verified empirically:

- The undocumented `/upload/policies/assets` endpoint that drag-drop uses **rejects bearer-token auth with a generic 422**. It needs a `_gh_sess` session cookie that you only get from a real browser login. (`gh-attach` accepts a `token` argument but its own debug output shows it skips this strategy and falls through to a branch commit.)
- A committed file's `https://github.com/<org>/<repo>/raw/<branch>/...` URL **404s in the PR description for private repos** even when authenticated. Only the `user-attachments` CDN (which authenticates against the viewer's GitHub session, not against the request) renders inline.
- Base64 `data:` URIs in Markdown image syntax (`![](data:image/gif;base64,...)`) are **sanitized out** of PR/issue/comment bodies. This is documented behavior, not a bug, and unlikely to change.
- External hosts (S3, imgur) work but introduce a third-party dependency every reviewer has to be able to reach.

So for the configured organization: produce the media with this skill, commit only the code/test changes (NOT the videos or screenshots), open the PR, and **the author drag-drops the `.mp4` (and `.png`) files into the PR body in the GitHub web UI**. ~30 seconds of manual work, no other path is honest. PNGs obey the same private-repo constraint as mp4s: raw committed URLs 404 in PR bodies, only the `user-attachments` CDN renders inline.

Don't try to script the upload to user-attachments via a token-only flow against a private repo - it will look like it works in dev (public test repo) and silently fail when the team uses it. We hit exactly that.

`mp4` cannot be embedded by Markdown image link in any case - GitHub strips `<video>` tags from raw repo URLs in PR bodies. The `user-attachments` URL is the only one that renders inline.

## Done

Hand off to the user with the file paths (videos, plus the PNG pair when screenshots mode ran). If they invoked you as part of `/create-pr`, return the paths so the PR body can reference them.

## Optional screenshot service mode

When `--lighthouse` is requested, load the procedures from `profile.contexts.record-pr` and the screenshot contract from `profile.integrations.lighthouse.screenshots_contract`. Follow their input/output protocol within the current authorization. If either is absent, report the missing integration; do not guess a repository, stack, database or credentials. Ordinary recording remains available without this integration.
