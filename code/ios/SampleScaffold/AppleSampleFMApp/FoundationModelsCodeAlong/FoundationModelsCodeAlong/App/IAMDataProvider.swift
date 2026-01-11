//
//  IAMDataProvider.swift
//  FoundationModelsCodeAlong
//
//  Created by Steve Johnson on 11/22/25.
//  Copyright © 2025 Apple. All rights reserved.
//

import Foundation
import SQLite3

struct LUIRecord {
    let id: String
    let chartID: String
    let role: String
    let createdAt: String
    let text: String
}

enum IAMDataProvider {

    static func sampleLUIs(limit: Int = 5) throws -> [LUIRecord] {
        // iam.db location you’re already using
        let path = IAMPaths.dbURL.path

        var db: OpaquePointer?
        guard sqlite3_open(path, &db) == SQLITE_OK else {
            throw NSError(
                domain: "IAM",
                code: 1,
                userInfo: [NSLocalizedDescriptionKey: "Failed to open iam.db at \(path)"]
            )
        }
        defer { sqlite3_close(db) }

        let sql = """
        SELECT l.id, l.chart_id, l.local_label, l.created_at,
               c.raw_text, l.span_start, l.span_end
        FROM luis l
        JOIN charts c ON l.chart_id = c.id
        ORDER BY l.created_at
        LIMIT ?
        """

        var stmt: OpaquePointer?
        guard sqlite3_prepare_v2(db, sql, -1, &stmt, nil) == SQLITE_OK else {
            throw NSError(
                domain: "IAM",
                code: 2,
                userInfo: [NSLocalizedDescriptionKey: "Failed to prepare LUI query"]
            )
        }
        defer { sqlite3_finalize(stmt) }

        sqlite3_bind_int(stmt, 1, Int32(limit))

        var results: [LUIRecord] = []

        while sqlite3_step(stmt) == SQLITE_ROW {
            let id        = String(cString: sqlite3_column_text(stmt, 0))
            let chartID   = String(cString: sqlite3_column_text(stmt, 1))
            let role      = String(cString: sqlite3_column_text(stmt, 2))
            let createdAt = String(cString: sqlite3_column_text(stmt, 3))
            let rawText   = String(cString: sqlite3_column_text(stmt, 4))
            let spanStart = Int(sqlite3_column_int(stmt, 5))
            let spanEnd   = Int(sqlite3_column_int(stmt, 6))

            // safe slice
            let clampedStart = max(0, min(spanStart, rawText.count))
            let clampedEnd   = max(clampedStart, min(spanEnd, rawText.count))

            let startIdx = rawText.index(rawText.startIndex, offsetBy: clampedStart)
            let endIdx   = rawText.index(rawText.startIndex, offsetBy: clampedEnd)
            let slice    = String(rawText[startIdx..<endIdx])

            results.append(
                LUIRecord(
                    id: id,
                    chartID: chartID,
                    role: role,
                    createdAt: createdAt,
                    text: slice
                )
            )
        }

        return results
    }
}
