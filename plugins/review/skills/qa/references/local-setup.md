# Local Docker setup and recovery

The goal is a working, isolated application and browser session on the reviewed source. Do the setup instead of treating an unprepared environment as a terminal blocker. Apply the phases relevant to the repository; do not invent framework commands or upgrade the application stack to make QA easier.

## 1. Discover and allocate

Read repository instructions, setup documentation, Dockerfiles, Compose definitions, task runners, isolated-stack scripts, package locks, browser configuration, and environment examples. Reuse the supported entrypoint and dependency versions. Search for an existing isolated workflow before constructing an override.

The input must permit local provisioning and allocate an execution copy, resource namespace, and budgets. An absent running environment is expected in this mode. If the coordinator omitted these permissions, request that precise input repair; do not claim the application cannot run. Capture the execution copy's source identity and match it to the review target before setup. Build outputs and runtime state are separate from source changes.

Use a unique job namespace for containers, networks, databases, caches, records, and browser profiles. A Compose project name alone does not isolate fixed container names, external volumes, bind mounts, ports, or remote connection strings. Inspect those destinations without printing secrets. Keep the source checkout and other developers' resources intact. Log planned resources before creating them.

## 2. Establish Docker availability

Check the installed client, daemon, active context, and Compose support with their version, info, context, and help commands. A missing client, stopped daemon, inaccessible socket, and remote Docker context are different conditions. Do not confuse a sandbox denial with absence of Docker.

When the installed local runtime is stopped, try its documented start operation if the input and host permissions allow it, then wait for actual daemon readiness with a bounded health check. Do not switch to a shared remote daemon, change global Docker settings, or install a new host runtime silently. If tool access needs approval, send the exact blocked action and reason to the coordinator for the normal approval mechanism.

Prefer Docker for QA. If it is genuinely unavailable after diagnosis, use a supported isolated local fallback when the input permits it, recording the reason. Still attempt the real UI through Playwright when relevant. The absence of a Docker recipe alone is not proof of impossibility: use the project's locked runtime and a temporary job-local container setup when its required services and isolation are understood. Keep that setup out of product source.

## 3. Build and start the application

Run the repository's documented setup in the execution copy. Prepare declared writable mount directories, acquire pinned dependencies or images, initialize the new local database, apply existing migrations, and build frontend assets as required. Verify the targets before data writes. Use local service substitutes or documented test configuration for mail, storage, and external APIs; do not invent credentials or call live integrations to complete setup.

Provisioning permission covers routine job-local dependencies, project images, browser binaries, scratch configuration, and synthetic data within the declared budget and access. It does not authorize changing dependency versions, schema source, product code, global permissions, shared databases, or unrelated services. If a real application defect prevents startup, preserve the defect and its evidence rather than patching the reviewed code under the name of setup.

Start the required services and frontend process. Verify actual health and logs, then a relevant HTTP endpoint. Identify which source mount or built image the running app uses. A container listed as running does not prove application readiness or correct revision.

## 4. Diagnose the failing layer and recover

For each observed failure, record the command, sanitized error, diagnosis, chosen recovery, and verification result in the checkpoint. Try an applicable, evidence-based recovery before declaring that layer blocked. Do not retry the same failing command unchanged or exhaust a fixed number of arbitrary attempts.

| Symptom | Investigation and bounded recovery |
| --- | --- |
| Missing mount path or permission error | Inspect the actual bind and runtime user. Create or adjust only job-owned directories in the execution copy; do not recursively change permissions on the user's checkout. |
| Port conflict | Identify the listener and allocate a free job-local loopback port or override. Do not stop someone else's process. |
| Image pull, registry, or dependency failure | Separate authentication, rate limiting, network access, version mismatch, and resource exhaustion. Use an existing compatible pinned image or package cache when verifiable; otherwise report the exact missing access. Never silently substitute a different runtime version. |
| Container exits or health check fails | Read the specific service logs and prerequisites. Correct job-local setup, dependency startup order, or supported local configuration, then verify health again. |
| Database is empty or schema is missing | Verify the isolated target, apply the repository's existing migrations, then create minimal synthetic fixtures. Do not edit migrations, reuse production data, or mutate shared seed identities. |
| HTML loads but assets or interactions fail | Check frontend build output, dev-server readiness, asset paths, browser console, and failed requests. Run the documented build or frontend process and retry the actual interaction. |
| Service works inside Docker but the browser cannot reach it | Check container bind address, host mapping, base URL, local TLS, and which network the browser uses. Use a job-scoped loopback mapping or temporary proxy, or place the browser on the isolated network. Preserve external service isolation. |
| Browser package or binary is missing | Use the repository's pinned Playwright tooling and browser-install command in job-owned storage. If unavailable there, use an explicitly available compatible browser runtime or isolated Playwright environment. Verify a page launch before declaring the browser ready. |
| Login or fixture does not reach the changed flow | Create a synthetic account with the required permissions and domain state through documented local setup. Verify the session and route. Do not change a real person's account. |
| CPU, disk, or memory is exhausted | Reduce only this job's concurrency or footprint and reuse compatible existing artifacts. Remove only this job's known disposable resources. Never run a global prune to make space. |

The table is a diagnostic guide. State which causes actually applied and what was attempted. A different failure after a successful repair is progress to the next layer, not evidence that the whole environment is impossible.

## 5. Prove the interface works

For an affected UI, launch Playwright against the actual application, complete required authentication, navigate to the changed flow, and perform a representative action. Verify visible output and relevant persisted state. Capture the initial screenshot, console errors, failed requests, and exact local URL without credentials. A successful curl request, a login page screenshot, or source inspection alone does not establish that the changed UI works.

Then execute mapped, surface-regression, applicable accessibility and viewport checks, and the bounded exploratory pass. For an API-only or CLI-only target, document the absence of an applicable UI and exercise the real public interface instead. Do not claim browser coverage for it.

## 6. Continue or return an actionable blocker

Continue useful diagnostics while the cause is actionable and the budget permits it. The coordinator should allocate setup separately from scenario execution. If its own setup allowance was too small, it can extend that allowance when useful work remains and the user set no conflicting hard limit. Preserve the checkpoint across attempts. Do not spin indefinitely or bypass the user's explicit time or cost cap.

A genuine blocker identifies the failing layer, attempt and recovery evidence, affected scenarios, usable partial results, exact missing prerequisite or approval, next command or decision, and cleanup state. Missing external credentials, denied host access, unavailable required artifacts, an unfixed product startup defect, or an explicit user budget cap can be real blockers. An unstarted stack, missing fixtures, or a browser URL that has not been diagnosed is not sufficient by itself.

Clean up only job-owned containers, volumes, proxies, processes, data, and temporary authentication state. A global Docker runtime started during setup is not job-owned; record it and do not shut it down as ordinary cleanup. Preserve sanitized screenshots, traces, results, and logs in the assigned artifacts. Verify cleanup and report residue.
