# Submission proposal

[Download the proposal PDF](GBS_Algorithm_Proposal.pdf) · [Editable LaTeX source](GBS_Algorithm_Proposal.tex)

This is the complete four-page project proposal and AI-assisted prototype report for the optional BlueQubit upload. It covers the research objective, physics, sampler, error mechanism, measured prototype, comparator limitations, AI workflow, three-month plan, resources, and references. It uses the existing smoke measurements rather than presenting new experiments.

## Verified form requirements

The [live Quantum Flywheel form](https://docs.google.com/forms/d/e/1FAIpQLSdGwhevKLEn71C9bRBf8eGHCJ3rp4XwiaDayhMuaId5H8rAEQ/viewform) was inspected on October 12, 2026. The optional section is labeled “Proposal PDF (AI generated)” and asks for a prototype or proposal-section report. Its limits are:

- **Maximum four pages**, rather than ten. All references are included within our four pages.
- **One PDF**, with a maximum file size of **10 MB**.
- Demonstrate use of AI to organize computational experiments or simulations. The report describes the actual AI-assisted workflow and its independent numerical checks.

The form links an [AI-agents tutorial](https://app.bluequbit.io/tutorial/ai-agents-quantum-research) as a suggested reference. It does not state that using that tutorial, a BlueQubit account, or credits is mandatory for this upload. No additional font, margin, or citation-format requirement was shown in the inspected upload section. The form describes selected projects lasting up to three months and expects public research outputs.

The proposal is **four pages including references**, about 235 KB, with an 11-point body font, embedded fonts, and clickable citations. The PDF is not encrypted and contains no JavaScript. The final pages were rendered and visually inspected. [Validation details](Submission_Validation.json) record the exact final size and hashes.

This update creates a submission file; it does not upload or submit the application. Personal form-answer drafts remain ignored by Git.

## Rebuild

The source is standalone: bibliography and tables are included, with no external figures or data files required. It uses standard LaTeX packages and compiles with pdfLaTeX. The built-in Codex LaTeX compiler and local MiKTeX both confirmed compilation. To export a fresh PDF from this directory:

```powershell
New-Item -ItemType Directory -Force -Path ../../temp/gbs-proposal | Out-Null
pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape -output-directory=../../temp/gbs-proposal GBS_Algorithm_Proposal.tex
pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape -output-directory=../../temp/gbs-proposal GBS_Algorithm_Proposal.tex
```

Check that both commands succeed, the PDF remains within four pages/10 MB, references resolve, and the pages render correctly. After verification, move the new PDF from `../../temp/gbs-proposal/` to this directory to replace the published `GBS_Algorithm_Proposal.pdf`. Temporary build files and page renders remain locally in the repository's ignored `temp/gbs-proposal/` folder; the finished PDF remains tracked here in `proposal/`. The source links the immutable `0a2bc00` evidence snapshot so its claims can be checked even after later algorithm changes.
