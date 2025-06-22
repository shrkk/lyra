import React from "react";

const steps = [
  {
    title: "MCP Server",
    description:
      "Handles user requests, orchestrates the workflow, and manages communication between all components.",
  },
  {
    title: "RAG (Retrieval-Augmented Generation)",
    description:
      "Fetches relevant information from internal knowledge or external sources to enhance responses.",
  },
  {
    title: "Spotify API Integration",
    description:
      "Connects to the Spotify API to fetch or control music data as needed.",
  },
  {
    title: "Response Generation",
    description:
      "Combines all results and generates a final response for the user.",
  },
];

export default function LyraWorkflow() {
  return (
    <section className="w-full flex flex-col items-center py-10">
      <h2 className="text-2xl md:text-3xl font-bold mb-8 text-center">How Lyra's Technology Works</h2>
      <div className="flex flex-col md:flex-row md:items-center md:justify-center gap-6 w-full max-w-5xl">
        {steps.map((step, idx) => (
          <div key={step.title} className="relative flex flex-col items-center md:w-1/4">
            <div
              className="group rounded-2xl shadow-xl p-6 flex flex-col justify-center items-center min-w-[220px] max-w-[240px] min-h-[220px] border text-center transition-transform hover:scale-105"
              style={{
                border: "1.5px solid rgba(40, 60, 90, 0.13)",
                background:
                  `
                    linear-gradient(to top, rgba(96,165,250,0.18) 0%, rgba(24,24,28,0.98) 40%),
                    radial-gradient(ellipse at 50% 95%, rgba(96,165,250,0.28) 30%, transparent 70%),
                    #18181c
                  `,
                boxShadow:
                  "0 8px 40px 0 rgba(59,130,246,0.18), 0 2px 24px 0 rgba(59,130,246,0.10)",
                backdropFilter: "blur(2px)",
              }}
            >
              <div className="font-semibold text-lg mb-2 text-white drop-shadow transition duration-200 group-hover:text-blue-100 group-hover:drop-shadow-[0_0_8px_rgba(96,165,250,0.25)]">{step.title}</div>
              <div className="text-gray-300 text-sm leading-snug font-light drop-shadow-sm transition duration-200 group-hover:text-blue-100 group-hover:drop-shadow-[0_0_6px_rgba(96,165,250,0.18)]">{step.description}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
} 