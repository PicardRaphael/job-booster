"use client";

import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

interface OfferInputProps {
  value: string;
  onChange: (value: string) => void;
}

export function OfferInput({ value, onChange }: OfferInputProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor="job-offer">Offre d'emploi</Label>
      <Textarea
        id="job-offer"
        placeholder="Collez l'offre d'emploi ici (minimum 50 caractères)..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="min-h-[300px] resize-y"
      />
      <p className="text-xs text-muted-foreground">
        {value.length} / 50 caractères minimum
      </p>
    </div>
  );
}
