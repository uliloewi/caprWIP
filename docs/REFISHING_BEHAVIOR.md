# Refishing behavior (current)

**Use new FST? = ON**
- Compile the transducer text from the editor.
- Refish using the freshly compiled FST.

**Use new FST? = OFF**
- Skip compilation.
- Use any existing compiled FST binaries (`*.bin`) found via `fst_index`.
- If no binaries exist, backend returns JSON:
  {"message":"No transducer available: turn on 'Use new FST?' or provide a default transducer file (refishing-fst2.txt)."}

**Error handling**
- Backend returns JSON on known runtime errors (no HTML traceback).
- Unknown/missing doculects are skipped with a log line, not a crash.
