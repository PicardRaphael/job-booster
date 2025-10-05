"use client";

import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Upload, FileText } from "lucide-react";

interface OfferInputProps {
  value: string;
  onChange: (value: string) => void;
  onFileUpload?: (content: string) => void;
}

export function OfferInput({ value, onChange, onFileUpload }: OfferInputProps) {
  const [fileName, setFileName] = useState<string | null>(null);
  const isValid = value.length >= 50;
  const charCount = value.length;

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.md')) {
      alert('Seuls les fichiers .md sont acceptés');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      setFileName(file.name);
      if (onFileUpload) {
        onFileUpload(content);
      } else {
        onChange(content);
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <Label htmlFor="job-offer">Offre d'emploi</Label>
        <div className="flex gap-2">
          <input
            type="file"
            id="file-upload"
            accept=".md"
            onChange={handleFileUpload}
            className="hidden"
          />
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => document.getElementById('file-upload')?.click()}
          >
            <Upload className="h-4 w-4" />
            Importer .md
          </Button>
        </div>
      </div>

      {fileName && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <FileText className="h-4 w-4" />
          <span>{fileName}</span>
        </div>
      )}

      <Textarea
        id="job-offer"
        placeholder="Collez l'offre d'emploi ici ou importez un fichier .md (minimum 50 caractères)..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="min-h-[280px] resize-y"
      />
      <div className="flex items-center justify-between text-xs">
        <span className={isValid ? "text-primary" : "text-muted-foreground"}>
          {isValid ? "✓ Prêt à générer" : "Minimum 50 caractères requis"}
        </span>
        <span className="text-muted-foreground">{charCount} caractères</span>
      </div>
    </div>
  );
}
