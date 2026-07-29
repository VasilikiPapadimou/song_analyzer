1. Manual input
   data/imports/<song>.txt

2. Input reading
   file_manager.input_read()

3. Metadata extraction
   line 1 → artist
   line 2 → song title
   remaining lines → lyrics

4. Export folder creation
   data/exports/<ISO week>/<song_artist_date>/

5. Original input preservation
   original_lyrics.txt

6. Lyrics preprocessing
   - normalize line endings
   - trim spaces
   - remove section labels
   - remove website metadata
   - normalize repeated spaces
   - remove excessive blank lines

7. Evidence numbering
   [1] lyric line
   [2] lyric line
   ...

8. Clean input output
   cleaned_lyrics.txt

9. First LLM call
   prompt + cleaned lyrics + SONG_ANALYSIS_SCHEMA

10. First structural validation
    parse_json()

11. Python metadata assembly

12. Final structural validation
    validate_final_analysis()

13. Final Pipeline 1 output
    analysis.json


Pipeline 1 implementation       ✅
        ↓
Pipeline 1 validation           ← βρισκόμαστε εδώ
        ↓
Pipeline 1 evaluation
        ↓
Pipeline 1 acceptance criteria
        ↓
Pipeline 2 weekly aggregation