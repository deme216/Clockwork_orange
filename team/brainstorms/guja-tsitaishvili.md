# Individual Problem Brainstorm

**CS-AI-2025 | Spring 2026 | Lab 1**

**Your Name:** Elguja Tsitaishvili
**GitHub Username:** guja-tsitaishvili
**Date:** 26 March 2026

---

## H1: Hassle

_What process in your daily life is tedious, error-prone, or needlessly manual?_

**WHO has this problem?**
Student developers and junior DevOps engineers who maintain small self-hosted projects (personal APIs, side-project backends, course assignment servers) and rely on terminal logs to debug deployment failures.

**PROBLEM in one sentence:**
When a deployment breaks at 2 AM, the developer must manually scroll through hundreds of lines of raw terminal output, Docker logs, and CI/CD pipeline errors to find the single misconfiguration or failed dependency that caused the crash.

**CURRENT SOLUTION:**
They copy-paste chunks of log output into a search engine or ChatGPT, often losing important context between pastes, or they `grep` for keywords like "error" and "failed" and hope the relevant line appears nearby.

**AI ANGLE:**
**Multimodal log analysis with screenshot understanding.** The developer takes a screenshot of their terminal (or pastes raw log text) and the AI uses vision + text reasoning to identify the root cause, trace it back to the specific config file or command, and suggest a fix — understanding both the visual layout of stacked error messages and the semantic content.

**WHY IT MATTERS:**
It turns a 30-minute frustrating debugging session into a 30-second interaction. For students learning DevOps for the first time, it also acts as a teaching tool — explaining _why_ the error happened, not just what to type to fix it.

---

## H2: Hardship

_What problem do you see in your community or country that affects real people?_

**WHO has this problem?**
Small guesthouse owners and family-run tourism operators in rural Georgia (Svaneti, Tusheti, Racha) who receive foreign visitors but cannot communicate effectively in English or other languages to describe local trails, cultural sites, or safety information.

**PROBLEM in one sentence:**
Language barriers between Georgian-speaking hosts and international tourists lead to missed experiences, safety misunderstandings on mountain trails, and negative reviews that hurt the local tourism economy.

**CURRENT SOLUTION:**
Hosts use Google Translate on their phones (which struggles with Georgian), rely on hand gestures, or depend on a younger family member who may speak some English to be physically present during every guest interaction.

**AI ANGLE:**
**Real-time multimodal translation with visual context.** The host photographs a trail sign, a menu, or a handwritten note in Georgian, and the AI provides a spoken or written translation that accounts for local context — for example, recognizing that "წყალი" on a hand-painted sign near a trail means "drinking water source" rather than just "water."

**WHY IT MATTERS:**
It directly increases income for rural families by improving guest satisfaction and review scores. It also removes the dependency on a single English-speaking family member, making the tourism business more resilient and scalable.

---

## H3: Horizon

_What new capability does multimodal AI unlock that was impossible 2 years ago?_

**WHO has this problem?**
Amateur gym-goers and home workout enthusiasts who follow exercise videos on YouTube or Instagram but have no coach to check whether their form is correct, risking injury from repeated poor technique.

**PROBLEM in one sentence:**
Watching a fitness video shows you _what_ the exercise should look like, but it cannot tell you that _your_ back is rounding on deadlifts or _your_ knees are caving inward on squats — feedback that requires a human coach watching in real time.

**CURRENT SOLUTION:**
They record themselves on their phone, then try to compare their video side-by-side with the tutorial, "eyeballing" differences. Some pay for online coaching ($50–150/month) where a coach reviews submitted videos asynchronously, with a 24–48 hour feedback delay.

**AI ANGLE:**
**Pose estimation and real-time visual feedback.** A multimodal model processes the user's live camera feed, estimates joint angles and body position using vision-based pose detection, and provides immediate spoken or on-screen corrections like "straighten your lower back" or "push your knees outward." Unlike older pose-estimation tools that only detected keypoints, a modern multimodal model can _reason_ about biomechanics — understanding that a rounded spine under load is dangerous, not just geometrically different.

**WHY IT MATTERS:**
It makes injury prevention accessible to anyone with a phone camera. Instead of paying for a coach or risking chronic injury from months of bad form, users get real-time, context-aware corrections that previously required a trained human standing next to them.

---

## Self-Assessment

| Your Problem           | Real Users | AI Diff. | Buildable | Global | Total | Passes? |
| ---------------------- | ---------- | -------- | --------- | ------ | ----- | ------- |
| H1: Log Debugger       | 2/3        | 2/3      | 3/3       | 2/3    | 9/12  | YES     |
| H2: Tourism Translator | 2/3        | 2/3      | 2/3       | 3/3    | 9/12  | YES     |
| H3: Form Coach         | 2/3        | 3/3      | 1/3       | 3/3    | 9/12  | YES     |

**Which of your three problems has the most specific WHO?**
**H2 (Tourism Translator).** I can picture the exact person — a guesthouse owner in Mestia who has a beautiful home and great food but loses bookings because they cannot answer questions on Booking.com in English.

**Which has the strongest AI angle (where AI is truly necessary, not just nice to have)?**
**H3 (Form Coach).** Traditional software can detect keypoints on a body, but only a multimodal reasoning model can understand _why_ a certain posture is dangerous in the context of a specific exercise and give a natural-language correction.

**Which would you fight hardest for if your team had to choose?**
**H1 (Log Debugger).** It is the closest to my own daily pain as a student learning DevOps, and I have the clearest idea of how to build and test it since I deal with broken deployments regularly.

**Is there a problem you thought of but discarded? What was it, and why did you drop it?**
I considered "AI-powered food calorie estimation from photos," but it has been done many times already (apps like MyFitnessPal and Lose It already offer this). It did not feel original enough for a 15-week project, and the accuracy ceiling for calorie estimation from a single photo is still unreliable even with current models.
