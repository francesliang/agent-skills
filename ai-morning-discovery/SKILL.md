---
name: morning-discovery
description: Produce a discovery-first spoken news briefing called Morning Discovery, covering the past 24 hours on weekdays and past 7 days on weekends (Australia/Melbourne). Use when asked to research popular Hacker News and Reddit discussions, Hugging Face Daily Papers and weekly popular papers/topics, or Last Week in AI podcast updates; create a source-linked two-host script and Gemini TTS podcast in a dated folder, publish the episode and updated RSS feed to the configured GitHub repository when authorized access is available.
---

# Morning Discovery

Create a self-contained, natural-sounding **two-host podcast** with distinct, substantive turns. Use the **Australia/Melbourne local date and time** to choose the reporting window: **Monday–Friday: rolling past 24 hours; Saturday–Sunday: rolling past 7 days**. State the exact reporting window and whether the edition is daily or weekend. On weekends, synthesize the week’s major developments rather than repeating each day’s headlines.

## News sources — EDIT THIS SECTION

This is the **single source-of-truth configuration** for where to look. Change the entries below to add/remove sources; set `Enabled` to `No` to skip a source. Do not change the reporting, script, or publishing sections when changing the news mix. Use the edition’s reporting window consistently for news and podcast coverage. Hugging Face daily and weekly rankings are both discovery inputs; an older paper can be covered when it gains meaningful attention during the window. State its original publication date and distinguish it from when the discussion became popular.

| Enabled | Source | Starting URL | What to collect | Popularity/selection signal |
|---|---|---|---|---|
| Yes | Hacker News | https://news.ycombinator.com/ | Current front page and notable discussions during the edition window | Primarily discussion comment count; points secondarily. Include major non-AI stories. |
| Yes | Hugging Face Daily Papers | https://huggingface.co/papers | Popular daily papers and newly emerging research topics within the edition window | Daily upvotes/rank; explain concrete research contribution and limitations. |
| Yes | Hugging Face Weekly Papers | https://huggingface.co/papers | Weekly most popular papers and broader research topics that gained attention during the edition window | Weekly upvotes/rank; group recurring themes and avoid duplicating daily-paper coverage. |
| Yes | Reddit popular | https://www.reddit.com/r/popular/ | Broadly trending posts across communities | Upvotes, comment counts, discussion breadth; corroborate factual claims. |
| Yes | AI podcast: Last Week in AI | https://lastweekin.ai/s/podcast | New episodes or new substantive coverage during the edition window; if none, do not present an older episode as fresh | Significant news, discussion highlights and recurring themes; do not invent popularity or imply an older episode is recent. |
| Yes | Important beyond rankings | Primary publishers/research labs; no single URL | Major consequential stories missed by popularity ranks, even when not trending on the configured feeds | Independent significance and verified developments in the edition window. |

To add a source, append a row with a valid starting URL, what to collect, and a selection signal. To remove it, delete its row; to pause it, change `Yes` to `No`. Treat disabled rows as excluded, not as optional suggestions. If the same story appears in multiple sources, cover it once and link all useful discussions in `sources.md`. Use Reddit Popular as the sole configured Reddit discovery feed; inspect linked discussion threads as needed. Do not invent rankings or claim sitewide popularity based on one subreddit.

## Previous-edition check — avoid repeated discoveries

Before selecting stories, fetch or pull the current default branch of https://github.com/francesliang/ai-morning-discovery/tree/main into a suitable local checkout. Read the dated `script.md` and `sources.md` files to build a coverage index of story subjects, original URLs, paper IDs, and developments already explained. Search the whole archive for each candidate, not just the latest episode; a new headline, discussion URL, ranking, or larger vote count does not make the same discovery new.

- Exclude previously covered discoveries with no substantive new development. Apply this to weekday and weekend editions, including papers resurfacing on weekly rankings.
- A follow-up qualifies only when a verified development inside the reporting window materially changes the story. Explain the new evidence or outcome, use at most a brief reminder of prior context, and avoid repeating the previous explanation.
- Record the archive revision checked, prior edition links for follow-ups, and the specific new development in `sources.md`. Include a short list of skipped repeats so selection can be audited.
- When regenerating the same date, use other editions as the duplication baseline and update the current edition rather than treating its own draft as an earlier discovery. Preserve intentional reruns.
- If archive access is unavailable, disclose that duplicate checking is incomplete; do not claim the episode contains only previously uncovered discoveries.

## Research and prioritization

1. Read the **News sources** table and research only enabled sources. Use the specified URLs as starting points, not as substitutes for verifying the actual story and opening relevant discussion threads. If a source is inaccessible, note the gap in `sources.md` rather than silently substituting a different source.
2. Apply the per-source ranking signal in the table. **Popularity first, personal relevance second**: an exceptionally discussed economic, political, cultural or scientific story should not be excluded for being unrelated to AI.
3. Include developments beyond popularity rankings when independently significant and new in the reporting window. Do not hardcode specific articles as mandatory inclusions.
4. Select the key stories that merit substantive explanations without imposing a fixed story count. Deduplicate overlapping coverage. Apply the appropriate weekday (24-hour) or weekend (7-day) window across news, paper discovery and podcast episodes. For Hugging Face, consult both daily and weekly popularity rankings; summarize notable weekly research themes as well as standout individual papers.
5. For weekend editions, review the entire past 7 days, rank the week’s most-discussed and consequential stories, and explain important developments across the week. Avoid reciting a seven-day chronology or repeating stories without new information.

## Reporting standards

- Verify the article, announcement, research findings and dates from primary sources where possible. Cite the original URLs.
- Make the distinction between **reported facts**, **community opinions**, **uncertainty** and **the hosts' own analysis** explicit. Never treat highly upvoted Reddit claims as verified news.
- For each story cover: **(a) what happened with concrete details, (b) why it matters, (c) the main points people are discussing or disagreeing about, (d) a memorable takeaway**. Summarise actual discussion arguments only after inspecting the discussion thread; otherwise label them as questions raised by the story.
- Prefer substance to generic headlines: tell listeners enough to understand the development even without opening the original link. Include relevant figures, comparisons and examples when verified.
- Do not manufacture metrics, quotes, research outcomes or consensus. Label snapshot popularity metrics and describe methodological limitations.
- Avoid forced thematic links between unrelated stories.

## Output

Always produce the complete, **two-host podcast script** as a UTF-8 Markdown file named `script.md`. Rewrite the researched briefing into an actual dialogue before audio generation; do not merely alternate unchanged monologue paragraphs between voices. Write in natural spoken paragraphs, with clear transitions and no tables or citations embedded in spoken sentences. Start with date, weekday/weekend edition label and reporting window, then substantive stories, then a short recap. Target around 10–20 minutes when enough verified stories merit coverage; prioritize depth and important stories over a rigid duration. Use the exact labels `Speaker1:` and `Speaker2:` at the start of each turn, with a blank line between turns. Start the file with a speaker label; all narration, including the opening date and recap, must belong to a labelled turn. These labels map directly to the TTS voices. Give both hosts meaningful explanations, questions, and responses; avoid repetitive agreement, filler, invented personal experiences, and fabricated disagreement. Keep facts and qualifications intact during the rewrite.

Also output `sources.md` containing each story title, original article/paper/podcast URL, relevant Hacker News or Reddit discussion URL, retrieval date and any available votes/comments. Keep source links in this separate file so the dialogue can be spoken naturally. Produce `briefing.md` only if a concise skimmable version is useful.

Group artifacts in a folder named `YYYY-MM-DD/` using the **Melbourne local date** (e.g., `2026-11-08/script.md`, `2026-11-08/sources.md`). Return downloadable file links whenever file output is supported. If scheduled-task execution cannot write files, provide the full two-host script and a companion source list as text, and clearly state the limitation.

## Audio generation — required before publication

Use the bundled [scripts/gemini_tts.py](scripts/gemini_tts.py), with the setup details in [scripts/README.md](scripts/README.md). Resolve the script path relative to this skill; the dated output belongs in the publication checkout, not necessarily beside the skill installation.

1. Finish and check the labelled `YYYY-MM-DD/script.md` and `sources.md` first. Dry-run the TTS command to validate splitting and speaker labels.
2. Read the Gemini key from `.gemini.key` in the working project root. The currently configured local key file is `/Users/xin/Projects/ai-morning-discovery/.gemini.key`; use it as the fallback when the working checkout has no key file. Load the key into `GEMINI_API_KEY` only in the child process environment. Accept a raw key or a `GEMINI_API_KEY=` / `GOOGLE_API_KEY=` assignment; parse as data rather than sourcing or executing the file. Never print the key, put it in command arguments, copy it to the dated folder, or stage it in Git.
3. Run `python3 <skill-directory>/scripts/gemini_tts.py <publication-checkout>/YYYY-MM-DD/script.md --two-speakers`. The script saves **`YYYY-MM-DD/podcast.m4a`** using its `audio_file_name` constant. Use the existing Gemini free-tier project configuration; no API parameter enforces free billing. Do not switch projects or models to bypass exhausted quotas.
4. The script uses macOS `afconvert` or installed `ffmpeg` to encode AAC/M4A. Check encoder availability before API requests. Temporary WAV input is cleaned up; resumable `.gemini-tts-cache/` PCM files are internal working artifacts. Keep caches out of publication. On a retry, reuse completed sections; replace an existing final file with `--overwrite` only when intentionally regenerating that edition.
5. Verify the final M4A is nonempty, decodable, and has a plausible duration. Inspect or listen to samples for speaker assignment and obvious omissions; do not claim a full listening review unless performed. Measure the actual audio duration and file byte length for the RSS enclosure rather than estimating them from text.
6. Only proceed to episode/feed publication once audio generation and checks succeed. If the key, API quota, encoder, or generation blocks completion, keep and deliver the local text artifacts, report the blocker, and leave the remote feed and episode unchanged. Do not publish a feed item pointing to missing audio.

## Publishing — GitHub

**Target repository:** https://github.com/francesliang/ai-morning-discovery

After checking `YYYY-MM-DD/script.md`, `YYYY-MM-DD/sources.md`, and `YYYY-MM-DD/podcast.m4a`, publish the dated episode folder **and the root `feed.xml`** in one commit when authenticated writing is available and publication is authorized. Keep other dates and channel metadata intact. Invocation authorizes the described workflow within applicable tool permissions; if an approval system still blocks a push, present the completed changes for the required approval rather than repeatedly retrying it.

1. Check repository access and its actual default branch. Pull or fetch the latest remote history before preparing changes, preserving existing work. Never assume a URL grants write access. The archive check and feed edit must use current remote contents.
2. Put the finished episode in `YYYY-MM-DD/` at the repo root. Include `script.md`, `sources.md`, `podcast.m4a`, and an optional intentional `briefing.md`. Exclude keys, `.env` files, caches, temporary audio, alternative audio versions, screenshots, and unrelated artifacts. If the date folder exists, update only intended episode files and preserve unrelated content.
3. Read the existing root `feed.xml` before modifying it. Preserve its RSS namespaces, channel metadata, existing items, and ordering convention. Match the existing date-based item names: `<title>YYYY-MM-DD</title>` and `<description>YYYY-MM-DD discovery</description>`. The current channel is `Personal AI Morning Discovery`, hosted at `https://francesliang.github.io/ai-morning-discovery/`.
4. Add the latest item at the front of the item list. For a new episode, use a unique date-based GUID (`<guid isPermaLink="false">YYYY-MM-DD</guid>`), an RFC 2822 publication timestamp with timezone, and an enclosure URL formed from the existing hosting base plus `/YYYY-MM-DD/podcast.m4a`. Set `length` to the actual M4A size in bytes, `type` to `audio/mp4` for AAC in M4A, and `itunes:duration` to the measured duration in `HH:MM:SS`. Follow the existing XML layout and date naming, but do not copy a mismatched GUID date, old audio basename, or incorrect `audio/mpeg` MIME type into a new item. On a rerun, locate the episode by date/title/enclosure, update the existing item rather than duplicating it, and preserve its established GUID so subscribers do not receive a duplicate episode. Do not rewrite unrelated historical items.
5. Parse the resulting XML to verify it is well formed. Check that the latest episode appears exactly once, its enclosure resolves to the intended dated file, its byte length and duration match the generated M4A, and existing entries remain. Before pushing, verify the enclosure path corresponds to the staged repository file; after publication, verify the hosted URL responds with audio once hosting has updated. If hosting is still deploying, report that separately from confirmed Git publication.
6. Stage only the intended episode files and root `feed.xml` by explicit path. Inspect the staged diff and confirm no key or cache is included. Commit with a descriptive message such as `Add Morning Discovery podcast for YYYY-MM-DD`, then push to the remote default branch. Make no empty commit if content is unchanged. If the audio exceeds the remote's supported file-size limit, report the concrete blocker; do not push a broken enclosure or silently change hosting.
7. On rejection or conflict, fetch and reconcile without force-pushing. Merge feed entries by episode identity, preserving concurrent episodes and avoiding duplicate GUIDs. Regenerate the feed metadata if the audio changed. Verify the remote contains the dated files and updated feed before reporting success, then return links to the episode folder, downloadable M4A, and feed.
8. If GitHub access or writing is unavailable, deliver the local dated files and prepared feed change, state that publication did not complete, and identify the missing access or approval. Do not claim remote publication or feed availability without confirmation.
