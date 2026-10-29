# Azure AI Content Understanding — document OCR showcase

Shows what **Azure AI Content Understanding** (`prebuilt-layout`) extracts from 14 synthetic test PDFs, and how a **vision LLM** (Azure OpenAI) recovers what OCR loses on fund-structure charts.

All data is fictional (made-up names, accounts and IBANs). Nothing here is a real person, fund or account.

## What's here

| Path | What it is |
|---|---|
| `content_understanding_batch_ocr.ipynb` | **Main notebook.** Sends every PDF to Content Understanding one by one, saves + prints each document's markdown, then (optional) runs a vision-LLM pass on the hierarchy charts. |
| `content_understanding_analyze.ipynb` | Original single-document notebook with the full inspection (words, lines, tables, fields). Its default `ANALYZER_ID` (`prebuilt-documentAnalyzer`) did not exist on the resource used here — set it to one that does, e.g. `prebuilt-layout`. |
| `*.pdf` (14 files) | Test documents, 2 variations per type (see below). |
| `results/<name>.md` | The markdown Content Understanding returned for each PDF. |
| `results/<name>_result.json` | Full analyzer result (pages, words, lines, tables, figures, bounding boxes). |
| `results/<name>_hierarchy.json` | Vision-LLM graph (nodes + edges) for the two fund-hierarchy charts. |
| `generate_test_pdfs.py` | Regenerates the 14 test PDFs (needs `reportlab`, `pillow`; uses Windows fonts). |

## The test documents

| # | Type | Files | What it stresses |
|---|---|---|---|
| 1 | Polish / accented names, image-only scans | `01_*` | OCR of ą ę ł ń ó ś ź ż, é ñ ø å on skewed, noisy scans with no text layer |
| 2 | Watermarks | `02_*` | Diagonal and tiled watermarks over body text |
| 3 | Signature over printed name | `03_*` | Handwriting overlapping typed names |
| 4 | Tables + trade order image | `04_*` | Text-based table; scanned (image-only) trade order ticket |
| 5 | Fund hierarchy charts | `05_*` | Boxes and connectors (master-feeder; umbrella with sub-funds and share classes) |
| 6 | Forms with ticked checkboxes | `06_*` | Real form checkboxes; hand-drawn X marks |
| 7 | Trade order with handwriting | `07_*` | Handwritten "Please process Order" / "I certify the order" and filled-in fields |

## What the output looks like (observed on this run)

| Case | Result |
|---|---|
| Polish and accented names (image-only) | Names and IBANs extracted correctly; the register comes back as a table |
| Checkboxes (real and hand-drawn) | Returned as `☑` / `☒` for ticked and `☐` for empty, in the markdown |
| Handwritten order fields and notes | "I certify the order" and the filled-in fields (account, side, ISIN, quantity, limit) read correctly, returned as a table |
| Table (text and image) | Returned as an HTML `<table>` in the markdown |
| Signature over a printed name | **Weakest case**: overlap corrupts some names (e.g. `Przemysław Zieliński` read as `Przemy sław Zzionribjński`) |
| Watermarks | Body text intact, but watermark text leaks into the markdown as noise |
| Hierarchy chart | The whole diagram is returned as **one figure** with a flat text caption — **the arrows and relationships are lost** |

### Vision-LLM pass on the hierarchy charts

Rendering the page to an image and asking an Azure OpenAI vision model for a schema-constrained graph (nodes + edges), cross-checked against the OCR text, recovers the structure:

- **Master-feeder** — 11 nodes, 7 edges: GP manages the master fund; three feeders invest in it; three investor groups invest in the feeders. The three service-provider boxes have no connectors on the chart, and the model reports them as unconnected rather than inventing links.
- **Umbrella** — 15 nodes, 14 edges: umbrella to management company, depositary and 3 sub-funds; each sub-fund to its 3 share classes. The model notes where connectors have no arrowheads, so direction is its own convention.

Output per chart: nodes/edges tables, an indented tree, Mermaid source, and the validation warnings.

## Running it

1. Python 3.10+ and Jupyter. The notebook installs its own packages (`azure-ai-contentunderstanding`, `openai`, `pymupdf`, `pandas`).
2. Put your own resource details in the config cells (the committed notebooks use `<your-resource>` placeholders).
3. Set keys as environment variables — **never paste a key into a notebook**:
   ```
   AZURE_CU_KEY      # Content Understanding resource key
   AZURE_OPENAI_KEY  # Azure OpenAI key (only for the optional vision pass)
   ```
   If a variable isn't set, the notebook prompts for it.
4. Run all cells. Results land in `results/`.

Notes: `prebuilt-layout` returns OCR + layout only (no named fields). To pull specific fields (account number, side, quantity, signature present) you would define a **custom analyzer** with a field schema.
