//
//  FoundationModelsCodeAlongApp.swift
//  FoundationModelsCodeAlong
//

import SwiftUI

@main
struct FoundationModelsCodeAlongApp: App {

    init() {
        do {
            try IAMPaths.ensureDatabasePresent()
            print("[IAM] Database verified at: \(IAMPaths.dbURL.path)")
        } catch {
            print("[IAM] ERROR ensuring iam.db: \(error)")
        }

        #if DEBUG
        // Run a simple DB smoke test on launch
        //runIAMDBSmokeTest()
        #endif
    }

    var body: some Scene {
        WindowGroup {
            LandmarksHomeView()
        }
    }
}
