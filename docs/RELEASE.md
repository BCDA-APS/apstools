# Release Guide

Step-by-step instructions for publishing a new apstools release to PyPI,
conda-forge, and GitHub Pages.

**Key scripts** (run from the repo root):

| Script | Purpose |
|--------|---------|
| `python scripts/release.py rc` | Tag the next rc, update `switcher.json`, push |
| `python scripts/release.py final` | Finalise `CHANGES.rst`, tag the release, push |
| `python scripts/make_switcher.py` | Regenerate `switcher.json` from git tags (called by the above) |

Use `--dry-run` with either release command to preview what will happen.

---

## Prerequisites

Before starting a release cycle:

- [ ] On the `main` branch with no uncommitted changes
- [ ] All PRs for this milestone are merged or moved to the next milestone
- [ ] GitHub milestone exists for the new version
- [ ] GitHub project exists for the new version (or reuse the current one)
- [ ] The upcoming release section in `CHANGES.rst` is up to date and
      still commented out
- [ ] You have a local clone of your fork of the
      [apstools-feedstock](https://github.com/conda-forge/apstools-feedstock)
      somewhere on your filesystem (outside the apstools repo directory).
      One-time setup if you haven't done this yet:

  ```bash
  # anywhere outside the apstools directory, e.g. ~/projects/conda-forge/
  git clone https://github.com/<your-github-username>/apstools-feedstock
  cd apstools-feedstock
  git remote add upstream https://github.com/conda-forge/apstools-feedstock
  ```

---

## Release Candidate Cycle

Repeat the steps below for each rc iteration (`rc1`, `rc2`, …) until
the conda-forge feedstock CI passes cleanly.

### Step 1 — Tag the rc

```bash
python scripts/release.py rc
```

This automatically:
- Determines the next rc tag (`1.7.10rc1`, `1.7.10rc2`, …)
- Tags the repo
- Regenerates `docs/source/_static/switcher.json`
- Commits `switcher.json` if changed
- Pushes the commit and the tag to `main`

### Step 2 — Note the SHA256 from PyPI CI

The [PyPI publish workflow](https://github.com/BCDA-APS/apstools/actions/workflows/pypi.yml)
runs automatically on every tag.  Find the build log for the `.tar.gz`
artifact and note its SHA256 hash — you will need this for the feedstock.

### Step 3 — Update the conda-forge feedstock

In your local feedstock clone (wherever it lives on your filesystem),
create a **new branch** for this release cycle:

```bash
git checkout main
git pull upstream main
git push origin main          # keep your fork current
git checkout -b release-1.7.10
```

Edit `recipe/meta.yaml`:
- Line 2: update `version` to the new rc tag (e.g. `1.7.10rc1`)
- Line 2: update `sha256` to the value from Step 2

Re-render the recipe:

```bash
conda update -c conda-forge conda-smithy
conda smithy rerender
```

Push and open (or update) the PR against conda-forge:

```bash
git push origin release-1.7.10
```

Complete all checklist items on the feedstock PR.

### Step 4 — Watch feedstock CI

- If CI passes → proceed to [Final Release](#final-release)
- If CI fails → fix `recipe/meta.yaml`, commit to the same branch,
  then go back to Step 1 to create the next rc

---

## Final Release

Once the feedstock CI is green on the latest rc:

### Step 1 — Finalise and tag

```bash
python scripts/release.py final
```

This automatically:
- Uncomments the upcoming release section in `CHANGES.rst` and replaces
  "Release expected by …" with "Released YYYY-MM-DD."
- Inserts a new commented-out section for the next minor version
- Regenerates `switcher.json` (drops all rc entries, adds the final version)
- Commits `CHANGES.rst` and `switcher.json`
- Tags the final release (e.g. `1.7.10`)
- Runs `switcher.json` again after tagging (rc entries now removed)
- Pushes everything to `main`

### Step 2 — Verify PyPI publish

Watch the [PyPI publish workflow](https://github.com/BCDA-APS/apstools/actions/workflows/pypi.yml)
to confirm the final release is published successfully.

### Step 3 — Deploy the docs

```bash
gh workflow run docs.yml -f deploy=true
```

Or via the GitHub UI:
[Actions → Publish Sphinx Docs → Run workflow](https://github.com/BCDA-APS/apstools/actions/workflows/docs.yml)
→ check **Deploy tagged release documentation** → click **Run workflow**.

This publishes the release docs to `https://bcda-aps.github.io/apstools/<version>/`.

### Step 4 — Update and merge the feedstock PR

In your local feedstock clone, update `recipe/meta.yaml`:
- version: final tag (drop the `rcN` suffix, e.g. `1.7.10`)
- sha256: from the final PyPI `.tar.gz` build log (Step 2 above)

Push to the same feedstock branch.  Once feedstock CI passes, merge the PR.

### Step 5 — Create the GitHub release

1. Go to [https://github.com/BCDA-APS/apstools/tags](https://github.com/BCDA-APS/apstools/tags)
2. Select the new tag → **Create release from tag**
3. Set the release name to the tag name (e.g. `1.7.10`)
4. In the release body add:

   ```
   - [Change history](CHANGES.rst)
   ```

5. Click **Generate release notes** to append GitHub's auto-generated notes
6. Click **Publish release**

### Step 6 — Close the milestone

Go to [https://github.com/BCDA-APS/apstools/milestones](https://github.com/BCDA-APS/apstools/milestones)
and close the milestone for this release.

---

## After the Release

- `CHANGES.rst` already has a new commented-out section for the next
  version (added by `release.py final`)
- Create a new GitHub milestone for the next planned release and set its
  due date
- Move any open issues to the new milestone as appropriate
