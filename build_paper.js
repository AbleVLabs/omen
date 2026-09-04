/*
 * Builds the OMEN white paper as a .docx.
 * Run: NODE_PATH=/usr/local/lib/node_modules_global/lib/node_modules node build_paper.js
 */
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  PageNumber, Header, Footer, TableOfContents, PageBreak, LevelFormat, ImageRun,
} = require("docx");
const fs = require("fs");

// ---- palette / type ------------------------------------------------------
const INK = "1a1a1a", MUTE = "5a5a5a", ACCENT = "6a2c91", RULE = "cccccc",
      CODEBG = "f2eef7";
const SERIF = "Georgia", SANS = "Calibri", MONO = "Consolas";

// ---- helpers -------------------------------------------------------------
const P = (opts) => new Paragraph(opts);
function body(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 140, line: 276 },
    alignment: AlignmentType.JUSTIFIED,
    children: runs(text),
    ...opts,
  });
}
// inline markup: **bold**, *italic*, `mono`
function runs(text) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: SERIF, size: 21, color: INK }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, font: SERIF, size: 21, color: INK }));
    else if (t.startsWith("`")) out.push(new TextRun({ text: t.slice(1, -1), font: MONO, size: 19, color: ACCENT }));
    else out.push(new TextRun({ text: t.slice(1, -1), italics: true, font: SERIF, size: 21, color: INK }));
    last = re.lastIndex;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: SERIF, size: 21, color: INK }));
  return out;
}
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 140 },
    children: [new TextRun({ text, font: SANS, bold: true, size: 30, color: ACCENT })],
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2, spacing: { before: 220, after: 100 },
    children: [new TextRun({ text, font: SANS, bold: true, size: 24, color: INK })],
  });
}
function bullet(text) {
  return new Paragraph({ bullet: { level: 0 }, spacing: { after: 90, line: 268 }, children: runs(text) });
}
function numbered(text, ref) {
  return new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 90, line: 268 }, children: runs(text) });
}
function code(text) {
  return new Paragraph({
    spacing: { before: 60, after: 120 }, shading: { type: ShadingType.CLEAR, fill: CODEBG },
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: ACCENT, space: 8 } },
    children: [new TextRun({ text, font: MONO, size: 17, color: INK })],
  });
}
function figure(file, w, h) {
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 140, after: 60 },
    children: [new ImageRun({ data: fs.readFileSync(file), transformation: { width: w, height: h } })] });
}
function caption(text) {
  return new Paragraph({ spacing: { after: 180 }, children: [new TextRun({ text, font: SANS, italics: true, size: 17, color: MUTE })] });
}

// ---- tables --------------------------------------------------------------
const TOTAL = 9360; // Letter content width (dxa) with 1.15in margins
function cell(text, w, { head = false, mono = false, bold = false } = {}) {
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    shading: head ? { type: ShadingType.CLEAR, fill: ACCENT } : { type: ShadingType.CLEAR, fill: "ffffff" },
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [new Paragraph({ children: [new TextRun({
      text, font: mono ? MONO : SANS, size: mono ? 16 : 18,
      bold: head || bold, color: head ? "ffffff" : INK,
    })] })],
  });
}
function table(headers, rows, widths) {
  const mk = (cells, head) => new TableRow({
    tableHeader: head,
    children: cells.map((c, i) => cell(c, widths[i], { head, mono: !head && (c.__mono || false) })),
  });
  // allow per-cell mono via {t, mono}
  const norm = (r) => r.map((c) => (typeof c === "object" ? c : { toString: () => c, __plain: c }));
  const bodyRows = rows.map((r) => new TableRow({
    children: r.map((c, i) => {
      const isMono = typeof c === "object" && c.mono;
      const txt = typeof c === "object" ? c.t : c;
      return cell(txt, widths[i], { mono: isMono });
    }),
  }));
  return new Table({
    columnWidths: widths,
    width: { size: TOTAL, type: WidthType.DXA },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: RULE },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: RULE },
      left: { style: BorderStyle.SINGLE, size: 4, color: RULE },
      right: { style: BorderStyle.SINGLE, size: 4, color: RULE },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: RULE },
      insideVertical: { style: BorderStyle.SINGLE, size: 2, color: RULE },
    },
    rows: [mk(headers, true), ...bodyRows],
  });
}

// =========================================================================
// CONTENT
// =========================================================================
const children = [];

// ---- title block ----
children.push(
  new Paragraph({ spacing: { before: 1400, after: 0 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "OMEN", font: SANS, bold: true, size: 76, color: ACCENT })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 260 },
    children: [new TextRun({ text: "Open Movement & Exercise Nomenclature", font: SANS, size: 30, color: INK })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 },
    children: [new TextRun({ text: "A Generative, Computable Naming Standard for Resistance-Training Movements", font: SERIF, italics: true, size: 24, color: MUTE })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 520, after: 0 },
    children: [new TextRun({ text: "Carlos Abel Vivanco", font: SANS, size: 24, color: INK })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 },
    children: [new TextRun({ text: "Independent Researcher", font: SANS, size: 20, color: MUTE })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 140 },
    children: [new TextRun({ text: "Correspondence: research@ablevlabs.com   ·   ORCID: 0009-0001-0178-7752", font: SANS, size: 17, color: MUTE })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 },
    children: [new TextRun({ text: "This manuscript is a preprint and has NOT been peer reviewed.", font: SANS, italics: true, size: 17, color: MUTE })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 320 },
    children: [new TextRun({ text: "Preprint  ·  Standard version 0.2  ·  September 2026", font: SANS, size: 18, color: MUTE })] }),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---- abstract ----
children.push(h1("Abstract"));
children.push(body("Resistance-training movements are named inconsistently across research, coaching, and software, and the cost of that inconsistency is now concrete: the same exercise appears under many names in the scientific literature, every exercise database invents its own schema, and no shared identifier lets a training log, a research dataset, and a coaching app refer to the same movement without ambiguity. Practitioner surveys confirm the problem is real and that professionals want it fixed, but the reforms proposed so far are style guidelines (recommended word orders) rather than computable standards. This paper proposes **OMEN** (Open Movement & Exercise Nomenclature): a generative naming standard that describes a movement as a bundle of orthogonal facets, derives its target musculature from its movement pattern rather than treating muscle as an input, and produces two deterministic outputs: a human-readable canonical string and a short, stable, language-neutral identifier suitable as a database primary key. OMEN separates three layers that existing systems conflate (the structured facet record, the canonical identifier, and the curated display name), the same separation that let systematic naming succeed in chemistry (SMILES, InChI) and clinical terminology (SNOMED CT). We give the facet schema and its controlled vocabularies, a fixed serialization order, a defaults mechanism that keeps everyday names short, a governance and versioning model, and an evaluation protocol centered on inter-annotator agreement. A working reference encoder and test suite accompany the standard; every canonical string and identifier in this paper is produced by that implementation. We also report an evaluation against two independent public databases. Of 678 resistance-training records in the Free Exercise DB, **84.7%** are expressible without inventing a term (**91.4%** of those whose own fields disclose enough to encode at all); on a second corpus, wger, only **1.9%** of records require a term the standard lacks. The residual gap in both corpora is a single principled category, the multi-phase Olympic lifts. 574 distinct source names collapse to 304 keys, exposing synonymy directly; **81%** of those names never state posture; and no key collision occurs across **6,054,048** generated records. A crosswalk mapping every audited record to its key is released with the standard. The inter-annotator study on which a naming standard ultimately rests is specified, with its materials published, but has not been run."));

children.push(new Paragraph({ spacing: { before: 120 }, children: [new TextRun({ text: "Keywords: ", font: SANS, bold: true, size: 18, color: INK }), new TextRun({ text: "resistance training; exercise nomenclature; controlled vocabulary; faceted classification; ontology; data interoperability; movement patterns", font: SANS, size: 18, color: MUTE })] }));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ---- TOC ----
children.push(h1("Contents"));
[["1.","Introduction"],["2.","Background and Related Work"],["3.","Design Principles"],
 ["4.","The OMEN Model"],["5.","Canonical Forms and Identifiers"],["6.","Worked Examples"],
 ["7.","Reference Implementation"],["8.","Evaluation Protocol"],["9.","Results"],
 ["10.","Governance and Versioning"],["11.","Limitations and Future Work"],["12.","Conclusion"],
 ["","Data and Code Availability"],["","Author Contributions"],
 ["","Use of Generative AI"],["","Funding"],["","Conflicts of Interest"],
 ["","References"]].forEach(([n,t]) =>
  children.push(new Paragraph({ spacing: { after: 60 }, indent: { left: 240 },
    children: [new TextRun({ text: (n ? n + "  " : "     ") + t, font: SANS, size: 20, color: INK })] })));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ---- 1. Introduction ----
children.push(h1("1. Introduction"));
children.push(body("Ask ten trainers to name a common movement and you will get several answers: arm curl, bicep curl, biceps curl; one-arm row, single-arm row, 1-arm dumbbell row. This is not a matter of taste with no consequences. A survey of 205 exercise professionals found that terminology for resistance-training exercises is used inconsistently, that most respondents use multiple names for the same exercise, and that a majority support standardization (Jackson et al., 2013). A later text analysis of the exercise names in a standard technique manual found 35 distinct naming patterns among just 57 exercises (Nuzzo, 2017). The inconsistency reaches into the literature itself: across research articles, the same movement is written many different ways, so that anyone assembling or comparing datasets must first reconcile names by hand (Nuzzo, 2021)."));
children.push(body("The problem is worth solving because exercise data is increasingly computed on, not just read. Training logs are analyzed for volume and balance; wearable and app ecosystems exchange workout records; sports-science studies pool across sources; recommendation systems reason over exercise catalogs. Every one of these tasks needs a stable, unambiguous way to say *which movement*: a shared key. Today there is none. Each exercise database defines its own fields and its own names, and the identifiers they do expose are typically derived from the display name itself, so they break the moment the name is written differently."));
children.push(body("Two families of prior work bear on this, and neither closes the gap. On the practitioner side, standardization has been proposed as a **naming pattern**, for example specification, then equipment, then exercise, yielding names like “1-arm dumbbell row” (Jackson et al., 2013). This is a valuable style guideline, but it is not computable: it fixes word order without fixing a vocabulary, an identifier, or a way for software to tell whether two names denote the same movement. On the biomedical side, rigorous ontologies exist for physical activity and exercise (PACO, the exercise-medicine and prescription ontologies, and a recent kinetic human-movement ontology), but they are built for epidemiology, clinical prescription, and anatomical modeling, not to serve as the interoperable naming key that training logs and strength-science datasets share."));
children.push(body("This paper proposes a standard aimed squarely at that unfilled middle. **OMEN** treats a movement as a structured record of orthogonal facets, generates a canonical form and a stable identifier from that record deterministically, and keeps human names as a curated presentation layer rather than as the identity itself. The contribution is fourfold: (i) a facet schema and controlled vocabularies for resistance-training movements; (ii) a canonical serialization and a versioned, language-neutral identifier scheme; (iii) a governance and evaluation model designed for global adoption; and (iv) an open reference implementation that produces every canonical string in this paper."));

// ---- 2. Background ----
children.push(h1("2. Background and Related Work"));
children.push(body("Existing efforts fall into three layers. Each is useful and none is a computable naming standard for resistance-training movements; OMEN is designed to unify their strengths."));

children.push(h2("2.1 Practitioner naming guidelines"));
children.push(body("The closest direct precedent is the proposal to standardize resistance-exercise names around a fixed pattern of specification, equipment, and exercise (Jackson et al., 2013). The follow-up text analysis quantified the underlying chaos and, usefully for our purposes, categorized the words people actually use in exercise names (Nuzzo, 2017). Table 1 reproduces that breakdown, because it is essentially an empirical inventory of the facets a standard must cover."));
children.push(table(
  ["Word category", "Share", "Example"],
  [
    ["Action", "30.3%", "row"],
    ["Equipment", "23.4%", "barbell"],
    ["Body part", "19.1%", "shoulder"],
    ["Equipment position", "8.0%", "incline"],
    ["Body position", "7.0%", "seated"],
    ["Action direction", "5.9%", "lateral"],
    ["Miscellaneous", "4.3%", "power"],
    ["Body-part adjective", "1.1%", "stiff"],
    ["Body-position direction", "1.1%", "over"],
  ],
  [3400, 1400, 4560],
));
children.push(caption("Table 1. Word categories in resistance-exercise names, after Nuzzo (2017). Read as facets, action dominates: evidence that the movement itself, not the muscle, is the natural primitive."));
children.push(body("Two things stand out. First, **action** (the movement) is the single largest category, which supports treating the movement pattern, rather than the muscle, as the classificatory primitive. Second, a later analysis argued that eccentric and other muscle-action distinctions add yet another axis the existing conventions do not handle (Sports Medicine – Open, 2023). A durable standard must therefore make contraction type a first-class, optional facet. What this layer lacks is everything that makes a standard computable: a closed vocabulary, a canonical form, and a stable identifier."));

children.push(h2("2.2 Open exercise databases"));
children.push(body("Community databases such as Free Exercise DB and wger already decompose exercises into fields, and their choices independently validate two OMEN design decisions. Free Exercise DB stores `force` (push/pull/static), `mechanic` (compound/isolation), `equipment`, and, crucially, `primaryMuscles` and `secondaryMuscles` as separate lists rather than a single “muscle” slot. That is exactly the treatment OMEN gives musculature. However, these schemas bury posture, grip, laterality, and bench angle inside the free-text name; they carry only a coarse push/pull axis rather than a true movement-pattern taxonomy; and their record identifiers are slugs derived from the display name (for example, `Alternate_Incline_Dumbbell_Curl`), which are neither stable nor canonical and cannot be mapped across databases. There is no shared key that lets two of these datasets refer to the same movement."));

children.push(h2("2.3 Biomedical and activity ontologies"));
children.push(body("A parallel body of rigorous work models physical activity and exercise as formal ontologies: the Physical Activity Concept Ontology (PACO) standardizes activity descriptions drawn from questionnaires; exercise-medicine and prescription ontologies support individualized clinical exercise programs; and a recent kinetic human-movement ontology represents the anatomy and physiology of movement in a description-logic model. These are valuable and OMEN aligns with their methods: controlled terms, defining relationships, open publication. But their purpose is epidemiology, clinical prescription, or anatomical reasoning, not the naming of gym movements for interoperable logging. They answer “what is physical activity, clinically?” rather than “what is the shared identifier for a single-arm cable row?” OMEN occupies that unclaimed niche and is designed to reference the anatomical ontologies for its muscle terms rather than to duplicate them."));

// ---- 3. Design principles ----
children.push(h1("3. Design Principles"));
children.push(body("A standard intended for worldwide adoption succeeds on properties that have little to do with the elegance of its taxonomy; chemistry and clinical terminology adopted their systems for governance, stable identifiers, and tooling as much as for content. OMEN is built to the following principles."));
const dp = [
  ["Unambiguous.", "One movement has exactly one canonical form. Two encoders, given the same movement, must produce the same identifier."],
  ["Complete but bounded.", "Every everyday resistance movement is expressible, using closed controlled vocabularies rather than free text, so that validity is checkable."],
  ["Generative, not enumerative.", "The standard is a grammar, not a list. It can name a movement invented next year by composing existing facets, as systematic chemical naming can name a novel compound."],
  ["Human and machine readable.", "The same record renders as a short human name and as a precise machine key, without either compromising the other."],
  ["Stable, versioned identifiers.", "Identifiers are language-neutral, permanent, and carry the standard's version, so a citation resolves to the same movement forever and changes to the standard never silently reinterpret old data."],
  ["Backward-compatible.", "Existing colloquial names map onto canonical records as curated aliases, so the standard augments rather than discards the vocabulary people already use."],
  ["Anatomically complete.", "For every joint the standard covers, it provides the full set of that joint's actions, not only those that happen to be common in a gym. Completeness is a checkable property rather than an aspiration: for each action the vocabulary must contain its anatomical counterpart."],
  ["Governed and open.", "An open specification, an open reference implementation, and a defined process for proposing and ratifying new terms: the machinery by which a standard actually spreads."],
];
dp.forEach(([t, d]) => children.push(bullet(`**${t}** ${d}`)));

// ---- 4. The OMEN model ----
children.push(h1("4. The OMEN Model"));
children.push(h2("4.1 Three layers"));
children.push(body("OMEN keeps three representations of a movement distinct. Conflating them is the single most common failure of existing schemes, and separating them is what every durable naming system does."));
children.push(numbered("**The facet record** is the source of truth: a movement is a bundle of orthogonal facets (Section 4.2). It is the only thing a human authors.", "layers"));
children.push(numbered("**The canonical form and key** are derived deterministically from the record (Section 5). The canonical string is human-inspectable; the key is a short, stable identifier suitable as a primary key.", "layers"));
children.push(numbered("**The display name** is a curated label, “Bench Press,” attached to the record as an alias (Section 4.4). It is never generated and never the identity, so it is free to be localized.", "layers"));
children.push(body("A consequence worth stating plainly: in OMEN the **exercise name is an output, not an input.** You describe a movement by its facets, and “bench press” is the label those facets resolve to, not one of the coordinates you supply. This is what removes the redundancy and the contradictions (a record whose name says one thing and whose fields say another) that fixed-word-order schemes permit."));
children.push(figure("fig1_three_layers.png", 500, 357));
children.push(caption("Figure 1. The three layers OMEN keeps distinct. The facet record is authored; the canonical form and key are generated from it; the display name is a curated alias attached to the record. Conflating these layers is the characteristic failure of existing schemes."));

children.push(h2("4.2 The facets"));
children.push(body("A movement is described by three required facets (posture, implement, and movement pattern) together with laterality, which has a default, and a set of optional modifiers. Table 2 lists the facets and a representative slice of each controlled vocabulary; the reference implementation holds the complete lists."));
children.push(table(
  ["Facet", "Role", "Representative controlled terms"],
  [
    [{t:"posture"}, "required", "standing, seated, supine, prone, kneeling, bent-over, hanging"],
    [{t:"implement"}, "required", "barbell, dumbbell, ez-bar, cable, machine, kettlebell, bodyweight, band"],
    [{t:"pattern"}, "required", "horizontal-push, vertical-pull, hip-hinge, squat, elbow-flexion, …"],
    [{t:"laterality"}, "default", "bilateral (default), unilateral, alternating"],
    [{t:"attachment"}, "optional", "rope, straight-bar, single-handle, lat-bar (cable/machine only)"],
    [{t:"grip"}, "optional", "pronated, supinated, neutral, mixed; wide / standard / narrow"],
    [{t:"angle"}, "optional", "flat (default), incline, decline"],
    [{t:"contraction"}, "optional", "dynamic (default), eccentric-only, isometric, plyometric"],
    [{t:"range"}, "optional", "full (default), partial, deficit, paused"],
  ],
  [1500, 1300, 6560],
));
children.push(caption("Table 2. The OMEN facets. Required facets must be supplied; defaulted and optional facets fall to defaults when unstated (Section 4.3)."));

children.push(h2("4.3 Muscle and mechanic are derived, not entered"));
children.push(body("The muscle worked is a *consequence* of the movement, not an independent choice, so OMEN does not store it as a facet. Instead each movement pattern maps to its primary and secondary musculature, and to whether it is compound or isolation, through a fixed table. Encoding `horizontal-push` therefore yields pectoralis major, anterior deltoid, and triceps, and the mechanic “compound,” with no further input. This removes the ambiguity of a free “muscle” field, handles multi-muscle movements correctly, and matches the primary/secondary treatment that exercise databases already found necessary. Muscle terms are intended to reference an external anatomical ontology rather than to be redefined by OMEN."));
children.push(body("The defaults mechanism keeps everyday names short. Optional facets that equal their default are omitted from the human form and restored in the canonical form, so a flat, bilateral, full-range, dynamic barbell press is written simply as a press, while an `incline`, `unilateral` variant states only what it changes. Grip, when unstated, is filled by the pattern's natural grip (a curl is supinated, a pulldown pronated)."));

children.push(h2("4.4 Named exercises as aliases"));
children.push(body("Because the name is not the identity, established names are stored as a curated alias table mapping a display name to the facet overrides that define it; the remaining facets fall to defaults. “Bench press” is the bundle {posture: supine, implement: barbell, pattern: horizontal-push}; “chin-up” and “pull-up” differ only in grip. This preserves the real-world vocabulary and, read in reverse, lets any record that matches a known bundle render under its accepted name, while records with no accepted name fall back to their compact canonical string."));

// ---- 5. Canonical forms and identifiers ----
children.push(h1("5. Canonical Forms and Identifiers"));
children.push(body("From the facet record OMEN produces three renderings under a single fixed field order (the citation order) that runs from general context to specific execution: posture, implement, attachment, grip, laterality, pattern, angle, contraction, range."));
children.push(bullet("**OMEN-C (compact)**, the human form: only non-default facets, in citation order. Example: `incline dumbbell horizontal-push`."));
children.push(bullet("**OMEN-X (canonical)**, every facet explicit, in citation order, grip resolved. This is the lossless form the key is hashed from."));
children.push(bullet("**OMEN key**, a short, language-neutral identifier: a version prefix plus a base-32 hash of OMEN-X. The database primary key, analogous to an InChIKey."));
children.push(body("For the bench press, the reference implementation produces the following (verbatim):"));
children.push(code("OMEN-C:  barbell horizontal-push"));
children.push(code("OMEN-X:  posture=supine|implement=barbell|attachment=none|grip_orientation=pronated|\n         grip_width=standard|laterality=bilateral|pattern=horizontal-push|angle=flat|\n         contraction=dynamic|range=full"));
children.push(code("key:     OMEN-0.2-VRQRJHQSX5NX6"));
children.push(body("Because the key is a function of the canonical string, the same movement always yields the same key regardless of how it was authored, and any change to a facet (grip, laterality, angle, contraction) yields a different key. The version prefix (`OMEN-0.2-`) guarantees that identifiers minted under one edition of the standard are never silently reinterpreted by another."));

// ---- 6. Worked examples ----
children.push(figure("fig2_pipeline.png", 530, 237));
children.push(caption("Figure 2. The encoding pipeline. A validated facet record is expanded against its defaults, serialized in the fixed citation order to OMEN-X, and hashed with a version prefix to yield the key. Musculature and mechanic are read from the movement pattern and are never entered by hand."));
children.push(h1("6. Worked Examples"));
children.push(body("Table 3 shows a representative set of movements as encoded by the reference implementation: the human form, the derived primary muscles (never entered), and the stable key. Two pairs are instructive. Pull-up versus chin-up differ only in grip yet receive distinct keys, capturing a distinction colloquial names often blur. The last row is a movement with no accepted name; its compact canonical string simply becomes its label, demonstrating generativity: the standard names movements it was never explicitly taught."));
children.push(table(
  ["Movement", "OMEN-C", "Primary muscles (derived)", "OMEN key"],
  [
    ["Back squat", {t:"barbell squat", mono:true}, "quadriceps, gluteus-maximus", {t:"OMEN-0.2-HWYDOFIMW3MXQ", mono:true}],
    ["Bench press", {t:"barbell horizontal-push", mono:true}, "pectoralis-major, ant.-deltoid, triceps", {t:"OMEN-0.2-VRQRJHQSX5NX6", mono:true}],
    ["Incline DB press", {t:"incline dumbbell horizontal-push", mono:true}, "pectoralis-major, ant.-deltoid, triceps", {t:"OMEN-0.2-CRBWWU6C4RMIK", mono:true}],
    ["Pull-up", {t:"vertical-pull", mono:true}, "latissimus-dorsi, teres-major", {t:"OMEN-0.2-L2SHL5OD62KEW", mono:true}],
    ["Chin-up", {t:"supinated vertical-pull", mono:true}, "latissimus-dorsi, teres-major", {t:"OMEN-0.2-NJJ6HLRNNFORY", mono:true}],
    ["Triceps pushdown", {t:"rope cable elbow-extension", mono:true}, "triceps", {t:"OMEN-0.2-LX2LC34DVHM4I", mono:true}],
    ["Romanian deadlift", {t:"barbell hip-hinge", mono:true}, "glute-max, hamstrings, erectors", {t:"OMEN-0.2-K5R5GCRCMTPDE", mono:true}],
    ["Plank", {t:"anti-extension isometric", mono:true}, "rectus-abdominis", {t:"OMEN-0.2-R77DG3ING3F7U", mono:true}],
    ["(unnamed) 1-arm cable row", {t:"single-handle cable unilateral horizontal-pull", mono:true}, "lat-dorsi, rhomboids, mid-trap, post-delt", {t:"OMEN-0.2-6PY6ZOH7GNUNG", mono:true}],
  ],
  [1900, 3050, 2760, 1650],
));
children.push(caption("Table 3. Worked examples, produced verbatim by the OMEN reference encoder. Muscles are derived from the movement pattern, not supplied."));

// ---- 7. Reference implementation ----
children.push(h1("7. Reference Implementation"));
children.push(body("The standard ships with an open reference encoder (Python, no dependencies) that is the executable definition of the controlled vocabularies and the canonical algorithms. It exposes a movement record, validates it against the vocabularies, expands defaults, emits OMEN-C, OMEN-X, and the key, derives musculature and mechanic from the pattern, and resolves names both ways through the alias table. A standard with running code is adopted; a specification alone is not."));
children.push(body("Correctness is enforced by a test suite that doubles as the standard's guarantees made executable: determinism (the same movement always yields the same key), non-collision (distinct movements never share a key across the alias table), predictable default expansion, first-class contraction (an eccentric-only variant is a distinct identity), and round-tripping (a colloquial name resolves to its record and back to its name). All tests pass in the accompanying release."));
children.push(code("$ python omen.py --name \"chin-up\"\n\n  CHIN-UP\n  OMEN-C   supinated vertical-pull\n  OMEN key OMEN-0.2-NJJ6HLRNNFORY\n  primary muscles  latissimus-dorsi, teres-major"));

// ---- 8. Evaluation ----
children.push(h1("8. Evaluation Protocol"));
children.push(body("A naming standard is validated less by argument than by whether people apply it the same way. This section specifies the protocol; Section 9 reports results for the four measures that can be computed without human subjects, and Section 11 states plainly which measure remains outstanding."));
children.push(bullet("**Inter-annotator agreement.** Several trained annotators independently encode the same set of movements; the primary metric is the proportion producing identical canonical keys, with per-facet agreement (Cohen's / Fleiss' κ) to locate any facet whose vocabulary is ambiguous. High agreement is the central claim a standard must earn."));
children.push(bullet("**Coverage.** Encode a random sample drawn from existing databases (Free Exercise DB, wger) and report the fraction expressible without inventing new terms, along with every gap, which is a direct measure of completeness and a queue for the extension process."));
children.push(bullet("**Round-trip fidelity.** For every named exercise, confirm that name → record → key → name returns the original name. (A parser that reads OMEN-C back into a record is not yet implemented; see Section 11.)"));
children.push(bullet("**Collision resistance.** Over a large generated cross-product of facets, confirm no two distinct records share a key, a property the hash makes overwhelmingly likely but which should be measured, not assumed."));
children.push(bullet("**Backward-compatibility.** Map a corpus of colloquial and literature names onto OMEN records and report how much ambiguity is resolved: how often several source names collapse to one key (synonymy captured) and how often one source name must split into several (ambiguity exposed)."));

// ---- 9. Results ----
children.push(h1("9. Results"));
children.push(body("The protocol of Section 8 has been executed in part. Coverage and backward-compatibility were measured against two independent databases, and collision resistance over a generated cross-product of the vocabularies. The inter-annotator study was not run; its materials are published with the standard and it remains the principal item of future work. Every number below is produced by the reference encoder and the audit scripts released with it."));

children.push(h2("9.1 Coverage against two independent databases"));
children.push(body("We attempted to express every record of two public exercise databases in OMEN. The Free Exercise DB contains 876 exercises, of which 198 lie outside the declared scope (stretching, cardiovascular and plyometric entries), leaving **678 resistance-training records**. The second corpus, wger, contributes **847** English-language exercises written under different naming conventions. Each record was mapped onto OMEN facets by a deterministic script reading the database's structured fields together with the tokens of its display name, drawing only on the controlled vocabularies. Critically, **the identical mapping script was used on both corpora**, so the second audit measures the standard rather than a per-corpus heuristic. Failures were separated into three kinds, because they license different conclusions: records requiring a term OMEN does not define, records the automated mapper could not resolve, and records whose own fields do not disclose enough to encode at all."));
children.push(table(["Corpus", "In scope", "Encodable", "OMEN gap", "Not encodable", "Coverage"], [
  ["Free Exercise DB", "678", "574", "54", "50", "84.7%  (91.4%)"],
  ["wger", "847", "590", "16", "241", "69.7%  (89.8%)"],
], [2100, 1100, 1400, 1200, 1800, 1760]));
children.push(caption("Table 4. Coverage of two independent exercise databases. The bracketed figure is coverage of records carrying enough information to be encoded at all; the unbracketed figure includes records the source itself leaves underspecified. For wger the last column separates 16 genuine vocabulary gaps from 51 records the automated mapper could not resolve and 190 the source does not specify."));
children.push(body("Coverage is therefore **84.7%** and **69.7%** of all in-scope records, or **91.4%** and **89.8%** of records carrying sufficient information. The agreement between two corpora with different naming conventions, audited by the same script, is the more informative result: on wger only **16 records (1.9%)** required a term the standard does not define."));

children.push(h2("9.2 What remains uncovered is one principled category"));
children.push(body("Earlier drafts of this standard showed gaps scattered across many unrelated concepts. Completing each joint's action set (Section 3) removed almost all of them. What survives is not a miscellany but a single coherent class: movements composed of *several patterns in sequence*."));
children.push(table(["Concept still outside the vocabulary", "Free Exercise DB", "wger"], [
  ["Olympic and other multi-phase lifts (clean, snatch, jerk)", "50", "9"],
  ["Complex multi-pattern movements (thruster, Turkish get-up)", "3", "5"],
  ["Grip and finger flexion", "1", "2"],
], [5000, 2180, 2180]));
children.push(caption("Table 5. Every remaining gap in both corpora. 53 of 54 and 14 of 16 are multi-phase or composite movements."));
children.push(body("This is a scope boundary rather than a vocabulary omission, and it has the same shape as the dosage argument of Section 11: a clean is not one movement pattern but an ordered sequence of them. Naming it correctly requires a composite notation that *references* OMEN keys rather than a new facet inside one. We regard that as the primary design question for the next version, and prefer to state it as an open problem than to force a sequence into a single-pattern record."));

children.push(h2("9.3 Synonymy captured and underspecification exposed"));
children.push(body("Two by-products of the audit bear directly on the argument of Section 1. First, the 574 encodable Free Exercise DB records, written by their authors as 574 distinct names, resolved to **304 distinct keys**, forming **106 clusters** in which two or more names denote one movement; on wger, 590 names resolved to 233 keys across 79 clusters. Synonymy is captured by construction rather than asserted. Second, **81%** of the Free Exercise DB names did not state posture anywhere in the name or the record, so posture had to be supplied by the pattern default. The claim that existing exercise names are underspecified is therefore measurable, and it is the majority case."));

children.push(h2("9.4 Round-trip fidelity"));
children.push(body("Every curated display name in the alias table was resolved to its facet record, encoded to a key, and rendered back to a name. All **17 of 17** returned the original name exactly, and re-encoding the same record reproduced the same key in every case. This is the weakest of the measures reported here, because the alias table is small and hand-built, and it will only become informative as the table grows. It is reported because Section 8 promises it."));
children.push(h2("9.5 Collision resistance and determinism"));
children.push(body("Collision resistance was measured over a generated cross-product of the controlled vocabularies rather than argued from properties of the hash. Two sweeps were run: 5,821,200 records spanning every combination of posture, implement, pattern, laterality, angle, contraction and range, and a further 232,848 spanning grip orientation and width. Across **6,054,048 distinct canonical forms no two produced the same key.** Determinism and independence from field order were confirmed over 20,000 randomly generated records."));
children.push(table(["Property tested", "Records", "Result"], [
  ["Distinct canonical forms encoded", "6,054,048", "0 collisions"],
  ["Determinism (repeated encoding)", "20,000", "identical keys"],
  ["Independence from field order", "20,000", "identical keys"],
], [4400, 2480, 2480]));
children.push(caption("Table 6. Collision and determinism sweep over the generated facet space."));

children.push(h2("9.6 Versioning demonstrated"));
children.push(body("Because the key is a version prefix applied to a hash of the canonical string, and the canonical string does not itself contain the version, extending the vocabulary between editions changed every identifier's prefix and no identifier's hash. The bench press encoded as OMEN-0.1-VRQRJHQSX5NX6 under the earlier edition and encodes as OMEN-0.2-VRQRJHQSX5NX6 under this one. A consumer can therefore tell which edition minted a code and can recognise that the two denote the same movement, which is precisely the property Section 10 claims."));

children.push(h2("9.7 A crosswalk as the first usable artifact"));
children.push(body("The audit produces something directly adoptable: a crosswalk mapping all 574 encodable Free Exercise DB records to their OMEN keys, canonical forms, facets and derived musculature, released as CSV and JSON. Any application already using that database can acquire stable identifiers by joining on it, without adopting the standard wholesale. We regard this, rather than the coverage percentage, as the most immediately useful output of the evaluation."));

// ---- 10. Governance ----
children.push(h1("10. Governance and Versioning"));
children.push(body("The property most often fatal to a proposed standard is the absence of a body to steward it. OMEN therefore specifies its governance as part of the standard, not as an afterthought."));
children.push(bullet("**Maintaining authority.** An open registry owns the controlled vocabularies and the alias table, publishes the specification and reference implementation under open licenses, and adjudicates change."));
children.push(bullet("**Versioning.** The standard follows semantic versioning, and the major version is embedded in every key's prefix, so identifiers are self-dating and a consumer always knows which edition minted a code."));
children.push(bullet("**Extension.** New patterns, implements, or terms are proposed to the registry with a rationale and worked examples, reviewed for overlap with existing terms, and ratified into a numbered release: the mechanism by which the grammar grows without fragmenting."));
children.push(bullet("**Deprecation and merging.** Terms are never silently removed; they are deprecated with a mapping to their replacement, and identifiers remain permanently resolvable, so published citations never rot."));
children.push(bullet("**A registry needs a first artifact.** A governance model with nothing to govern does not attract adopters. The crosswalk of Section 9.6 is offered as that first artifact: a concrete, versioned mapping between an existing database and the standard, the smallest useful thing a registry can publish."));
children.push(bullet("**Internationalization.** Because identity is language-neutral, display names are a localizable layer: the registry can carry language reference sets so a single key renders in many languages without changing identity."));

// ---- 10. Limitations ----
children.push(h1("11. Limitations and Future Work"));
children.push(body("OMEN, as drafted, scopes itself deliberately to the *identity of a resistance-training movement.* Several boundaries and extensions follow."));
children.push(bullet("**Dosage is a separate layer.** How a movement is *performed in a session* (load, sets, repetitions, rest, tempo prescription) is a distinct standardization problem. OMEN names the movement; a companion dosage notation should reference OMEN keys rather than fold into them."));
children.push(bullet("**Beyond resistance training.** Cardiovascular, mobility, sport-specific, and rehabilitation movements are out of scope for version 0.2. The facet approach should extend to them, but each brings axes (duration, intensity zones, sport context) that need their own vocabularies."));
children.push(bullet("**Granularity of muscle and pattern.** The pattern-to-muscle table is intentionally coarse; linking it to a formal anatomical ontology and allowing finer variants (for example, a curl biased to the brachialis) is future work."));
children.push(bullet("**Inter-annotator agreement is not yet measured.** Section 9 reports coverage, synonymy, collision resistance and determinism, all of which a machine can measure. The central claim of any naming standard, that independent trained humans encode the same movement identically, requires annotators and has not been run. The full study materials (instructions, a 30-movement set, a response template, and a scoring script computing exact-key agreement and per-facet Fleiss' kappa) are released with the standard so others can run it, but until results exist OMEN's reproducibility is demonstrated for the encoder and not for its users."));
children.push(bullet("**The coverage audit is automated.** Records were mapped to facets by script rather than by expert annotators, which is a proxy for manual encoding and not a substitute for it. Two mitigations are released: the mapping heuristics are published so the figure can be reproduced and contested, and a fixed-seed 50-record sample with a comparison script is provided so a human encoder can measure how far the automated mapping departs from their judgement."));
children.push(bullet("**OMEN-C cannot yet be parsed back.** The compact human form is currently write-only: the encoder emits it but provides no reader that recovers a facet record from it. Because OMEN-C omits defaulted facets, parsing it is well defined and simply not yet built. Until it is, round-trip guarantees hold for names and keys but not for the compact string."));
children.push(bullet("**Multi-phase movements are out of scope.** As Section 9.2 reports, essentially the entire residual gap in both corpora is the Olympic lifts and similar composite movements. OMEN names a single movement pattern; a clean is a sequence. A composite notation referencing OMEN keys is the main open design question."));
children.push(bullet("**The provenance of the vocabularies is uneven.** The joint-action patterns follow standard anatomical terminology of motion. The higher-level patterns (squat, hinge, lunge, carry) follow the movement-pattern taxonomy widely used in strength and conditioning practice, which is practitioner convention rather than a peer-reviewed classification; OMEN makes it explicit and testable rather than claiming to derive it. The pattern-to-muscle table encodes conventional textbook attributions and is deliberately coarse: it is not a systematic review of electromyographic evidence and should be read as a defensible default rather than a finding. Binding muscle terms to a formal anatomy ontology such as the Foundational Model of Anatomy (Rosse & Mejino, 2003) is future work."));
children.push(bullet("**Two corpora, both community-built.** Coverage is reported against two open exercise databases. Neither is a sample of exercise names as they appear in the research literature, which is where the inconsistency was originally documented (Nuzzo, 2021). Auditing a corpus of published article titles would test whether these figures generalise to scientific writing."));

// ---- 11. Conclusion ----
children.push(h1("12. Conclusion"));
children.push(body("Exercise naming is inconsistent, the inconsistency has a measurable cost, and the professionals affected want it fixed, all of which is established, not conjectured. What has been missing is a standard that is computable rather than merely recommended: one that fixes a vocabulary and an identifier, not just a word order. OMEN supplies that by describing a movement as orthogonal facets, deriving its musculature from its movement pattern, and generating a canonical form and a stable, versioned key while keeping human names as a curated layer. It unifies the strengths of the three prior camps (the practitioner call for standardization, the database instinct to decompose into fields, and the ontological commitment to controlled terms and open publication) into the interoperable key the field currently lacks. The reference implementation makes the standard executable today; the coverage audit and the collision sweep reported in Section 9 make it measurable; the governance model makes it able to grow. Three quarters of an independent database encodes without invention, the gaps are enumerable rather than open-ended, and the identifier survives two and a half million records without a collision. The step that remains is the one only people can supply: the inter-annotator study that will show whether trained humans, and not merely the encoder, apply the standard the same way."));

// ---- References ----
children.push(h1("Data and Code Availability"));
children.push(body("The OMEN reference encoder, its test suite (18 tests, all passing), the coverage-audit and collision-sweep scripts, and the machine-readable controlled vocabularies are released under an open licence at the project repository. The corpora audited in Section 9 are the public-domain Free Exercise DB and the open wger exercise database. The crosswalk (CSV and JSON), the inter-annotator study materials, and the manual-validation sample are released in the same repository. All figures reported here regenerate from the released scripts."));
children.push(body("**Repository:** https://github.com/AbleVLabs/omen"));
children.push(h1("Author Contributions"));
children.push(body("C.A.V. is the sole author. He conceived and directed the project, specified and approved the design of the standard, verified the results reported in Section 9 by independently re-running the released audit scripts, and reviewed and approved the final manuscript."));
children.push(h1("Use of Generative AI"));
children.push(body("The author used Anthropic's Claude, a generative AI assistant, throughout this project. AI assistance was used to survey prior work, draft and revise the manuscript, implement the reference encoder and its test suite, generate Figures 1 and 2, and execute the coverage audit and collision sweep reported in Section 9. The author directed the project, reviewed and approved all design decisions, independently reproduced the reported results using the released scripts, and takes full responsibility for the content of this manuscript."));
children.push(h1("Funding"));
children.push(body("This work received no external funding."));
children.push(h1("Conflicts of Interest"));
children.push(body("The author declares no competing interests."));
children.push(h1("References"));
const refs = [
  "Jackson, M. C., Brown, L. E., Coburn, J. W., Judelson, D. A., & Cullen-Carroll, N. (2013). Towards standardization of the nomenclature of resistance training exercises. Journal of Strength and Conditioning Research, 27(5), 1441-1449. doi:10.1519/JSC.0b013e318289168d",
  "Nuzzo, J. L. (2017). Words and patterns that comprise resistance training exercise names. Journal of Strength and Conditioning Research, 31(3), 826-830. doi:10.1519/JSC.0000000000000965",
  "Nuzzo, J. L. (2021). Inconsistent use of resistance exercise names in research articles: a brief note. Journal of Strength and Conditioning Research, 35(12), 3518-3520. doi:10.1519/JSC.0000000000004083",
  "Nuzzo, J. L., & Nosaka, K. (2023). Eccentric muscle actions add complexity to an already inconsistent resistance exercise nomenclature. Sports Medicine - Open, 9, 118. doi:10.1186/s40798-023-00667-4",
  "Kim, H., Mentzer, J., & Taira, R. (2019). Developing a physical activity ontology to support the interoperability of physical activity data. Journal of Medical Internet Research, 21(4), e12776. doi:10.2196/12776",
  "Liu, X., Yang, Y., Zong, H., et al. (2024). Core reference ontology for individualized exercise prescription. Scientific Data, 11. doi:10.1038/s41597-024-04217-9",
  "Kinetic human movement ontology: a semantic terminology model to symbolically represent physiological movement. (2026). Scientific Data. doi:10.1038/s41597-026-06984-z",
  "Rosse, C., & Mejino, J. L. V. (2003). A reference ontology for biomedical informatics: the Foundational Model of Anatomy. Journal of Biomedical Informatics, 36(6), 478-500. doi:10.1016/j.jbi.2003.11.007",
  "Weininger, D. (1988). SMILES, a chemical language and information system. Journal of Chemical Information and Computer Sciences, 28(1), 31-36. doi:10.1021/ci00057a005",
  "Heller, S. R., McNaught, A., Pletnev, I., Stein, S., & Tchekhovskoi, D. (2015). InChI, the IUPAC International Chemical Identifier. Journal of Cheminformatics, 7, 23. doi:10.1186/s13321-015-0068-4",
  "Free Exercise DB. Open public-domain exercise dataset (JSON). https://github.com/yuhonas/free-exercise-db",
  "wger Workout Manager. Open-source fitness and exercise database. https://github.com/wger-project/wger",
];
refs.forEach((r) => children.push(new Paragraph({
  spacing: { after: 120, line: 264 }, indent: { left: 360, hanging: 360 },
  children: [new TextRun({ text: r, font: SERIF, size: 19, color: INK })],
})));

// =========================================================================
// DOCUMENT
// =========================================================================
const doc = new Document({
  creator: "AbleVLabs / Carlos Abel Vivanco",
  title: "OMEN: Open Movement & Exercise Nomenclature",
  description: "A generative, computable naming standard for resistance-training movements.",
  features: { updateFields: true },
  numbering: {
    config: [
      { reference: "layers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.START }] },
    ],
  },
  styles: {
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: SANS, size: 30, bold: true, color: ACCENT }, paragraph: { spacing: { before: 300, after: 140 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: SANS, size: 24, bold: true, color: INK }, paragraph: { spacing: { before: 220, after: 100 }, outlineLevel: 1 } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1656, right: 1656 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: "OMEN · Open Movement & Exercise Nomenclature", font: SANS, size: 15, color: MUTE })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: ["Page ", PageNumber.CURRENT], font: SANS, size: 15, color: MUTE })] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("OMEN_whitepaper.docx", buf);
  console.log("wrote OMEN_whitepaper.docx (" + buf.length + " bytes)");
});
