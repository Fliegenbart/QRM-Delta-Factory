/**
 * Document Verification System
 *
 * Provides tools for agents to verify claims against source documents.
 * Uses simple keyword matching for MVP, can be upgraded to semantic search.
 */

import type {
  SourceSnippet,
  DocumentSearchResult,
  VerifiedClaim,
  ClaimConfidence,
} from "./types";
import { demoSnippets } from "../demo-data";

export class DocumentVerifier {
  private snippets: SourceSnippet[];

  constructor(snippets?: SourceSnippet[]) {
    // Use demo snippets if none provided
    this.snippets = snippets || this.loadDemoSnippets();
  }

  /**
   * Search for relevant documents based on query
   */
  searchDocuments(query: string, limit: number = 5): DocumentSearchResult[] {
    const queryTerms = this.tokenize(query);
    const results: Array<DocumentSearchResult & { score: number }> = [];

    for (const snippet of this.snippets) {
      const contentTerms = this.tokenize(snippet.content);
      const titleTerms = this.tokenize(snippet.sectionTitle);
      const allTerms = [...contentTerms, ...titleTerms];

      // Simple TF-IDF-like scoring
      let score = 0;
      for (const term of queryTerms) {
        const termFreq = allTerms.filter(t => t === term).length;
        if (termFreq > 0) {
          score += termFreq * (1 / Math.log(allTerms.length + 1));
        }
        // Boost for exact phrase match
        if (snippet.content.toLowerCase().includes(term)) {
          score += 2;
        }
      }

      if (score > 0) {
        results.push({
          snippetId: snippet.id,
          documentType: snippet.documentType,
          sectionTitle: snippet.sectionTitle,
          content: snippet.content,
          relevanceScore: score,
          score,
        });
      }
    }

    return results
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map(({ score, ...rest }) => rest);
  }

  /**
   * Get a specific snippet by ID
   */
  getSnippet(snippetId: string): SourceSnippet | null {
    return this.snippets.find(s => s.id === snippetId) || null;
  }

  /**
   * Verify a claim against a specific source snippet
   * Returns verification result with confidence level
   */
  verifyClaim(claim: string, snippetId: string): VerifiedClaim {
    const snippet = this.getSnippet(snippetId);

    if (!snippet) {
      return {
        claim,
        sourceSnippetId: snippetId,
        sourceText: null,
        confidence: "UNVERIFIED",
        verificationNote: `Source snippet ${snippetId} not found`,
      };
    }

    // Tokenize and compare
    const claimTerms = this.tokenize(claim);
    const contentTerms = this.tokenize(snippet.content);

    // Calculate overlap
    const matchingTerms = claimTerms.filter(t => contentTerms.includes(t));
    const matchRatio = matchingTerms.length / claimTerms.length;

    // Find the most relevant quote
    const relevantQuote = this.findRelevantQuote(claim, snippet.content);

    let confidence: ClaimConfidence;
    let note: string;

    if (matchRatio > 0.7) {
      confidence = "VERIFIED";
      note = `High term overlap (${Math.round(matchRatio * 100)}%). Claim appears well-supported.`;
    } else if (matchRatio > 0.4) {
      confidence = "INFERRED";
      note = `Partial term overlap (${Math.round(matchRatio * 100)}%). Claim may be implied but not explicit.`;
    } else if (this.hasContradiction(claim, snippet.content)) {
      confidence = "CONTRADICTED";
      note = "Source content appears to contradict this claim.";
    } else {
      confidence = "UNVERIFIED";
      note = `Low term overlap (${Math.round(matchRatio * 100)}%). Claim not clearly supported by source.`;
    }

    return {
      claim,
      sourceSnippetId: snippetId,
      sourceText: relevantQuote,
      confidence,
      verificationNote: note,
    };
  }

  /**
   * Batch verify all claims in a list
   */
  verifyAllClaims(claims: Array<{ claim: string; sourceSnippetId: string | null }>): VerifiedClaim[] {
    return claims.map(c => {
      if (!c.sourceSnippetId) {
        return {
          claim: c.claim,
          sourceSnippetId: null,
          sourceText: null,
          confidence: "UNVERIFIED" as ClaimConfidence,
          verificationNote: "No source snippet linked",
        };
      }
      return this.verifyClaim(c.claim, c.sourceSnippetId);
    });
  }

  /**
   * Find snippets that might support a given claim
   */
  findSupportingSnippets(claim: string): DocumentSearchResult[] {
    return this.searchDocuments(claim, 3);
  }

  // ===========================================================================
  // PRIVATE HELPERS
  // ===========================================================================

  private loadDemoSnippets(): SourceSnippet[] {
    return demoSnippets.map(s => ({
      id: s.id,
      documentId: s.documentId,
      documentType: s.documentType,
      sectionTitle: s.sectionTitle,
      content: s.text, // Demo data uses 'text' instead of 'content'
      lineReference: s.lineReference,
      snippetHash: s.snippetHash,
    }));
  }

  private tokenize(text: string): string[] {
    return text
      .toLowerCase()
      .replace(/[^\w\säöüß]/g, " ")
      .split(/\s+/)
      .filter(t => t.length > 2)
      .filter(t => !this.isStopWord(t));
  }

  private isStopWord(word: string): boolean {
    const stopWords = new Set([
      "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
      "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
      "be", "have", "has", "had", "do", "does", "did", "will", "would",
      "could", "should", "may", "might", "must", "shall", "can", "need",
      "der", "die", "das", "und", "oder", "aber", "in", "an", "auf", "zu",
      "für", "von", "mit", "bei", "aus", "als", "ist", "war", "sind", "waren",
      "this", "that", "these", "those", "it", "its", "they", "them", "their",
    ]);
    return stopWords.has(word);
  }

  private findRelevantQuote(claim: string, content: string): string {
    const claimTerms = this.tokenize(claim);
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 10);

    let bestSentence = "";
    let bestScore = 0;

    for (const sentence of sentences) {
      const sentenceTerms = this.tokenize(sentence);
      const matchCount = claimTerms.filter(t => sentenceTerms.includes(t)).length;
      if (matchCount > bestScore) {
        bestScore = matchCount;
        bestSentence = sentence.trim();
      }
    }

    if (bestSentence.length > 200) {
      return bestSentence.slice(0, 200) + "...";
    }
    return bestSentence || content.slice(0, 150) + "...";
  }

  private hasContradiction(claim: string, content: string): boolean {
    const contradictionPatterns = [
      { positive: "approved", negative: "not approved" },
      { positive: "validated", negative: "not validated" },
      { positive: "confirmed", negative: "not confirmed" },
      { positive: "compliant", negative: "non-compliant" },
      { positive: "effective", negative: "ineffective" },
      { positive: "acceptable", negative: "unacceptable" },
    ];

    const claimLower = claim.toLowerCase();
    const contentLower = content.toLowerCase();

    for (const pattern of contradictionPatterns) {
      if (claimLower.includes(pattern.positive) && contentLower.includes(pattern.negative)) {
        return true;
      }
      if (claimLower.includes(pattern.negative) && contentLower.includes(pattern.positive)) {
        return true;
      }
    }

    return false;
  }
}

// Singleton instance for easy access
let verifierInstance: DocumentVerifier | null = null;

export function getDocumentVerifier(snippets?: SourceSnippet[]): DocumentVerifier {
  if (!verifierInstance || snippets) {
    verifierInstance = new DocumentVerifier(snippets);
  }
  return verifierInstance;
}
