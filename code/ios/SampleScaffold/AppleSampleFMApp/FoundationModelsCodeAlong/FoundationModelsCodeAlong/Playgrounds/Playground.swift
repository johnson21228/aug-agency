/*
See the LICENSE.txt file for this sample’s licensing information.

Abstract:
A Playground for testing Foundation Models framework features.
*/

import FoundationModels
import Playgrounds


#Playground {
    let model = SystemLanguageModel.default

    switch model.availability {
    case .available:
        print("Foundation Models is available and ready to go!")

    default:
        print("Model unavailable: \(model.availability)")
        return
    }

    // MARK: Load LUIs via app code
    let luis: [LUIRecord]
    do {
        luis = try IAMDataProvider.sampleLUIs(limit: 5)
        print("📄 Loaded \(luis.count) LUIs from iam.db")
    } catch {
        print("❌ Failed to load LUIs: \(error)")
        return
    }

    let session = LanguageModelSession()

    for lui in luis {
        let prompt = """
        Analyze the following message:

        ROLE: \(lui.role)
        TIME: \(lui.createdAt)

        TEXT:
        \(lui.text)

        Provide:
        - mainIntent: a 1-sentence description
        - isQuestion: true or false
        - topics: 1–5 short labels
        """

        do {
            let reply = try await session.respond(to: prompt)
            print("\n--- LUI \(lui.id.prefix(8)) ---")
            print(reply.content)
        } catch {
            print("❌ FM error: \(error)")
        }
    }
}
