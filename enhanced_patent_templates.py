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
- Hints at key differentiators (e.g., calibration, explainability, triage)
- Format: "Systems and Methods for [Core Function] Using [Technical Approach] with [Differentiators]"

Example: "Systems and Methods for Detecting Anomalies in Medical Images Using Convolutional Neural Networks with Explainability and Calibration"

Generate ONLY the title, no other text.""",

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

Generate the FIELD OF THE INVENTION section only.""",

    "BACKGROUND": """Generate the BACKGROUND OF THE INVENTION section with two paragraphs.

INVENTION DESCRIPTION:
{description}

GLOSSARY:
{glossary}

REQUIREMENTS:
Paragraph 1 - Clinical Pain Points:
- False negatives, double-reading workload, variability
- Use neutral language
- No admissions

Paragraph 2 - Technical Pain Points:
- Domain shift across devices/sites
- Class imbalance
- Lack of calibrated confidence
- Poor explainability
- Use technical, neutral language

End with: "Accordingly, there is a need for techniques that provide [key features] with [differentiators] and robust performance across [relevant domains]."

CRITICAL:
- NO superiority claims
- NO admissions about prior art
- Use "the disclosure" not "the present invention"
- Neutral, technical tone throughout

Generate the BACKGROUND OF THE INVENTION section with both paragraphs.""",

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

Generate the BRIEF SUMMARY OF THE INVENTION section.""",

    "DRAWINGS": """Generate the BRIEF DESCRIPTION OF THE DRAWINGS section with consistent numeral scheme.

INVENTION DESCRIPTION:
{description}

OUTLINE FIGURES:
{figures}

REQUIREMENTS:
Use consistent numeral scheme (100-series system, 200-series method, 300-series UI):

FIG. 1 (100-series): System block diagram
- Acquisition interface (110)
- Preprocessor (120)
- CNN module (130)
- Calibration module (140)
- Explainer (150)
- UI (160)
- Datastore (170)

FIG. 2 (200-series): Method flow
- Receive image (210)
- Normalize/resize (220)
- Infer (230)
- Compute anomaly score (240)
- Calibrate (250)
- Generate heatmap (260)
- Decide/route (270)
- Output report (280)

FIG. 3 (300-series): UI
- Image pane (310)
- Heatmap overlay (320)
- Confidence gauge (330)
- Threshold control (340)
- Triage queue (350)

Format: "FIG. N shows [detailed description with numerals]."

Generate the BRIEF DESCRIPTION OF THE DRAWINGS section.""",

    "DETAILED_DESCRIPTION": """Generate the DETAILED DESCRIPTION OF THE INVENTION section with enablement requirements.

INVENTION DESCRIPTION:
{description}

GLOSSARY:
{glossary}

OUTLINE:
{outline}

REQUIREMENTS:
Write numbered subsections. Each subsection must include:
- Concrete ranges (not single values)
- At least one worked example
- Technical specifications

Required Subsections:

1. System Architecture (100-series)
   - Hardware options (CPU/GPU/edge TPU)
   - Memory ranges
   - Latency targets (e.g., ≤300 ms per 1024×1024 image)

2. Image Acquisition & Preprocessing (110, 120)
   - Supported modalities (CT, MRI, X-ray, ultrasound)
   - Normalization ranges (min-max or z-score)
   - Resizing ranges (512-1536 px)
   - Windowing (for CT HU ranges)
   - De-identification note

3. Model (CNN Module 130)
   - Define convolutional block (conv→norm→activation→pool)
   - Backbone choices (ResNet-xx, DenseNet-xx, U-Net encoder)
   - Kernel sizes (3×3/5×5)
   - Strides (1-2)
   - Depth ranges (8-200 layers)
   - Heads: (a) anomaly score head (sigmoid), (b) segmentation/heatmap head (upsampling)

4. Training Procedure
   - Loss functions (focal/BCE + dice)
   - Class-imbalance strategies (weights, sampling)
   - Augmentation (rotations ±15°, flips, noise)
   - Optimization (Adam/SGD, LR 1e-5-1e-2)
   - Batch size (4-64)
   - Epochs (10-200)
   - Early stopping
   - Domain adaptation options (instance norm, style transfer, test-time adaptation)

5. Calibration (140)
   - Temperature scaling / isotonic regression
   - Calibrated anomaly score in [0,1]
   - ECE target ≤0.05

6. Explainability (150)
   - Grad-CAM/Integrated Gradients
   - Mapping to heatmap (0-255)
   - Smoothing
   - Confidence-weighted overlay

7. Decision & Triage (270)
   - Threshold τ∈[0.1,0.9]
   - Routes to urgent/normal queues
   - Hysteresis for multi-frame series
   - Optional double-read trigger when 0.45≤score≤0.55

8. UI (160, 300)
   - Controls, overlays, metadata, audit log
   - Human-in-the-loop feedback
   - Active learning pool

9. Deployment & Privacy
   - On-device quantized model vs cloud inference
   - Encryption in transit/at rest
   - PHI handling
   - Logging without PHI

10. Worked Examples
    - Example 1: chest X-ray pneumothorax triage (settings, score, heatmap)
    - Example 2: brain MRI anomaly localization with multi-slice fusion

11. Support Map Paragraph
    - Every claim term points to numbered paragraphs and figures
    - Explicit mapping: "The [claim term] of claim X refers to [paragraph Y] and FIG. Z"

CRITICAL:
- Use "the disclosure" not "the present invention"
- Include ranges for all parameters
- Provide alternatives using "In some embodiments", "In other embodiments"
- Reference figures numerically (FIG. 1, FIG. 2, etc.)
- Use passive/neutral tone
- Include enablement language: "sufficient detail for a person of ordinary skill in the art to make and use"

Generate the DETAILED DESCRIPTION OF THE INVENTION section with all subsections.""",

    "CLAIMS": """Generate CLAIMS section with proper structure and antecedent basis.

INVENTION DESCRIPTION:
{description}

GLOSSARY:
{glossary}

SPECIFICATION:
{specification}

REQUIREMENTS:

Independent Claims (3 required):

Claim 1 - System:
A system comprising:
(a) an acquisition interface configured to receive a medical image;
(b) a preprocessing module configured to normalize and resize the medical image;
(c) a convolutional neural network comprising a plurality of convolutional layers configured to generate an anomaly score for the medical image;
(d) a calibration module configured to transform the anomaly score into a calibrated confidence value; and
(e) a user interface configured to display the medical image with an explainability heatmap and the calibrated confidence value.

Claim 2 - Method:
A method comprising the steps of:
[mirror Claim 1 system steps in gerund form; ensure one-to-one mapping]

Claim 3 - Non-transitory CRM:
A non-transitory computer-readable medium storing instructions that, when executed by a processor, cause the processor to perform the method of claim 2.

Dependent Claims (10-15 required):
- Modality specifics (CT, MRI, X-ray, ultrasound)
- Preprocessing variants (windowing ranges; artifact removal)
- Model variants (U-Net, DenseNet; kernel sizes; depth)
- Training specifics (focal loss; class weights; augmentation types)
- Calibration types (temperature scaling; isotonic)
- Explainability types (Grad-CAM; Integrated Gradients)
- Triage logic (threshold ranges; uncertainty band)
- Deployment (edge device quantization; differential privacy)
- Multi-view fusion (combining PA and lateral, or multi-slice MRI)
- Active learning feedback loop

CRITICAL REQUIREMENTS:
- Each claim must be a single sentence
- Number claims sequentially: 1., 2., 3., etc.
- Independent claims start with "A [system/method/apparatus] comprising:"
- Dependent claims reference preceding claims: "The [system/method] of claim X, wherein..."
- Ensure all claim terms have antecedent basis in specification
- Use consistent terminology from glossary
- Avoid "the present invention"
- Avoid unnecessary "said" references
- NO mixing categories inside one claim (system vs method vs CRM)
- Every claim noun must be supported in Detailed Description (by paragraph number and figure numeral)

Generate the CLAIMS section with all claims properly formatted.""",

    "ABSTRACT": """Generate the ABSTRACT OF THE DISCLOSURE section.

INVENTION DESCRIPTION:
{description}

GLOSSARY:
{glossary}

REQUIREMENTS:
- Exactly ≤150 words (count carefully)
- Single paragraph
- Focus on what it does, not how it's better
- Include: "calibrated anomaly score" + "explainability heatmap" + "triage"
- No legalese
- No limitations
- No "the present invention"
- Technical and specific

Generate the ABSTRACT OF THE DISCLOSURE (≤150 words, single paragraph).""",

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
    "only",  # In spec context (narrowing)
    "must",  # In spec context (narrowing)
    "always",  # In spec context (narrowing)
    "essential"  # In spec context (narrowing)
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

