#!/usr/bin/env python3
"""
chunk_lui_packets_for_fm.py

Take Stage-1 LUI packets JSONL and split into smaller "FM prompt-ready" chunks.

Input (JSONL): lines like:
{
  "schema": "lui.packet.stage1",
  "mode": "final-human",
  "conversation_id": "...",
  "conversation_title": "...",          # optional
  "packet_index": 0,
  "max_chars": 24000,
  "turns": [ { "message_row_id":..., "role":..., "text":... }, ... ]
}

Output (folder):
  out_dir/
	manifest.json
	<conversation_id>/
	  p0000_c0000.json
	  p0000_c0001.json
	  p0001_c0000.json
	  ...

Each chunk file:
{
  "schema": "lui.chunk.stage1.fm",
  "mode": "...",
  "conversation_id": "...",
  "conversation_title": "...",          # if present in input + --include-titles
  "packet_index": 0,
  "chunk_index": 0,
  "max_chars": 24000,
  "target_chars": 16000,
  "reserve_chars": 2000,
  "turn_index_range": [start, end],     # indices within original packet.turns[]
  "turns": [ ...subset of turns... ],
  "approx_char_count": 15321
}

Notes:
- Deterministic order: (conversation_id, packet_index) then in-order turns.
- Budget model: counts only rendered turn["text"] length + 2 chars newline padding.
- Keeps turns with null text (they cost 0 chars). You can drop them with --drop-null-text.
- Safe for re-running: clears output dir only if --clean is passed.

Typical usage:
  python3 code/export/chunk_lui_packets_for_fm.py \
	--in data/artifacts/lui_packets.jsonl \
	--out data/artifacts/fm_chunks \
	--target-chars 16000 \
	--reserve-chars 2000 \
	--include-titles \
	--clean
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional, Tuple


@dataclass(frozen=True)
class PacketKey:
	conversation_id: str
	packet_index: int


def read_jsonl(path: str) -> Iterator[Dict[str, Any]]:
	with open(path, "r", encoding="utf-8") as f:
		for line_no, line in enumerate(f, start=1):
			line = line.strip()
			if not line:
				continue
			try:
				yield json.loads(line)
			except json.JSONDecodeError as e:
				raise SystemExit(f"Invalid JSON on line {line_no} of {path}: {e}") from e


def safe_name(s: str) -> str:
	# folder-safe; keep deterministic.
	s = s.strip()
	s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
	return s[:200] if len(s) > 200 else s


def approx_turn_cost(turn: Dict[str, Any]) -> int:
	t = turn.get("text", None)
	if not t:
		return 0
	return len(t) + 2  # newline-ish padding


def ensure_dir(p: str) -> None:
	os.makedirs(p, exist_ok=True)


def write_json(path: str, obj: Dict[str, Any]) -> None:
	with open(path, "w", encoding="utf-8") as f:
		json.dump(obj, f, ensure_ascii=False, indent=2)


def main() -> None:
	ap = argparse.ArgumentParser()
	ap.add_argument("--in", dest="in_path", required=True, help="Input JSONL (lui_packets.jsonl)")
	ap.add_argument("--out", dest="out_dir", required=True, help="Output directory for chunks")
	ap.add_argument("--target-chars", type=int, default=16000, help="Target chars per FM chunk (payload budget)")
	ap.add_argument("--reserve-chars", type=int, default=2000, help="Reserve chars for prompt modifiers/system text")
	ap.add_argument("--include-titles", action="store_true", help="Carry conversation_title into chunk files")
	ap.add_argument("--drop-null-text", action="store_true", help="Drop turns where turn.text is null/empty")
	ap.add_argument("--clean", action="store_true", help="Delete output directory before writing")
	args = ap.parse_args()

	in_path = os.path.expanduser(args.in_path)
	out_dir = os.path.expanduser(args.out_dir)

	if args.target_chars <= 0:
		raise SystemExit("--target-chars must be > 0")
	if args.reserve_chars < 0:
		raise SystemExit("--reserve-chars must be >= 0")
	if args.reserve_chars >= args.target_chars:
		raise SystemExit("--reserve-chars must be < --target-chars")

	payload_budget = args.target_chars - args.reserve_chars

	if args.clean and os.path.exists(out_dir):
		shutil.rmtree(out_dir)
	ensure_dir(out_dir)

	# Load and sort packets deterministically.
	packets: List[Dict[str, Any]] = list(read_jsonl(in_path))

	def key_fn(p: Dict[str, Any]) -> Tuple[str, int]:
		return (p.get("conversation_id", ""), int(p.get("packet_index", 0)))

	packets.sort(key=key_fn)

	manifest: Dict[str, Any] = {
		"schema": "lui.chunk.manifest.fm.v1",
		"input": os.path.basename(in_path),
		"output_dir": out_dir,
		"target_chars": args.target_chars,
		"reserve_chars": args.reserve_chars,
		"payload_budget": payload_budget,
		"chunks": [],
		"stats": {
			"packets_in": len(packets),
			"chunks_out": 0,
			"turns_out": 0,
		},
	}

	for p in packets:
		conv_id = str(p.get("conversation_id", ""))
		if not conv_id:
			continue

		conv_title = p.get("conversation_title")
		packet_index = int(p.get("packet_index", 0))
		mode = p.get("mode", "final-human")
		turns = p.get("turns", [])
		if not isinstance(turns, list):
			continue

		if args.drop_null_text:
			turns = [t for t in turns if t.get("text")]

		# Output subdir per conversation
		conv_dir = os.path.join(out_dir, safe_name(conv_id))
		ensure_dir(conv_dir)

		chunk_index = 0
		buf: List[Dict[str, Any]] = []
		buf_cost = 0
		start_i = 0

		def flush(end_i_exclusive: int) -> None:
			nonlocal chunk_index, buf, buf_cost, start_i

			if not buf:
				return

			approx_chars = buf_cost
			chunk_obj: Dict[str, Any] = {
				"schema": "lui.chunk.stage1.fm",
				"mode": mode,
				"conversation_id": conv_id,
				"packet_index": packet_index,
				"chunk_index": chunk_index,
				"max_chars": int(p.get("max_chars", 0)) or None,
				"target_chars": args.target_chars,
				"reserve_chars": args.reserve_chars,
				"payload_budget": payload_budget,
				"turn_index_range": [start_i, end_i_exclusive - 1],
				"turns": buf,
				"approx_char_count": approx_chars,
			}
			if args.include_titles:
				chunk_obj["conversation_title"] = conv_title

			fname = f"p{packet_index:04d}_c{chunk_index:04d}.json"
			out_path = os.path.join(conv_dir, fname)
			write_json(out_path, chunk_obj)

			manifest["chunks"].append(
				{
					"path": os.path.relpath(out_path, out_dir),
					"conversation_id": conv_id,
					"packet_index": packet_index,
					"chunk_index": chunk_index,
					"turn_index_range": chunk_obj["turn_index_range"],
					"approx_char_count": approx_chars,
				}
			)

			manifest["stats"]["chunks_out"] += 1
			manifest["stats"]["turns_out"] += len(buf)

			# reset
			chunk_index += 1
			buf = []
			buf_cost = 0
			start_i = end_i_exclusive

		for i, t in enumerate(turns):
			cost = approx_turn_cost(t)

			# If adding would exceed payload budget, flush current chunk first.
			if buf and (buf_cost + cost) > payload_budget:
				flush(i)

			buf.append(t)
			buf_cost += cost

			# If a single turn is huge (exceeds budget), emit it alone.
			if buf and buf_cost > payload_budget:
				flush(i + 1)

		flush(len(turns))

	# write manifest
	write_json(os.path.join(out_dir, "manifest.json"), manifest)

	print("Wrote FM chunks:")
	print(f"  in:  {in_path}")
	print(f"  out: {out_dir}")
	print(f"  packets: {manifest['stats']['packets_in']}")
	print(f"  chunks:  {manifest['stats']['chunks_out']}")
	print(f"  turns:   {manifest['stats']['turns_out']}")
	print(f"  payload_budget_chars: {payload_budget} (target {args.target_chars} - reserve {args.reserve_chars})")


if __name__ == "__main__":
	main()
