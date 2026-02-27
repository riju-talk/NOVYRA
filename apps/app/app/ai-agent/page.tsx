"use client"

import { useState } from "react"
import { NotebookLayout } from "@/components/ai-agent/notebook/notebook-layout"
import { ChatAgent } from "@/components/ai-agent/chat-agent"
import { MindMapAgent } from "@/components/ai-agent/mindmap-agent"
import { AssessmentsAgent } from "@/components/ai-agent/assessments-agent"
import { ChartsAgent } from "@/components/ai-agent/charts-agent"
import { WIPSection } from "@/components/wip-feature"
import { Sparkles } from "lucide-react"

export default function AIAgentPage() {
  const [activeTab, setActiveTab] = useState("qa")
  const [selectedDoc, setSelectedDoc] = useState<any | null>(null)

  return (
    <div className="fixed inset-0 pt-16 bg-background">
      <NotebookLayout
        activeTab={activeTab}
        onTabChange={setActiveTab}
        selectedDocId={selectedDoc?.id}
        onDocSelect={setSelectedDoc}
      >
        <div className="h-full w-full">
          {activeTab === "qa" && <ChatAgent contextDoc={selectedDoc} />}
          {activeTab === "mindmap" && (
            <WIPSection
              phase={2}
              estimatedCompletion="February 2025"
              features={[
                "Interactive concept maps with Neo4j visualization",
                "Real-time prerequisite path highlighting",
                "D3.js force-directed graph",
                "Concept clustering by domain",
              ]}
            >
              <MindMapAgent contextDoc={selectedDoc} />
            </WIPSection>
          )}
          {(activeTab === "assessments" || activeTab === "flashcards") && (
            <WIPSection
              phase={2}
              estimatedCompletion="February 2025"
              features={[
                "Spaced repetition flashcards",
                "Auto-generated quizzes from documents",
                "Progressive difficulty adjustment",
                "Rubric-based evaluation integration",
              ]}
            >
              <AssessmentsAgent contextDoc={selectedDoc} />
            </WIPSection>
          )}
          {activeTab === "charts" && (
            <WIPSection
              phase={2}
              estimatedCompletion="March 2025"
              features={[
                "Learning analytics dashboard",
                "Mastery progression over time",
                "Concept heatmaps by domain",
                "Peer comparison insights (anonymized)",
              ]}
            >
              <ChartsAgent contextDoc={selectedDoc} />
            </WIPSection>
          )}
        </div>
      </NotebookLayout>
    </div>
  )
}
