#!/usr/bin/env python3
"""
Enhanced patent section templates with detailed, enablement-ready prompts.
Based on user feedback for §101/§112 compliance and enablement requirements.
"""

# Enhanced section-specific prompt templates
ENHANCED_SECTION_PROMPTS = {
    "TITLE OF THE INVENTION": """Generate a complete, grammatical, tech-specific title for this invention.

INVENTION DESCRIPTION:
{description}

REQUIREMENTS:
- Complete sentence (not truncated)
- Grammatically correct
- Modality-agnostic where possible
- Names the ML/technical approach
- Neutral, functional language (NO superlatives like "High Accuracy" or "Explanatory Capabilities")
- Format: "Systems and Methods for [Core Function] Using [Technical Approach] with [Neutral Differentiators]"

Example: "Systems and Methods for Detecting Anomalies in Medical Images Using Convolutional Neural Networks with Calibrated Confidence and Visual Explanations"

BANNED PHRASES IN TITLE:
- "High Accuracy"
- "Explanatory Capabilities" (use "Visual Explanations" instead)
- "Remarkable"
- "Revolutionary"
- Any performance claims or superlatives
- Fixed numbers like "95%"

CRITICAL: Generate ONLY the title as plain text. Do NOT output JSON, do NOT use quotes, do NOT include any structure. Just the title text.""",

    "FIELD": """Generate the FIELD OF THE INVENTION section (2-3 lines, neutral tone).

INVENTION DESCRIPTION:
{description}

GLOSSARY:
{glossary}

REQUIREMENTS:
- 2-3 sentences maximum
- Neutral, technical language
- Use "the disclosure" instead of "the present invention"
- Be specific about technical domain
- No superiority claims
- No admissions

Template: "The disclosure relates to [technical domain] using [key technology] for [primary function], [secondary function], and [tertiary function]."

CRITICAL: Generate ONLY plain text. Do NOT output JSON, do NOT use structured format. Just the section text.""",

    "BACKGROUND": """Generate the BACKGROUND OF THE INVENTION section with two short paragraphs.

INVENTION DESCRIPTION:
{description}

GLOSSARY:
{glossary}

REQUIREMENTS:
Paragraph 1 - Clinical Pain Points (2-3 sentences):
- False negatives in medical image interpretation
- Double-reading workload burden
- Inter-reader variability
- Use neutral, factual language
- NO admissions about prior art
- NO external literature citations (remove any pseudo-references)

Paragraph 2 - Technical Pain Points (2-3 sentences):
- Domain shift across devices and imaging sites
- Class imbalance in training data
- Lack of calibrated confidence estimates
- Poor explainability of model decisions
- Use technical, neutral language
- NO comparative claims

End with: "Accordingly, there is a need for techniques that provide [key features] with [differentiators] and robust performance across [relevant domains]."

CRITICAL:
- NO superiority claims
- NO admissions about prior art
- NO external citations or pseudo-references
- NO hype or marketing language
- Use "the disclosure" not "the present invention"
- Neutral, technical tone throughout
- Keep paragraphs SHORT (2-3 sentences each)

CRITICAL: Generate ONLY plain text paragraphs. Do NOT output JSON, do NOT use structured format. Just the section text with both paragraphs.""",

    "SUMMARY": """Generate the BRIEF SUMMARY OF THE INVENTION section structured as 3-5 "aspects."

INVENTION DESCRIPTION:
{description}

GLOSSARY:
{glossary}

OUTLINE:
{outline}

REQUIREMENTS:
Structure as "In one aspect..." paragraphs:

Aspect 1 - System:
- Ingestion → preprocessing → CNN backbone → anomaly head → calibration → UI with heatmap + thresholding
- High level, no narrowing implementation details

Aspect 2 - Method:
- Training with class-imbalanced loss, augmentation, domain adaptation
- Inference with confidence calibration
- High level description

Aspect 3 - Computer-Readable Medium:
- Instructions to perform the method

Aspect 4 - Variants (optional):
- Single-view vs multi-view
- On-device vs cloud
- Active learning loop

CRITICAL:
- Use open-ended ranges, not single-point values
- Avoid narrowing language: "must", "only", "always", "essential"
- Keep high level; no narrowing implementation details
- Use "the disclosure" not "the present invention"

CRITICAL: Generate ONLY plain text. Do NOT output JSON, do NOT use structured format. Just the section text with "In one aspect..." paragraphs.""",

    "DRAWINGS": """Generate the BRIEF DESCRIPTION OF THE DRAWINGS section with consistent numeral scheme.

INVENTION DESCRIPTION:
{description}

OUTLINE FIGURES:
{figures}

REQUIREMENTS:
- Use consistent numeral scheme matching the Detailed Description:
  - 100-series for system components
  - 200-series for method steps
  - 300-series for UI components
- Describe exactly 3 figures with specific numerals:
  - FIG. 1: system block diagram (100-series: acquisition 110, preprocessing 120, CNN 130, calibration 140, explainer 150, UI 160, datastore 170)
  - FIG. 2: method flow (200-series: receive 210, normalize 220, infer 230, anomaly score 240, calibrate 250, heatmap 260, triage 270, output 280)
  - FIG. 3: UI components (300-series: image pane 310, heatmap overlay 320, confidence gauge 330, threshold control 340, triage queue 350)
- Each figure description should be 1-2 sentences
- Format: "FIG. 1 shows [description with numerals]." "FIG. 2 illustrates [description with numerals]." etc.
- Reference the specific numerals (100, 110, 120, etc.) that will be used in Detailed Description
- DO NOT repeat the same information multiple times
- DO NOT include "In some embodiments" variations for each figure
- DO NOT include glossary JSON or metadata

CRITICAL: Generate ONLY plain text figure descriptions. Do NOT output JSON, do NOT use structured format. Just the BRIEF DESCRIPTION OF THE DRAWINGS section with 3 figure descriptions.""",

    "DETAILED_DESCRIPTION": """Generate the DETAILED DESCRIPTION OF THE INVENTION section with enablement requirements.

INVENTION DESCRIPTION:
{description}

GLOSSARY:
{glossary}

OUTLINE:
{outline}

REQUIREMENTS:
Write numbered subsections with ranges + alternatives so a practitioner can implement without guesswork. Each subsection must include concrete ranges (not single values) and technical specifications.

Required Subsections (numbered, with figure references):

1. System Architecture (100-series, reference FIG. 1)
   - Hardware options: CPU, GPU, or edge TPU
   - Latency target: e.g., ≤300 ms for 1024×1024 image
   - Batch constraints and memory ranges
   - Reference components: acquisition interface (110), preprocessing module (120), CNN module (130), calibration module (140), explainer (150), UI (160), datastore (170)

2. Image Acquisition & Preprocessing (110, 120, reference FIG. 1)
   - Supported modalities: X-ray, CT, MRI, ultrasound
   - Normalization: z-score or min-max (specify ranges)
   - Resizing range: 512 to 1536 pixels
   - Optional artifact removal
   - CT windowing examples if CT is included (HU ranges)

3. Model Architecture (130, reference FIG. 1)
   - Define "convolutional block": conv→norm→activation→pool
   - Kernel sizes: 3×3 or 5×5
   - Stride: 1 or 2
   - Depth range: 8 to 200 layers
   - Backbone options: ResNet-xx, DenseNet-xx, U-Net encoder (list specific variants)
   - Anomaly head: sigmoid activation
   - Optional segmentation/heatmap head: upsampling layers

4. Training Procedure
   - Loss functions: BCE or focal loss; optional Dice loss for segmentation
   - Class imbalance: class weights or sampling strategies (specify ranges)
   - Augmentation: rotations in range ±15°, flips, noise injection
   - Optimization: Adam or SGD
   - Learning rate range: 1e-5 to 1e-2
   - Batch size range: 4 to 64
   - Epochs range: 10 to 200
   - Early stopping criteria
   - Domain adaptation options: instance normalization, test-time adaptation (describe)

5. Calibration (140, reference FIG. 1)
   - Methods: temperature scaling or isotonic regression
   - Calibrated anomaly score range: [0, 1]
   - Held-out validation set for calibration
   - Expected calibration error (ECE) target range (do NOT claim universal achievement)

6. Explainability (150, reference FIG. 1)
   - Methods: Grad-CAM or Integrated Gradients
   - Heatmap scaling: 0 to 255
   - Smoothing techniques
   - Confidence-weighted overlay

7. Decision & Triage (270, reference FIG. 2)
   - Threshold τ in range [0.1, 0.9]
   - Routing logic: urgent queue vs normal queue
   - Hysteresis for multi-frame series
   - Uncertainty band for triggering second read (e.g., when score in range 0.45 to 0.55)

8. User Interface (160, 300, reference FIG. 1 and FIG. 3)
   - Image pane (310), heatmap overlay (320), confidence gauge (330)
   - Threshold control (340), triage queue (350)
   - Audit logging
   - Human-in-the-loop feedback to active learning pool

9. Deployment & Privacy
   - On-device: quantized model options
   - Cloud inference: secure transport and storage
   - PHI handling: de-identification requirements
   - Logging: no PHI in logs

10. Worked Examples (at least two, step-by-step)
    - Example 1: Chest X-ray pneumothorax triage
      * Input: chest X-ray image (specify dimensions)
      * Preprocessing: normalization method, resizing
      * Inference: CNN forward pass, anomaly score
      * Calibration: calibrated confidence value
      * Heatmap: explainability visualization
      * Triage: routing decision based on threshold
    - Example 2: Brain MRI anomaly localization with multi-slice fusion
      * Input: multi-slice MRI stack
      * Preprocessing: per-slice normalization
      * Inference: per-slice scores, fusion method
      * Calibration and heatmap generation
      * Triage decision

11. Support Map Paragraph
    - Explicit mapping: "The [claim term] of claim X refers to [paragraph Y] and FIG. Z"
    - Every claim term must point to numbered paragraphs and figures
    - Example: "The acquisition interface of claim 1 refers to paragraph [X] and FIG. 1, element 110"

CRITICAL:
- Use "the disclosure" not "the present invention"
- Include RANGES for all parameters (not single values)
- Provide alternatives using "In some embodiments", "In other embodiments" (limit to 2-3 alternatives per subsection)
- Reference figures numerically with element numbers (FIG. 1, element 110; FIG. 2, step 210, etc.)
- Use passive/neutral tone
- NO marketing language or superlatives
- NO fixed performance numbers (e.g., "95% accuracy")
- NO comparative claims
- Include enablement language: "sufficient detail for a person of ordinary skill in the art to make and use the invention without undue experimentation"

CRITICAL: Generate ONLY plain text paragraphs. Do NOT output JSON, do NOT use structured format. Just the section text with numbered subsections.""",

    "CLAIMS": """Generate CLAIMS section with proper structure and antecedent basis.

INVENTION DESCRIPTION:
{description}

GLOSSARY:
{glossary}

SPECIFICATION:
{specification}

REQUIREMENTS:

Independent Claims (3 required):

Claim 1 - System (matching FIG. 1):
A system comprising:
(a) an acquisition interface configured to receive a medical image;
(b) a preprocessing module configured to normalize and resize the medical image;
(c) a convolutional neural network comprising a plurality of convolutional layers configured to generate an anomaly score for the medical image;
(d) a calibration module configured to transform the anomaly score into a calibrated confidence value; and
(e) a user interface configured to display the medical image with an explainability heatmap and the calibrated confidence value.

Claim 2 - Method (matching FIG. 2):
A method comprising the steps of:
(a) receiving a medical image;
(b) preprocessing the medical image to normalize and resize the medical image;
(c) inferring an anomaly score via a convolutional neural network having a plurality of convolutional layers;
(d) calibrating the anomaly score to produce a calibrated confidence value;
(e) generating an explainability heatmap; and
(f) displaying the medical image with the explainability heatmap and the calibrated confidence value.

Claim 3 - Non-transitory CRM:
A non-transitory computer-readable medium storing instructions that, when executed by a processor, cause the processor to perform the method of claim 2.

Dependent Claims (12-18 required, covering these buckets):

Modality:
- The system/method of claim X, wherein the medical image is an X-ray image.
- The system/method of claim X, wherein the medical image is a CT image.
- The system/method of claim X, wherein the medical image is an MRI image.

Preprocessing:
- The system/method of claim X, wherein preprocessing includes windowing for CT images.
- The system/method of claim X, wherein preprocessing includes artifact removal.

Model Architecture:
- The system/method of claim X, wherein the convolutional neural network has kernel sizes in a range from 3×3 to 5×5.
- The system/method of claim X, wherein the convolutional neural network has a depth in a range from 8 to 200 layers.
- The system/method of claim X, wherein the convolutional neural network includes a backbone selected from ResNet, DenseNet, or U-Net encoder.

Training:
- The system/method of claim X, wherein the convolutional neural network is trained using focal loss.
- The system/method of claim X, wherein the convolutional neural network is trained with class weighting to address class imbalance.
- The system/method of claim X, wherein training includes augmentation selected from rotations, flips, or noise injection.

Calibration:
- The system/method of claim X, wherein calibration uses temperature scaling.
- The system/method of claim X, wherein calibration uses isotonic regression.

Explainability:
- The system/method of claim X, wherein the explainability heatmap is generated using Grad-CAM.
- The system/method of claim X, wherein the explainability heatmap is generated using Integrated Gradients.

Triage:
- The system/method of claim X, wherein triage uses a threshold τ in a range from 0.1 to 0.9.
- The system/method of claim X, wherein triage includes an uncertainty band for triggering a second read.

Multi-view:
- The system/method of claim X, wherein the medical image includes multiple views selected from PA and lateral views.
- The system/method of claim X, wherein the medical image includes a multi-slice MRI stack.

Deployment:
- The system/method of claim X, wherein the convolutional neural network is quantized for on-device inference.
- The system/method of claim X, wherein inference is performed on a cloud server.

Active Learning:
- The system/method of claim X, further comprising receiving human feedback and updating a training set based on the feedback.

CRITICAL REQUIREMENTS:
- Each claim must be a single sentence
- Number claims sequentially: 1., 2., 3., etc.
- Independent claims start with "A [system/method/apparatus] comprising:" or "A method comprising the steps of:"
- Dependent claims reference preceding claims: "The [system/method] of claim X, wherein..." or "The [system/method] of claim X, further comprising..."
- Ensure all claim terms have antecedent basis in specification (e.g., "the medical image", "the calibrated confidence value")
- Use consistent terminology from glossary (lower-case unless defined)
- Avoid "the present invention"
- Avoid unnecessary "said" references
- NO "use of" claims (not statutory in U.S.)
- NO mixing categories inside one claim (system vs method vs CRM)
- NO comparative accuracy claims (e.g., "more accurate than")
- NO fixed performance numbers (e.g., "95%")
- Keep ranges/alternatives; avoid locking to one architecture
- Every claim noun must be supported in Detailed Description (by paragraph number and figure numeral)

CRITICAL: Generate ONLY plain text claims. Do NOT output JSON, do NOT use structured format. Just numbered claims like "1. A system..." "2. The system of claim 1..." etc.""",

    "ABSTRACT": """Generate the ABSTRACT OF THE DISCLOSURE section.

INVENTION DESCRIPTION:
{description}

GLOSSARY:
{glossary}

REQUIREMENTS:
- Exactly ≤150 words (count carefully)
- Single paragraph
- Focus on WHAT IT DOES (functional pipeline), NOT how well it performs
- Include: "calibrated confidence value" + "explainability heatmap" + "triage"
- Describe the functional steps: receiving image → preprocessing → CNN inference → calibration → heatmap generation → display/triage
- NO legalese
- NO limitations
- NO "the present invention"
- NO performance claims or numbers
- NO comparative language ("better than", "more accurate")
- Technical and specific, but functional only

BANNED IN ABSTRACT:
- "high accuracy"
- "95%"
- "more accurate than"
- "remarkable"
- "revolutionary"
- Any superlatives or performance claims

CRITICAL: Generate ONLY plain text abstract. Do NOT output JSON, do NOT use structured format. Just a single paragraph of text (≤150 words).""",

    "DEFINITIONS": """Generate a DEFINITIONS section.

INVENTION DESCRIPTION:
{description}

GLOSSARY:
{glossary}

REQUIREMENTS:
Define key terms that appear in claims:
- "medical image"
- "convolutional block"
- "anomaly score"
- "calibrated confidence value"
- "explainability heatmap"
- "triage"
- Any other technical terms from claims

Format:
"[Term] means [definition]."

Generate the DEFINITIONS section."""
}

# Global banned phrases (apply to all sections)
GLOBAL_BANNED_PHRASES = [
    "the present invention",  # Use "the disclosure" instead
    "revolutionary",
    "will make millions",
    "superior to all",
    "more accurate than",
    "remarkable",
    "high accuracy",  # Marketing claim
    "95%",  # Fixed performance number
    "more accurate",
    "better than",
    "only",  # In spec context (narrowing)
    "must",  # In spec context (narrowing)
    "always",  # In spec context (narrowing)
    "essential",  # In spec context (narrowing)
    "exclusively",
    "cannot be",
    "revolutionize"
]

# Section-specific banned phrases
SECTION_BANNED_PHRASES = {
    "BACKGROUND": [
        "the present invention is superior",
        "prior art fails completely",
        "superior to",
        "better than"
    ],
    "SUMMARY": [
        "must",
        "only",
        "exclusively",
        "cannot be",
        "always"
    ],
    "CLAIMS": [
        "the present invention",
        "said"  # When unnecessary
    ],
    "ABSTRACT": [
        "the present invention",
        "according to claim"
    ]
}

