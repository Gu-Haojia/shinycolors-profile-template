# Shiny Colors Profile

An animated GitHub Profile README inspired by the enza browser game's UI. A Python builder turns GitHub data into one self-contained SVG, with embedded fonts, images and subtle looping animation. No server or GitHub Pages required.

## Quick start

1. [Use this template](https://github.com/Gu-Haojia/shinycolors-profile-template/generate) to create a **public** repository named exactly like your GitHub username, e.g. `alice/alice`.
2. Open **Actions → Shiny Refresh → Run workflow**, enabling Actions if prompted.
3. Wait for the successful run, then visit your GitHub profile. Edit `config.json` and `projects.json` to personalize the content.

The workflow automatically uses the repository owner's username, GitHub display name, avatar and public repository data. It needs only the built-in `GITHUB_TOKEN`, not a personal access token. The default refresh is daily at **16:17 UTC**, and after configuration/source changes. A strict refresh failure leaves the published profile intact.

## Configuration

- `github: "auto"`, `nickname: "auto"`: detect your identity. Explicit values override these defaults.
- `projects.json`: `{"items": null, "limit": 4}` automatically selects four recently pushed repositories. An explicit `items` array controls order and text; `[]` hides all project cards. See `examples/projects.manual.json`.
- The home card independently finds the latest default-branch commit, excluding the profile and current build repositories.
- `character`: choose one of [28 characters](CHARACTERS.md) by ID or name, e.g. `"hana"` or `"madoka"`. Use `"random"` to choose once per build (repeats are possible), while keeping random mode for subsequent scheduled runs. Refreshing the GitHub page does not reroll.
- **Run workflow → character** can save a character or `random` to your config; `from-config` preserves your settings.
- Optional `illustration`: relative PNG/WebP path, or `null` to hide the character. This overrides `character`; remove it to use the built-in roster. Explicit CLI/Actions selections remove this override. Included backgrounds and UI labels remain.
- Skills, bio and greeting are editable sample copy, not inferred from your GitHub data. The UI is primarily Simplified Chinese.

A same-name profile repository replaces its README with the generated image. Ordinary repositories retain this template's documentation and update only the marked preview. Add `--readme-mode preserve` to the workflow to keep a custom profile README; place one `<!-- SHINY:START -->` / `<!-- SHINY:END -->` pair where the image should appear. `PROFILE.md` is always generated as a standalone snippet.

## Local preview

Python 3.12+:

```sh
python -m venv .venv
# Activate .venv for your shell, then:
python -m pip install -r requirements.txt
python build.py --demo
python build.py --demo --character madoka  # One-off override; config is unchanged
python build.py --list-characters
python -m http.server 4180 --bind 127.0.0.1
```

Open `http://127.0.0.1:4180/preview.html`. Demo mode uses synthetic data and makes no network requests. For live data, provide `GITHUB_TOKEN` through the environment and run `python build.py --username YOUR_USERNAME --strict-refresh`. Subsequent offline edits can use `--offline --watch` with the same username.

Tests: `python -m unittest discover -s tests -v`.

The home commit count is a rolling-year contribution count; panels labeled with a year show calendar-year contributions. Neither is a raw lifetime commit count. Read the [full configuration reference](CONFIGURATION.md) and [deployment troubleshooting](DEPLOYMENT.md) (Chinese).

## Licensing

Builder code, tests and documentation are MIT licensed. **Game assets, characters and derivative illustrations are excluded from that license.** Their inclusion does not grant commercial or redistribution rights. Fonts and icons have their own licenses. Read [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) and replace third-party visuals where appropriate. This is an unofficial fan project, not affiliated with Bandai Namco Entertainment.
