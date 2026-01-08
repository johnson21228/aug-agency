#!/usr/bin/env python3
"""
cap.py — Continuity Access Protocol (CAP)

Minimal read interface over:
- provdb_core.db (provenance + text by stable IDs)
- subdb_core.db (semantic-free continuity geometry)

Design constraints:
- CAP does NOT perform semantic joins inside SubDB.
- CAP does NOT perform semantic search.
- CAP composes by stable IDs only, and composition is view-level (ephemeral).
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple, Dict, Any


@dataclass(frozen=True)
class EventCoord:
	event_id: int
	stream_id: int
	turn_index: int
	observed_ts: Optional[str]


@dataclass(frozen=True)
class StreamRef:
	stream_id: int
	source_type: str
	source_ref: str


class CAP:
	"""
	CAP orchestrates safe read access:
	- SubDB: continuity geometry
	- ProvDB: text/provenance resolution
	"""

	def __init__(self, provdb_path: str | Path, subdb_path: str | Path):
		self.provdb_path = str(provdb_path)
		self.subdb_path = str(subdb_path)
		self._prov = sqlite3.connect(self.provdb_path)
		self._prov.row_factory = sqlite3.Row
		self._sub = sqlite3.connect(self.subdb_path)
		self._sub.row_factory = sqlite3.Row

		# Fail fast if required tables are missing
		self._assert_schema()

	def close(self) -> None:
		self._prov.close()
		self._sub.close()

	# -----------------------------
	# Schema checks
	# -----------------------------

	def _assert_schema(self) -> None:
		prov_tables = self._table_set(self._prov)
		sub_tables = self._table_set(self._sub)

		required_prov = {"events", "event_text"}
		required_sub = {"streams", "event_coords", "edges"}

		missing_prov = required_prov - prov_tables
		missing_sub = required_sub - sub_tables

		if missing_prov:
			raise RuntimeError(f"ProvDB missing tables: {sorted(missing_prov)}")
		if missing_sub:
			raise RuntimeError(f"SubDB missing tables: {sorted(missing_sub)}")

	@staticmethod
	def _table_set(conn: sqlite3.Connection) -> set[str]:
		rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
		return {r[0] for r in rows}

	# -----------------------------
	# SubDB (semantic-free) methods
	# -----------------------------

	def get_stream(self, stream_id: int) -> Optional[StreamRef]:
		r = self._sub.execute(
			"SELECT stream_id, source_type, source_ref FROM streams WHERE stream_id=?",
			(stream_id,),
		).fetchone()
		if not r:
			return None
		return StreamRef(stream_id=int(r["stream_id"]), source_type=r["source_type"], source_ref=r["source_ref"])

	def get_event_coord(self, event_id: int) -> Optional[EventCoord]:
		r = self._sub.execute(
			"SELECT event_id, stream_id, turn_index, observed_ts FROM event_coords WHERE event_id=?",
			(event_id,),
		).fetchone()
		if not r:
			return None
		return EventCoord(
			event_id=int(r["event_id"]),
			stream_id=int(r["stream_id"]),
			turn_index=int(r["turn_index"]),
			observed_ts=r["observed_ts"],
		)

	def get_neighbors_by_adjacency(self, event_id: int, k: int = 2) -> List[int]:
		"""
		Returns a neighborhood by walking adjacency edges out to k steps in each direction.
		This is purely structural and uses only SubDB edges.

		Output is ordered from closest to farther, with event_id excluded.
		"""
		if k <= 0:
			return []

		seen = {event_id}
		frontier = {event_id}
		out: List[int] = []

		for _ in range(k):
			next_frontier = set()

			for nid in frontier:
				# forward edges
				fwd = self._sub.execute(
					"SELECT dst_event_id FROM edges WHERE src_event_id=? AND edge_type='adjacent'",
					(nid,),
				).fetchall()
				for row in fwd:
					eid = int(row["dst_event_id"])
					if eid not in seen:
						seen.add(eid)
						out.append(eid)
						next_frontier.add(eid)

				# reverse edges (who points to nid)
				rev = self._sub.execute(
					"SELECT src_event_id FROM edges WHERE dst_event_id=? AND edge_type='adjacent'",
					(nid,),
				).fetchall()
				for row in rev:
					eid = int(row["src_event_id"])
					if eid not in seen:
						seen.add(eid)
						out.append(eid)
						next_frontier.add(eid)

			frontier = next_frontier
			if not frontier:
				break

		return out

	def get_window_by_turn_index(self, stream_id: int, center_turn_index: int, radius: int = 5) -> List[int]:
		"""
		Returns event_ids in a turn_index window within a stream (semantic-free).
		Ordered by turn_index ascending.
		"""
		lo = max(0, center_turn_index - radius)
		hi = center_turn_index + radius
		rows = self._sub.execute(
			"""
			SELECT event_id FROM event_coords
			WHERE stream_id=? AND turn_index BETWEEN ? AND ?
			ORDER BY turn_index ASC
			""",
			(stream_id, lo, hi),
		).fetchall()
		return [int(r["event_id"]) for r in rows]

	def get_event_id_at(self, stream_id: int, turn_index: int) -> Optional[int]:
		r = self._sub.execute(
			"SELECT event_id FROM event_coords WHERE stream_id=? AND turn_index=?",
			(stream_id, turn_index),
		).fetchone()
		return int(r["event_id"]) if r else None

	# -----------------------------
	# ProvDB methods (by-ID only)
	# -----------------------------

	def get_text(self, event_id: int) -> Optional[str]:
		"""
		Resolve event_id → canonical text.
		No search, no semantics, no joins to SubDB.
		"""
		r = self._prov.execute(
			"SELECT text FROM event_text WHERE event_id=?",
			(event_id,),
		).fetchone()
		return r["text"] if r else None

	def get_provenance(self, event_id: int) -> Optional[Dict[str, Any]]:
		"""
		Resolve event_id → provenance fields stored in provdb events table.
		"""
		r = self._prov.execute(
			"""
			SELECT event_id, capture_id, source_type, source_ref, source_event_key, actor_type, observed_ts, ingested_ts
			FROM events WHERE event_id=?
			""",
			(event_id,),
		).fetchone()
		if not r:
			return None
		return dict(r)

	# -----------------------------
	# IAM-facing composition helpers
	# (ephemeral; do not persist joins)
	# -----------------------------

	def reentry_packet(
		self,
		event_id: int,
		*,
		window_radius: int = 5,
		include_text: bool = True,
	) -> Dict[str, Any]:
		"""
		A minimal re-entry packet:
		- fetch structural context from SubDB (window around event_id)
		- fetch text from ProvDB (optional)
		- returns an ephemeral assembled view (not stored)
		"""
		coord = self.get_event_coord(event_id)
		if not coord:
			return {"event_id": event_id, "error": "event_id not found in SubDB"}

		window_ids = self.get_window_by_turn_index(coord.stream_id, coord.turn_index, radius=window_radius)

		items = []
		for eid in window_ids:
			item = {"event_id": eid}
			c = self.get_event_coord(eid)
			if c:
				item.update({"turn_index": c.turn_index, "observed_ts": c.observed_ts})
			if include_text:
				item["text"] = self.get_text(eid) or ""
			items.append(item)

		return {
			"center_event_id": event_id,
			"stream_id": coord.stream_id,
			"center_turn_index": coord.turn_index,
			"window_radius": window_radius,
			"items": items,
		}
