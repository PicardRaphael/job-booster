"use client";

import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

interface OfferInputProps {
  value: string;
  onChange: (value: string) => void;
}

export function OfferInput({ value, onChange }: OfferInputProps) {
  const isValid = value.length >= 50;
  const charCount = value.length;

  return (
    <div className="space-y-2">
      <Label htmlFor="job-offer">Offre d'emploi</Label>
      <Textarea
        id="job-offer"
        placeholder="Collez l'offre d'emploi ici (minimum 50 caractères)..."
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
