# U9 "DATA PLANE" — design (concern: "the things exist, but there's no language")

## Concern (2026-08-30)
The glove honestly rejected a video host → but that's a HOLE: a whole class of software
(files, media, streams, pipelines, ML) can't be implemented and can't be guaranteed.

## Thesis
The data plane HAS a math — not the semantics of bytes, but:
reference bookkeeping + measurable output properties + hash idempotence.
This is exactly what real data systems guarantee. It all maps onto the engine's
existing mechanisms.

## Mechanisms (all — reuse)
1. TYPE blob (types-2, like D66): in state/events — a reference
   {hash: str, size: int, mime: str}; the bytes — in a blob store behind the membrane;
   log/replay see only references. The court proves: provenance is complete,
   orphans are impossible, quotas are preserved (ordinary invariants).
2. transforms: skills-over-blobs (ribosome, D27): intent (a command) +
   probe_contract — a bool-Expr over int/str facts of the output probe
   (ffprobe/identify/wc: duration_s, width, height, vcodec, rows...).
   Every output is MEASURED by gates, not taken on faith.
3. Determinism via certification (D6): cache by hash(input)+command+version;
   retry is idempotent; same input -> same output hash — a guarantee.
4. A pipeline = a saga (D54: emit-cascades of job states); realtime delivery =
   membrane assumptions (latency/error_rate -> drift -> REVOKE, D43).

## The honest boundary (remains, but narrow)
Perceptual quality (the picture is "good") — unprovable by anyone;
only proxy-probes (bitrate, resolution, duration).

## Wave exam (the glove from both sides)
That very video host: upload (a reference) -> transcode saga into 3 resolutions
(a mock-ffmpeg island with probe contracts) -> court: provenance+non-loss
proven; probes: every output measured; kill -9 mid-pipeline -> replay
with no lost jobs and no re-transcode (cache by hash).

## Status: DESIGN. Launch command: "smash out U9."
