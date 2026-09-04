# OMEN preprint: submission checklist

## Before you upload
- [ ] Fill in **Correspondence email** and **ORCID iD** on the title page
      (edit `build_paper.js`, search for "Correspondence:", then rebuild).
- [ ] Get an ORCID iD (free, 2 minutes): https://orcid.org/register
- [ ] Push the code to a public GitHub repo (omen.py, test_omen.py, audit/, LICENSE, CITATION.cff).
- [ ] Archive a release on Zenodo to mint a DOI:
      Zenodo -> log in with GitHub -> enable the repo -> tag a release (v0.1) on GitHub.
- [ ] Put the repo URL and the Zenodo DOI into the **Data and Code Availability**
      section (edit `build_paper.js`, search for "[add repository URL]"), then rebuild.

## Rebuild the paper
```
cd Desktop\omen
node build_paper.js                                  # writes OMEN_whitepaper.docx
soffice --headless --convert-to pdf OMEN_whitepaper.docx
```

## Upload to SportRxiv (free, no fee)
1. https://sportrxiv.org -> Register / Log in.
2. New submission -> upload `OMEN_whitepaper.pdf`.
3. Title: OMEN: Open Movement and Exercise Nomenclature
4. Abstract: paste from the paper (the Abstract section).
5. Keywords: resistance training; exercise nomenclature; controlled vocabulary;
   faceted classification; ontology; data interoperability; movement patterns
6. Licence: CC BY 4.0 is the usual choice for a preprint.
7. Declare: no funding, no competing interests.

## After the preprint is live
- [ ] Add the preprint DOI to your site and to the repo README.
- [ ] Optional next step for a journal: run the inter-annotator study
      (3-5 people encode ~30 movements), then submit to
      Frontiers in Sports and Active Living (Technology & Code) or
      Sports Medicine - Open.
