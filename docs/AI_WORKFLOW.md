# AI Workflow

This project was built in close collaboration with Claude (Anthropic), used as an active pair-programming partner rather than a one-shot code generator. This doc covers how it was used, what I accepted as-is, what I pushed back on or corrected, and the decisions that were mine to make regardless of what the AI proposed.

## How the workflow actually went

Roughly in order:

1. **Requirements doc first, before any code.** I asked Claude to draft the one-page requirements doc from the assessment brief. I reviewed the scope cuts it proposed (no 
   auth, no FX conversion, no payroll/tax, no CSV import/export) and the reasoning behind each, and approved them as written — these matched my own read of what the exercise was actually testing.

2. **Backend scaffolded incrementally, not all at once.** Models → schemas → CRUD layer → routers → app entrypoint, each verified running before moving to the next 
   (Claude actually executed the code against a test client at each step rather than just writing it and assuming it worked — I asked for this explicitly after the first pass, and it caught real issues, see below).

3. **I asked for a full code walkthrough before moving on.** Once the backend scaffold was in place, I had Claude explain every file line-by-line — the indexing choices,
   the append-only salary history design, why Pydantic schemas are separate from SQLAlchemy models. This wasn't just for my own understanding; it's also how I caught that the reasoning behind each decision actually held up rather than just accepting code that looked plausible.

4. **I made the job-level taxonomy decision myself.** The initial proposal was junior/mid/senior/lead; I changed it to junior/mid/senior/lead/manager/ceo specifically so 
   the `manager_id` hierarchy would tell a real organizational story instead of being arbitrary.

5. **Frontend scaffolded with an explicit design brief.** I asked for a restrained, information-dense UI appropriate for an internal HR tool rather than a flashy 
   consumer-app aesthetic — Claude proposed a specific palette and rationale (single indigo accent, tabular-nums for salary columns) before writing any component code, which I approved before it proceeded.

6. **Deployment was the most hands-on-keyboard part.** Claude gave step-by-step instructions for Railway/Vercel, but I was the one clicking through the actual 
   dashboards, pasting real error messages and screenshots back for diagnosis at each failure.

## Bugs the AI introduced and how they were caught

Worth being specific about this rather than implying everything worked first try — it didn't, and the catches are arguably more informative than the code itself.

**Currency-mixing in analytics.** The first version of the pay-statistics aggregation averaged `SalaryRecord.amount` across all employees in a group regardless of currency — so a USD salary and an INR salary got summed as if they were the same unit. This wasn't caught by reading the code; it was caught by actually running the seeded analytics endpoint and noticing the average was wildly inconsistent with the median and max for the same group. The fix: group by `(dimension, currency)` instead of `dimension` alone, so no response row ever mixes currencies. This is now a regression test (`test_pay_stats_never_mixes_currencies` in `backend/tests/test_analytics.py`).

**Invalid emails from generated names.** The seed script's email-building logic stripped apostrophes from Faker-generated names but not periods. Faker occasionally generates names with titles/suffixes like "Mr. Brandon Lopez MD", which produced emails like `mr..brandon.lopez.md@acme-corp.com` — invalid per Pydantic's `EmailStr` validation, which only surfaced when I ran the seed script and hit the live API locally (it hadn't shown up in Claude's own test run, since it depends on which random names Faker happens to generate). Fixed by stripping all non-letter characters before building the email, verified against all 10,000 generated emails afterward.

**CORS trailing-slash mismatch during deployment.** Not a code bug, but worth noting: `FRONTEND_ORIGIN` was set to the Vercel URL with a trailing slash, which never matches the `Origin` header a browser actually sends. Diagnosed by comparing the exact string against what CORS requires, not by guessing.

## What I did not just accept

- The original analytics aggregation code *looked* correct — no syntax errors, ran without exceptions, returned a response. I didn't sanity-check the actual numbers until 
  I asked to see it running against real seeded data, which is what surfaced the currency bug above. Lesson applied going forward: passing code review isn't the same as producing correct output.
- I chose Postgres over the SQLite default suggested for "quick start" once we got to deployment, since the assessment scenario (10,000 employees, real org) called for it, 
  even though SQLite would have been less setup friction.
- I decided against building CSV import/export even though it's the closest analog to the spreadsheet workflow being replaced — Claude flagged this as the scope cut most 
  likely to be questioned, and I agreed to leave it as a documented fast-follow rather than build it under time pressure.
- After deploying and actually using the app myself (not just testing it), I noticed the employee list paginated into 400 pages of Previous/Next-only 
  navigation — technically correct, but painful for anyone who needed to browse rather than search. I asked whether this was actually the right approach before accepting it as-is. The fix that came out of that discussion was deliberately restrained: an adjustable page size (25/50/100) and a jump-to-page control, not infinite scroll or virtualization — because the requirements doc's own jobs-to-be-done say the primary workflow is search/filter to find someone specific, not paging through all 10,000
  employees. Reaching for the more complex UI pattern would have been solving a problem the tool doesn't actually have.