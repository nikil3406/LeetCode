(() => {
  "use strict";

  let busy = false;

  const sleep = ms => new Promise(r => setTimeout(r, ms));

  function slug() {
    const m = location.pathname.match(/\/problems\/([^/]+)/);
    return m ? m[1] : null;
  }

  function csrf() {
    const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  }

  async function config() {
    return await chrome.storage.local.get({ apiUrl: "", archiveToken: "" });
  }

  async function gql(query, variables) {
    const token = csrf();
    const r = await fetch("https://leetcode.com/graphql", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { "x-csrftoken": token } : {})
      },
      body: JSON.stringify({ query, variables })
    });
    if (!r.ok) throw new Error(`LeetCode HTTP ${r.status}`);
    const data = await r.json();
    if (data.errors?.length) throw new Error(data.errors.map(x => x.message).join("; "));
    return data;
  }

  async function submissions(problemSlug) {
    const q = `
      query submissionList($offset: Int!, $limit: Int!, $questionSlug: String) {
        submissionList(offset: $offset, limit: $limit, questionSlug: $questionSlug) {
          hasNext
          submissions {
            id title titleSlug statusDisplay lang runtime timestamp url memory
          }
        }
      }`;

    const all = [];
    let offset = 0;
    const limit = 20;

    while (true) {
      const r = await gql(q, {
        offset,
        limit,
        questionSlug: problemSlug
      });

      const page = r?.data?.submissionList;
      const batch = page?.submissions || [];
      all.push(...batch);

      if (!page?.hasNext || batch.length === 0) break;
      offset += limit;
    }

    return all;
  }

  async function details(id) {
    const q = `
      query submissionDetails($submissionId: ID!) {
        submissionDetails(submissionIdV2: $submissionId) {
          runtime runtimeDisplay runtimePercentile
          memory memoryDisplay memoryPercentile
          code timestamp statusCode
          user { username }
          lang { name verboseName }
          question { questionId titleSlug hasFrontendPreview }
          runtimeError compileError lastTestcase codeOutput expectedOutput
          totalCorrect totalTestcases fullCodeOutput testDescriptions testBodies testInfo stdOutput
        }
      }`;
    const r = await gql(q, { submissionId: String(id) });
    return r?.data?.submissionDetails;
  }

  async function problem(problemSlug) {
    const q = `
      query questionData($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
          questionId questionFrontendId title titleSlug difficulty content
        }
      }`;
    const r = await gql(q, { titleSlug: problemSlug });
    return r?.data?.question;
  }

  function toast(message) {
    document.getElementById("lca-toast")?.remove();
    const x = document.createElement("div");
    x.id = "lca-toast";
    x.textContent = message;
    Object.assign(x.style, {
      position: "fixed", right: "20px", bottom: "20px", zIndex: 999999,
      padding: "12px 16px", borderRadius: "10px",
      background: "#111827", color: "#fff", font: "14px Arial",
      boxShadow: "0 8px 24px rgba(0,0,0,.25)"
    });
    document.body.appendChild(x);
    setTimeout(() => x.remove(), 5000);
  }

  async function run() {
    if (busy) return;
    const s = slug();
    if (!s) return;
    busy = true;

    try {
      const before = await submissions(s);
      const previous = before[0]?.id ?? null;

      let result = null;
      for (let i = 0; i < 15; i++) {
        await sleep(2000);
        const current = await submissions(s);
        if (current[0] && String(current[0].id) !== String(previous)) {
          result = { current, newest: current[0] };
          break;
        }
      }

      if (!result) {
        console.warn("[LeetCode Auto Archive] New submission not detected.");
        return;
      }

      toast("⏳ Archiving submission...");
      const d = await details(result.newest.id);
      const p = await problem(s);
      const c = await config();

      if (!c.apiUrl || !c.archiveToken) {
        throw new Error("Extension settings are not configured.");
      }
      if (!d?.code) throw new Error("LeetCode did not return submission code.");

      const r = await fetch(`${c.apiUrl.replace(/\/$/, "")}/archive-submission`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Archive-Token": c.archiveToken
        },
        body: JSON.stringify({
          problem: {
            question_number: String(p.questionFrontendId),
            title: p.title,
            slug: p.titleSlug,
            difficulty: p.difficulty,
            content: p.content
          },
          submission: result.newest,
          details: d,
          all_submissions: result.current
        })
      });

      const body = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(body.detail || `Archive API HTTP ${r.status}`);

      console.log("[LeetCode Auto Archive] ✓", body);
      toast("✓ Submission archived to GitHub");
    } catch (e) {
      console.error("[LeetCode Auto Archive]", e);
      toast("⚠ Archive failed. Check Console.");
    } finally {
      busy = false;
    }
  }

  document.addEventListener("click", e => {
    const el = e.target instanceof Element ? e.target : null;
    const button = el?.closest("button");
    if (!button) return;
    const text = (button.innerText || button.textContent || "").trim().toLowerCase();
    if (text.includes("submit")) setTimeout(run, 800);
  }, true);

  console.log("[LeetCode Auto Archive] Loaded:", slug());
})();