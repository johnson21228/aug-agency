#!/usr/bin/env python3
"""
cap_nodes.py — CAP over node-layer SubDB

Read-only orchestration over:
- provdb_core.db with node layers (nodes, node_members) and atomic events + event_text
- subdb_nodes.db with node_coords + adjacency edges over node_id

Constraints:
- join only by stable IDs
- no semantic search
- composition is ephemeral

This CAP variant treats node_id as the unit of re-entry.
"""

from __future__ import annotations
import sqlite3
from typing import Any, Dict, List

class CAPNodes:
	def __init__(self, provdb_path: str, subdb_nodes_path: str, layer_key: str):
		self.layer_key = layer_key
		self._prov = sqlite3.connect(provdb_path)
		self._prov.row_factory = sqlite3.Row
		self._sub = sqlite3.connect(subdb_nodes_path)
		self._sub.row_factory = sqlite3.Row
		self._assert_schema()

	def close(self) -> None:
		self._prov.close()
		self._sub.close()

	def _assert_schema(self) -> None:
		for t in ["events", "event_text", "nodes", "node_members", "node_layers"]:
			row = self._prov.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone()
			if not row:
				raise RuntimeError(f"provdb missing table: {t}")
		for t in ["node_coords", "edges", "streams", "layer_meta"]:
			row = self._sub.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone()
			if not row:
				raise RuntimeError(f"subdb_nodes missing table: {t}")

	def window(self, center_node_id: int, radius: int) -> List[int]:
		row = self._sub.execute(
			"SELECT stream_id, node_index FROM node_coords WHERE node_id=?", (center_node_id,)
		).fetchone()
		if not row:
			return []
		sid = int(row["stream_id"])
		idx = int(row["node_index"])
		lo = max(0, idx - radius)
		hi = idx + radius
		rows = self._sub.execute(
			"""
			SELECT node_id FROM node_coords
			WHERE stream_id=? AND node_index BETWEEN ? AND ?
			ORDER BY node_index ASC
			""",
			(sid, lo, hi),
		).fetchall()
		return [int(r["node_id"]) for r in rows]

	def reentry_packet(self, center_node_id: int, radius: int = 3, include_text: bool = True) -> Dict[str, Any]:
		node_ids = self.window(center_node_id, radius)
		if not node_ids:
			return {"layer_key": self.layer_key, "center_node_id": center_node_id, "items": []}

		items: List[Dict[str, Any]] = []
		for nid in node_ids:
			nrow = self._prov.execute(
				"""
				SELECT stream_id, node_index, observed_ts_min, observed_ts_max
				FROM nodes
				WHERE layer_key=? AND node_id=?
				""",
				(self.layer_key, nid),
			).fetchone()
			if not nrow:
				continue

			members = self._prov.execute(
				"""
				SELECT member_index, event_id, member_role
				FROM node_members
				WHERE node_id=?
				ORDER BY member_index ASC
				""",
				(nid,),
			).fetchall()

			events_out = []
			for m in members:
				eid = int(m["event_id"])
				erow = self._prov.execute(
					"SELECT actor_type, observed_ts, source_type, source_ref, source_event_key, capture_id FROM events WHERE event_id=?",
					(eid,),
				).fetchone()
				if not erow:
					continue
				text = None
				if include_text:
					trow = self._prov.execute("SELECT text FROM event_text WHERE event_id=?", (eid,)).fetchone()
					text = trow["text"] if trow else None

				events_out.append({
					"event_id": eid,
					"member_role": m["member_role"],
					"actor_type": erow["actor_type"],
					"observed_ts": erow["observed_ts"],
					"capture_id": erow["capture_id"],
					"source": {
						"source_type": erow["source_type"],
						"source_ref": erow["source_ref"],
						"source_event_key": erow["source_event_key"],
					},
					"text": text,
				})

			items.append({
				"node_id": nid,
				"stream_id": int(nrow["stream_id"]),
				"node_index": int(nrow["node_index"]),
				"observed_ts_min": nrow["observed_ts_min"],
				"observed_ts_max": nrow["observed_ts_max"],
				"events": events_out,
			})

		return {
			"layer_key": self.layer_key,
			"center_node_id": center_node_id,
			"radius": radius,
			"items": items,
		}

if __name__ == "__main__":
	import argparse, json
	ap = argparse.ArgumentParser()
	ap.add_argument("--provdb", required=True)
	ap.add_argument("--subdb", required=True)
	ap.add_argument("--layer", required=True)
	ap.add_argument("--center", type=int, required=True)
	ap.add_argument("--radius", type=int, default=3)
	args = ap.parse_args()

	cap = CAPNodes(args.provdb, args.subdb, args.layer)
	pkt = cap.reentry_packet(args.center, radius=args.radius, include_text=True)
	print(json.dumps(pkt, ensure_ascii=False, indent=2))
	cap.close()
