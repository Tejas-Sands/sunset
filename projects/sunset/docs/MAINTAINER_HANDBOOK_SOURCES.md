# Open-source Maintainer Handbook: sources and editorial limits

This is an original CC0-1.0 SUNSET example resource, written for small open-source teams. It is a practical starting point rather than an official Git or GitHub manual, an expert-reviewed standard, or evidence of adoption. The checked-in pack is [maintainer-handbook.json](../public/packs/maintainer-handbook.json).

The pack contains four substantive procedures and sixteen concrete checklist items. Its prose, commands and checklist labels are inert plain text. There are no URLs, embedded markup, executable handlers or actual credentials in the resource. Source links live in this companion document so the guide itself remains readable offline without remote dependencies.

## Primary references checked on 3 November 2026

- [Git: git-reflog](https://git-scm.com/docs/git-reflog) establishes that reference history is local, that the default display concerns HEAD, and that reflog entries have expiry rules. The recovery procedure consequently starts in the original local repository and makes no recovery guarantee. No fixed retention period is promised.
- [Git: git-show](https://git-scm.com/docs/git-show) documents inspection of commit messages and changes. The guide asks the reader to inspect the summary and actual patch before selecting a candidate.
- [Git: git-branch](https://git-scm.com/docs/git-branch) documents creating a new branch at a selected start point without switching the working tree. The recovery example uses a new unused name and no overwrite flag.
- [Git: git-bundle](https://git-scm.com/docs/git-bundle) documents portable objects/references and the scope of --all. The guide distinguishes reachable Git history from working files, hosted project context and a complete operational backup.
- [Git: gitsubmodules](https://git-scm.com/docs/gitsubmodules) explains the separate repository boundary of a submodule. Retaining the parent alone is not presented as retaining every dependency.
- [GitHub: managing releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository) supports checking the selected tag/target, release notes, assets and draft before publication. The broader clean-environment package check and second-maintainer review are editorial recommendations, not claims that GitHub performs those checks.
- [GitHub: repository roles for an organization](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/managing-repository-roles/repository-roles-for-an-organization) supports matching access to responsibilities and distinguishing maintain permissions from administrative authority. Exact access can also depend on organization rules and configuration.
- [GitHub: managing deploy keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys) explains that repository deploy keys can remain active after their creator loses access. The handover procedure therefore inventories automation separately from people and directs changes through the responsible administrator.
- [GitHub: duplicating a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/duplicating-a-repository) documents the separate handling of Git Large File Storage objects. The handbook retains that boundary without reproducing the page's mirror-push or removal commands.

## Deliberate boundaries

The wording is original; the official references were used to check factual behavior, not copied into the pack. The CC0-1.0 designation concerns this original sample content and does not relicense the linked documentation.

Recovery covers a committed change whose object is still available. It does not recover arbitrary uncommitted files or guarantee recovery after expiry or object removal. COMMIT_ID is a plain-text placeholder that must be replaced with an inspected identifier. The branch name must be unused. The commands assume an ordinary local Git repository; this workspace's alternate metadata path is not a generic Git requirement.

The guide does not prescribe a reset, clean, force-push, merge or checkout. The only recovery mutation shown is naming the inspected commit on a new branch. Bundle creation writes a separate file and calls for a new filename. No command in the prose was run as part of writing it, and no repository recovery, hosted release, permission change or signing action is claimed.

Secret values never belong in this public resource. Access inventory, handover sequencing, independent retained copies and representative offline checks are editorial operating practices; they are not a security audit or a guarantee of complete continuity. The sample contains no finance or legal procedure. Actual reader/export/offline verification is recorded separately by the implementation and browser evidence, not established by this content file.
