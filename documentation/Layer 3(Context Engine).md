# Context Engine (Layer 3)

## Content Understanding System

# 1. Introduction

The Context Engine converts raw content into structured features and then scores those features for downstream use.

The current system supports:
- Image content
- Text content
- Video content

Each modality runs through its own processing path while producing a unified feature payload that the scoring layer can consume.

---

# 2. System Architecture

```mermaid
flowchart LR

	A[Content Item]:::dark
	B[Image Processing]:::dark
	C[Text Processing]:::dark
	D[Video Processing]:::dark
	E[LLM Scoring]:::dark

	A --> B
	A --> C
	A --> D

	B --> E
	C --> E
	D --> E

	E --> F[Engagement Report]:::dark

	classDef dark fill:#666666,color:#ffffff,stroke:#333333,stroke-width:2px
```

The Context Engine is divided into four major stages:

- Image Processing
- Text Processing
- Video Processing
- Engagement Scoring

Each stage is modality-specific and communicates through standardized feature structures.

---

# 3. Image Processing Pipeline

## 3.1 Motivation

Image analysis extracts object, face, color, and text signals from a single image.

## 3.2 Complete Workflow

```mermaid
flowchart

	A[Image Path]:::dark
	B[Image VLM]:::dark
	C[Object Schema]:::dark
	D[Face Schema]:::dark
	E[Color Analysis]:::dark
	F[Image Features]:::dark

	A --> B
	B --> C
	B --> D
	A --> E
	C --> F
	D --> F
	E --> F

	classDef dark fill:#666666,color:#ffffff,stroke:#333333,stroke-width:2px
```

## 3.3 Feature Output

The image pipeline returns:

```text
Objects detected
Faces detected
Facial emotions
Visual appeal score
Color analysis
Text content
```

---

# 4. Text Processing Pipeline

## 4.1 Motivation

Text analysis extracts sentiment, emotion, readability, and trigger signals from a caption or post.

## 4.2 Complete Workflow

```mermaid
flowchart

	A[Text Input]:::dark
	B[Sentiment Model]:::dark
	C[Emotion Model]:::dark
	D[Readability Metrics]:::dark
	E[Trigger Lexicon]:::dark
	F[Text Features]:::dark

	A --> B
	A --> C
	A --> D
	A --> E
	B --> F
	C --> F
	D --> F
	E --> F

	classDef dark fill:#666666,color:#ffffff,stroke:#333333,stroke-width:2px
```

## 4.3 Feature Output

The text pipeline returns:

```text
Raw text
Sentiment
Readability
Emotional triggers
```

---

# 5. Video Processing Pipeline

## 5.1 Motivation

Video analysis combines transcript, subtitles, editing pace, audio, frame emotion, and hook signals.

## 5.2 Complete Workflow

```mermaid
flowchart

	A[Video Path]:::dark
	B[Transcript]:::dark
	C[Subtitles]:::dark
	D[Editing Pace]:::dark
	E[Audio Metrics]:::dark
	F[Frame Emotion]:::dark
	G[Hook Score]:::dark
	H[Video Features]:::dark

	A --> B
	A --> C
	A --> D
	A --> E
	A --> F
	B --> G
	D --> G
	E --> G

	B --> H
	C --> H
	D --> H
	E --> H
	F --> H
	G --> H

	classDef dark fill:#666666,color:#ffffff,stroke:#333333,stroke-width:2px
```

## 5.3 Feature Output

The video pipeline returns:

```text
Transcript
Subtitles
Editing pace
Audio analysis
Frame emotions
Hook analysis
```

---

# 6. Scoring Layer

## 6.1 Motivation

The scoring layer converts modality features into engagement scores.

## 6.2 Complete Workflow

```mermaid
flowchart LR

	A[Feature Payload]:::dark
	B[Gemini Scoring]:::dark
	C[Primary Scores]:::dark
	D[Composite Scores]:::dark
	E[Engagement Result]:::dark

	A --> B
	B --> C
	C --> D
	C --> E
	D --> E

	classDef dark fill:#666666,color:#ffffff,stroke:#333333,stroke-width:2px
```

## 6.3 Output

The scoring layer returns:

```text
Per-dimension scores
Shareability
Saveability
Model name
```

---

# 7. Entry Points

- `Context_Engine/core/orchestrator.py`
- `Context_Engine/test.py`

---

# 8. Notes

The logic remains unchanged. The code is organized into separate files by responsibility so each modality and helper step can be maintained independently.