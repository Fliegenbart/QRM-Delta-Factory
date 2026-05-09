/**
 * Document Upload Component
 *
 * Allows users to upload documents for risk analysis.
 * Supports drag-and-drop and file selection.
 */

"use client";

import { useState, useCallback, useRef } from "react";
import { Upload, FileText, X, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { useI18n } from "@/src/lib/i18n";

export interface UploadedDocument {
  id: string;
  name: string;
  type: string;
  size: number;
  content: string;
  uploadedAt: string;
}

interface DocumentUploadProps {
  onDocumentsChange: (documents: UploadedDocument[]) => void;
  documents: UploadedDocument[];
  maxFiles?: number;
  maxSizeMb?: number;
}

export function DocumentUpload({
  onDocumentsChange,
  documents,
  maxFiles = 10,
  maxSizeMb = 5
}: DocumentUploadProps) {
  const { t, locale } = useI18n();
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const labels = {
    title: locale === "de" ? "Dokumente hochladen" : "Upload Documents",
    dragDrop: locale === "de"
      ? "Dateien hierher ziehen oder klicken zum Auswählen"
      : "Drag files here or click to select",
    supported: locale === "de"
      ? "Unterstützt: PDF, DOCX, TXT, MD, CSV (max. {size}MB)"
      : "Supported: PDF, DOCX, TXT, MD, CSV (max {size}MB)",
    processing: locale === "de" ? "Verarbeite..." : "Processing...",
    uploadedDocs: locale === "de" ? "Hochgeladene Dokumente" : "Uploaded Documents",
    noDocuments: locale === "de"
      ? "Noch keine Dokumente hochgeladen. Lade Dokumente hoch für eine echte Risikoanalyse."
      : "No documents uploaded yet. Upload documents for a real risk analysis.",
    usingMock: locale === "de"
      ? "Demo-Modus: Realistische Mock-Dokumente werden verwendet"
      : "Demo Mode: Using realistic mock documents",
    remove: locale === "de" ? "Entfernen" : "Remove",
    clearAll: locale === "de" ? "Alle entfernen" : "Clear all",
  };

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const processFiles = useCallback(async (files: FileList) => {
    setIsProcessing(true);
    setError(null);

    const newDocuments: UploadedDocument[] = [];

    for (const file of Array.from(files)) {
      // Check file size
      if (file.size > maxSizeMb * 1024 * 1024) {
        setError(`${file.name}: File too large (max ${maxSizeMb}MB)`);
        continue;
      }

      // Check file type
      const allowedTypes = [
        "text/plain",
        "text/markdown",
        "text/csv",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
      ];
      const allowedExtensions = [".txt", ".md", ".csv", ".pdf", ".docx", ".doc"];

      const hasAllowedType = allowedTypes.includes(file.type);
      const hasAllowedExtension = allowedExtensions.some(ext =>
        file.name.toLowerCase().endsWith(ext)
      );

      if (!hasAllowedType && !hasAllowedExtension) {
        setError(`${file.name}: Unsupported file type`);
        continue;
      }

      try {
        let content = "";

        // For text-based files, read directly
        if (file.type.startsWith("text/") ||
            file.name.endsWith(".txt") ||
            file.name.endsWith(".md") ||
            file.name.endsWith(".csv")) {
          content = await file.text();
        } else if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
          // For PDF, we'll extract text on the server or show placeholder
          content = `[PDF Document: ${file.name}]\n\nNote: PDF text extraction will be processed server-side.\nFile size: ${(file.size / 1024).toFixed(1)} KB`;
        } else if (file.name.endsWith(".docx") || file.name.endsWith(".doc")) {
          // For Word docs, show placeholder
          content = `[Word Document: ${file.name}]\n\nNote: Word document extraction will be processed server-side.\nFile size: ${(file.size / 1024).toFixed(1)} KB`;
        }

        newDocuments.push({
          id: `doc-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
          name: file.name,
          type: file.type || guessType(file.name),
          size: file.size,
          content,
          uploadedAt: new Date().toISOString()
        });
      } catch (err) {
        console.error(`Error processing ${file.name}:`, err);
        setError(`Error processing ${file.name}`);
      }
    }

    // Check max files
    const totalFiles = documents.length + newDocuments.length;
    if (totalFiles > maxFiles) {
      setError(`Maximum ${maxFiles} files allowed`);
      const allowed = maxFiles - documents.length;
      newDocuments.splice(allowed);
    }

    if (newDocuments.length > 0) {
      onDocumentsChange([...documents, ...newDocuments]);
    }

    setIsProcessing(false);
  }, [documents, maxFiles, maxSizeMb, onDocumentsChange]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files.length > 0) {
      processFiles(e.dataTransfer.files);
    }
  }, [processFiles]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFiles(e.target.files);
    }
  }, [processFiles]);

  const removeDocument = useCallback((id: string) => {
    onDocumentsChange(documents.filter(d => d.id !== id));
  }, [documents, onDocumentsChange]);

  const clearAll = useCallback(() => {
    onDocumentsChange([]);
  }, [onDocumentsChange]);

  return (
    <div className="space-y-4">
      {/* Upload Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`
          relative cursor-pointer rounded-2xl border-2 border-dashed p-8
          transition-all duration-200 text-center
          ${isDragging
            ? "border-teal-500 bg-teal-50 dark:bg-teal-950/30"
            : "border-slate-300 dark:border-slate-600 hover:border-teal-400 hover:bg-slate-50 dark:hover:bg-slate-800/50"
          }
          ${isProcessing ? "pointer-events-none opacity-60" : ""}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".txt,.md,.csv,.pdf,.docx,.doc"
          onChange={handleFileSelect}
          className="hidden"
        />

        {isProcessing ? (
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="h-10 w-10 animate-spin text-teal-500" />
            <span className="text-sm text-slate-600 dark:text-slate-400">
              {labels.processing}
            </span>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className={`
              rounded-full p-4 transition-colors
              ${isDragging
                ? "bg-teal-100 dark:bg-teal-900"
                : "bg-slate-100 dark:bg-slate-800"
              }
            `}>
              <Upload className={`h-8 w-8 ${isDragging ? "text-teal-600" : "text-slate-500"}`} />
            </div>
            <div>
              <p className="font-medium text-slate-700 dark:text-slate-300">
                {labels.dragDrop}
              </p>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                {labels.supported.replace("{size}", maxSizeMb.toString())}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex items-center gap-2 rounded-xl border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/30 px-4 py-3 text-sm text-red-700 dark:text-red-300">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Document List */}
      <div className="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-700 px-4 py-3">
          <h3 className="font-medium text-slate-800 dark:text-white">
            {labels.uploadedDocs}
          </h3>
          {documents.length > 0 && (
            <button
              onClick={clearAll}
              className="text-xs text-red-600 hover:text-red-700 dark:text-red-400"
            >
              {labels.clearAll}
            </button>
          )}
        </div>

        {documents.length === 0 ? (
          <div className="p-6 text-center">
            <div className="flex justify-center mb-3">
              <div className="rounded-full bg-amber-100 dark:bg-amber-900/30 p-3">
                <FileText className="h-6 w-6 text-amber-600 dark:text-amber-400" />
              </div>
            </div>
            <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
              {labels.noDocuments}
            </p>
            <p className="text-xs text-amber-600 dark:text-amber-400 font-medium">
              {labels.usingMock}
            </p>
          </div>
        ) : (
          <ul className="divide-y divide-slate-200 dark:divide-slate-700">
            {documents.map((doc) => (
              <li
                key={doc.id}
                className="flex items-center justify-between px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-700/50"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="rounded-lg bg-teal-100 dark:bg-teal-900/30 p-2">
                    <FileText className="h-4 w-4 text-teal-600 dark:text-teal-400" />
                  </div>
                  <div className="min-w-0">
                    <p className="font-medium text-slate-800 dark:text-white truncate">
                      {doc.name}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {(doc.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeDocument(doc.id)}
                  className="ml-2 rounded-lg p-2 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950/30 dark:hover:text-red-400 transition-colors"
                  title={labels.remove}
                >
                  <X className="h-4 w-4" />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function guessType(filename: string): string {
  const ext = filename.toLowerCase().split(".").pop();
  const types: Record<string, string> = {
    txt: "text/plain",
    md: "text/markdown",
    csv: "text/csv",
    pdf: "application/pdf",
    docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    doc: "application/msword"
  };
  return types[ext || ""] || "application/octet-stream";
}
