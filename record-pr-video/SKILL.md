---
name: record-pr-video
description: Record a "before/after" walkthrough video pair for a PR using Playwright. Trigger when the user asks to record a PR video, demo a fix, capture a UI walkthrough, or produce reviewer-facing media for a frontend or workflow change. Produces narrated mp4 (preferred for browser drag-drop into a PR description) and gif (committable to the repo so no browser is needed). Follows the team visual standard.
user_invocable: true
allowed-tools: Bash(git *), Bash(docker *), Bash(just *), Bash(curl *), Bash(ffmpeg *), Bash(brew *), Bash(uv *), Bash(.venv/bin/*), Read, Edit, Write, Grep, Glob, AskUserQuestion
argument-hint: "<ISSUE-ID> (e.g. COM-4479)"
---

# Record PR walkthrough video

Produces a narrated Playwright walkthrough showing the change in action. For bug fixes, produces **two** videos - the bug repro (with the fix temporarily reverted) and the fix-applied case. Same scenario, same data, same camera, only the code changes. The output is intended to be embedded in the PR description via the `/create-pr` skill.

## When to use

- The diff touches frontend or workflow code and the change is **interactive** (multi-step, before/after comparison, bug repro). For a single static state, prefer the screenshot path in `/create-pr` instead.
- The user explicitly asks for a walkthrough, demo, "show me the bug", or video.

If the diff is purely backend with no observable UI flow, do not run this skill.

## Output

All artifacts go to `~/work/tasks/<ISSUE-ID>/`:

- `record_qa.py` - the Playwright script (re-runnable)
- `reset_workflow.py` (or equivalent) - small Django shell script that resets test data between recordings, run inside the app-server container
- `bug-before-fix.mp4` and `fix-applied.mp4` (or single `walkthrough.mp4` for non-bug changes) - encoded videos
- `bug-before-fix.gif` and `fix-applied.gif` - same content, smaller, committable
- `.venv/` - Python venv with playwright + chromium

## Visual standard (non-negotiable)

Do not improvise alternatives to any of these. If a scene cannot meet a rule, drop the scene.

- **One pulse style only**: a pulsing red aura, **1 second per pulse cycle**.
- **Pulse counts encode meaning**:
  - **4 pulses (4s)** when showing the viewer something to look at.
  - **2 pulses (2s)** when about to click or navigate away. The same element pulses *before* the click happens.
- **Only one element pulses at a time** on a given screen.
- **Every screen must have at least one pulse**. If a scene has nothing worth pulsing, drop the scene.
- **Persistent narration banner** fixed at the top; only its inner text updates between scenes. Never remove and re-add it (avoid flicker and viewport jumps). Each banner update has a step indicator (`2/4`) and a one-sentence description.
- **Missing data is shown explicitly**: where the change is *removal* or absence, inject a red `"<thing> should be here →"` marker into the DOM at the *same DOM position* the missing data would normally render, and pulse the marker. Anchoring "before" and "after" highlights to the same DOM ancestor keeps the spatial location identical across scenes.
- **Banners and pulses are CSS injected by the script**, not native browser/OS overlays.
- **Highlights must stay inside the element's bounding box.** Outward `box-shadow` is clipped to broken-looking corner fragments by table containers, modals, or any `overflow: hidden`/`auto` ancestor. Use a background tint plus a negative-`outline-offset` border so the highlight renders entirely within the element:
  ```css
  @keyframes pw-pulse-red {
    0%, 100% {
      background-color: rgba(220, 38, 38, 0);
      outline: 0 solid rgba(220, 38, 38, 0);
      outline-offset: -2px;
    }
    50% {
      background-color: rgba(220, 38, 38, 0.30);
      outline: 3px solid #dc2626;
      outline-offset: -3px;
    }
  }
  ```

## Workflow

### Step 1: Confirm preconditions

- The dev stack is up and reachable at `https://localhost`. If not, start it with `just dev-deploy` (which restores `db.dump.gpg` and brings the stack up).
- The user can log in. If credentials aren't ready, set a temporary password on a known dev user via the Django shell:
  ```bash
  docker compose -f docker-compose-development.yaml exec -T app-server python manage.py shell -c "
  from core.models import User
  u = User.all_tenants.get(email='aden+test@compassregulatory.com')
  u.set_password('com<NNNN>-qa'); u.save()
  "
  ```
- ffmpeg installed: `brew install ffmpeg` if missing.
- Playwright + chromium installed in a venv at `~/work/tasks/<ISSUE-ID>/.venv` (uv venv + uv pip install playwright + python -m playwright install chromium).

### Step 2: Map the scenario

Before writing any code, list every scene and the single element to pulse on each. If you cannot enumerate them, the scenario isn't ready.

A typical bug-fix walkthrough has four scenes:

1. **Before**: source state on the auth/entity detail page; pulse the field that will be affected.
2. **Workflow / interaction**: the page where the user triggers the change; pulse the rows or selection.
3. **Action**: the button about to be clicked; 2-pulse before click.
4. **After**: same field as Scene 1, anchored to the same DOM ancestor; 4-pulse showing either the missing-data marker (bug) or the preserved/changed value (fix).

Scene 1 and Scene 4 must point at the same place. If you cannot anchor them to the same DOM ancestor (e.g. because the page navigates and the field moves), pick a different "place" both scenes can share - usually a table row or a dedicated detail section, never the page subheader for a "draft" version that doesn't render in the subheader.

### Step 3: Write the Playwright script

Save to `~/work/tasks/<ISSUE-ID>/record_qa.py`. Use `playwright.sync_api`. Inject the CSS standard at the top of the script. Drive the page with semantic locators (`get_by_role`, `get_by_text`, or specific CSS) - inferred selectors that are robust against minor template changes.

Helpers the script needs:

- `install_page_chrome(page, step, banner_text)` - injects CSS once, creates the persistent banner, sets initial text. Call after every navigation since the new page has no chrome.
- `set_banner(page, step, text)` - updates the persistent banner only.
- `pulse_locator(page, locator, pulses)` - adds a `pw-pulse-red` class for `pulses` seconds, removes it.
- `pulse_text(page, text, pulses)` and `pulse_missing(page, anchor, label, pulses)` - text-based and "should be here" injection variants.

The video size must be `1440 x 900`; output goes through `record_video_dir` and `record_video_size` on the browser context.

### Step 4: Write the reset script

If the recording involves stateful workflow data (decisions, drafts, etc.), write a small `reset_workflow.py` (or analogous Django shell file) that resets the data to a clean known state between recordings. The script must be deterministic - sort by uid or similar so cert / version numbering doesn't drift between runs.

Run the reset before each recording:

```bash
docker compose -f docker-compose-development.yaml exec -T app-server \
  python manage.py shell < ~/work/tasks/<ISSUE-ID>/reset_workflow.py
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

Each `.webm` produces an `.mp4` (preferred for browser drag-drop) and a `.gif` (committable to repo for no-browser embedding):

```bash
# mp4 - small, smooth playback, controls in any player
ffmpeg -y -i <label>.webm \
  -c:v libx264 -preset slow -crf 28 -pix_fmt yuv420p -movflags +faststart \
  -vf "scale=1280:-2" <label>.mp4

# gif - bigger but committable
ffmpeg -y -i <label>.webm \
  -vf "fps=8,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=96[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5" \
  -loop 0 <label>.gif
```

Target sizes for a ~30-second clip: mp4 around 800 KB, gif around 2.5 MB. If the gif is much larger, drop fps to 6 and scale width to 640.

### Step 8: Verify and report

- Open the mp4 and watch it through. Specifically check: each banner is readable, each pulse lands inside its element bounds, scenes 1 and 4 point at the same place.
- If anything is off, iterate on the script and re-record. Do not deliver media that doesn't meet the standard.
- Report the file paths and sizes. Mention both the mp4 and gif options for the next step (`/create-pr` will reference them).

## Embedding into a PR

For a **public repo**, you have a workable no-browser fallback. For a **private repo** like Compass-Regulatory/compass, the browser drag-drop is unavoidable - I (or the team) verified this against the real PR endpoint. Don't promise a no-browser path that doesn't exist.

### Public repos

- **Option A (recommended): browser drag-drop.** Open the PR, edit the description, drag each `.mp4` into the body, save. GitHub auto-uploads to its `user-attachments` CDN and inserts a `github.com/.../assets/<uuid>` URL that renders inline as a `<video>` tag with controls.
- **Option B: commit gif to a branch + Markdown image link.** GIFs (not mp4) render inline from public repo raw URLs. Trade-off is permanent binary blobs in git history.
  ```bash
  mkdir -p clients/web/docs/com-<NNNN>
  cp ~/work/tasks/COM-<NNNN>/{bug-before-fix,fix-applied}.gif clients/web/docs/com-<NNNN>/
  git add clients/web/docs/com-<NNNN>/ && git commit -S -m "docs: walkthrough gifs for COM-<NNNN>" && git push
  ```
  ```markdown
  ![bug](https://github.com/<org>/<repo>/raw/<branch>/clients/web/docs/com-<NNNN>/bug-before-fix.gif)
  ```

### Private repos (the honest answer)

**Browser drag-drop is the only reliable path.** The reasons, verified empirically:

- The undocumented `/upload/policies/assets` endpoint that drag-drop uses **rejects bearer-token auth with a generic 422**. It needs a `_gh_sess` session cookie that you only get from a real browser login. (`gh-attach` accepts a `token` argument but its own debug output shows it skips this strategy and falls through to a branch commit.)
- A committed file's `https://github.com/<org>/<repo>/raw/<branch>/...` URL **404s in the PR description for private repos** even when authenticated. Only the `user-attachments` CDN (which authenticates against the viewer's GitHub session, not against the request) renders inline.
- Base64 `data:` URIs in Markdown image syntax (`![](data:image/gif;base64,...)`) are **sanitized out** of PR/issue/comment bodies. This is documented behavior, not a bug, and unlikely to change.
- External hosts (S3, imgur) work but introduce a third-party dependency every reviewer has to be able to reach.

So for Compass: produce the videos with this skill, commit only the code/test changes (NOT the videos), open the PR, and **the author drag-drops the `.mp4` files into the PR body in the GitHub web UI**. ~30 seconds of manual work, no other path is honest.

Don't try to script the upload to user-attachments via a token-only flow against a private repo - it will look like it works in dev (public test repo) and silently fail when the team uses it. We hit exactly that.

`mp4` cannot be embedded by Markdown image link in any case - GitHub strips `<video>` tags from raw repo URLs in PR bodies. The `user-attachments` URL is the only one that renders inline.

## Done

Hand off to the user with the file paths. If they invoked you as part of `/create-pr`, return the paths so the PR body can reference them.
