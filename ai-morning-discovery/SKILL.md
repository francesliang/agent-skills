---
name: morning-discovery
description: Produce a discovery-first spoken news briefing called Morning Discovery, covering the past 24 hours on weekdays and past 7 days on weekends (Australia/Melbourne). Use when asked to research popular Hacker News and Reddit discussions, Hugging Face Daily Papers and weekly popular papers/topics, or Last Week in AI podcast updates; create a source-linked single-narrator script, dated output folder, print the full script in chat for Read Aloud, and publish the folder to the configured GitHub repository when authorized access is available.
---

# Morning Discovery

Create a self-contained, natural-sounding **single-narrator monologue**, not a two-host script. Use the **Australia/Melbourne local date and time** to choose the reporting window: **Monday–Friday: rolling past 24 hours; Saturday–Sunday: rolling past 7 days**. State the exact reporting window and whether the edition is daily or weekend. On weekends, synthesize the week’s major developments rather than repeating each day’s headlines.

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

## Research and prioritization

1. Read the **News sources** table and research only enabled sources. Use the specified URLs as starting points, not as substitutes for verifying the actual story and opening relevant discussion threads. If a source is inaccessible, note the gap in `sources.md` rather than silently substituting a different source.
2. Apply the per-source ranking signal in the table. **Popularity first, personal relevance second**: an exceptionally discussed economic, political, cultural or scientific story should not be excluded for being unrelated to AI.
3. Include developments beyond popularity rankings when independently significant and new in the reporting window. Do not hardcode specific articles as mandatory inclusions.
4. Select the key stories that merit substantive explanations without imposing a fixed story count. Deduplicate overlapping coverage. Apply the appropriate weekday (24-hour) or weekend (7-day) window across news, paper discovery and podcast episodes. For Hugging Face, consult both daily and weekly popularity rankings; summarize notable weekly research themes as well as standout individual papers.
5. For weekend editions, review the entire past 7 days, rank the week’s most-discussed and consequential stories, and explain important developments across the week. Avoid reciting a seven-day chronology or repeating stories without new information.

## Reporting standards

- Verify the article, announcement, research findings and dates from primary sources where possible. Cite the original URLs.
- Make the distinction between **reported facts**, **community opinions**, **uncertainty** and **the narrator's own analysis** explicit. Never treat highly upvoted Reddit claims as verified news.
- For each story cover: **(a) what happened with concrete details, (b) why it matters, (c) the main points people are discussing or disagreeing about, (d) a memorable takeaway**. Summarise actual discussion arguments only after inspecting the discussion thread; otherwise label them as questions raised by the story.
- Prefer substance to generic headlines: tell listeners enough to understand the development even without opening the original link. Include relevant figures, comparisons and examples when verified.
- Do not manufacture metrics, quotes, research outcomes or consensus. Label snapshot popularity metrics and describe methodological limitations.
- Avoid forced thematic links between unrelated stories.

## Output

Always produce the complete, **single-host read-aloud script** as a UTF-8 Markdown file named `script.md`. Write in natural spoken paragraphs, with clear transitions and no tables or citations embedded in spoken sentences. Start with date, weekday/weekend edition label and reporting window, then substantive stories, then a short recap. Target around 10–20 minutes when enough verified stories merit coverage; prioritize depth and important stories over a rigid duration. No two-host dialogue.

Also output `sources.md` containing each story title, original article/paper/podcast URL, relevant Hacker News or Reddit discussion URL, retrieval date and any available votes/comments. Keep source links in this separate file so the monologue can be read aloud naturally. Produce `briefing.md` only if a concise skimmable version is useful.

Group artifacts in a folder named `YYYY-MM-DD/` using the **Melbourne local date** (e.g., `2026-11-08/script.md`, `2026-11-08/sources.md`). Return downloadable file links whenever file output is supported. If scheduled-task execution cannot write files, provide the full monologue and a companion source list as text, and clearly state the limitation.

## Read Aloud — print the script in chat

After generating `script.md`, **include its full text verbatim in the final chat response** so the user can press ChatGPT's **Read Aloud** control on the response. Do this on every run, whether or not GitHub publishing succeeds. Do not replace it with an abstract, teaser, link-only response, shortened summary, or "say start reading" invitation. Preserve the script's order, wording, and spoken paragraph breaks; do not insert source URLs, inline citations, stage directions, or status messages inside the narration.

Place the full script under a short heading such as **Morning Discovery — Read Aloud**, then put download links, `sources.md` links, and publishing status **after** the complete narration so they do not interrupt playback. Avoid duplicating the script elsewhere in the response. The user starts audio playback using ChatGPT's Read Aloud control; do not claim that audio playback starts automatically. If a response-length or environment limit prevents showing the full script, clearly disclose the limitation and provide the complete downloadable `script.md` file rather than silently truncating the narration.

## Publishing — GitHub

**Target repository:** https://github.com/francesliang/ai-morning-discovery

After generating and checking `YYYY-MM-DD/script.md` and `YYYY-MM-DD/sources.md`, **publish the entire date folder to this existing repository and git push it**, when an authenticated write-capable GitHub connection or `git` environment is available. Keep the repository's other dates and files intact.

1. Check repository access and its default branch. Never assume an unauthenticated connection can push or that a GitHub URL itself grants write access. Do not expose credentials or tokens in content or logs.
2. Pull or clone the current remote branch; preserve its history. Copy the generated date folder into the repo root as `YYYY-MM-DD/`. If the folder already exists, update only the intended files in that folder rather than deleting unrelated content.
3. Stage only the intended date-folder changes (`git add YYYY-MM-DD/`), inspect the diff, commit with a descriptive message such as `Add Morning Discovery briefing for YYYY-MM-DD`, then push to the remote default branch. If there is no change, do not make an empty commit.
4. If a push is rejected or conflicts arise, fetch and reconcile safely; do not force-push or overwrite others' work. Verify the remote contains the new files and report the resulting folder URL only after success.
5. If authorized GitHub writing or command execution is unavailable, **still deliver the local dated files**, state explicitly that the push was not completed, and say what connection or permission is missing. Never report a successful publication without confirmation.

Do not commit generated audio files or update podcast RSS unless specifically requested in a later change.
