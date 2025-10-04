"use client";

import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import type { OutputType } from "@/types/api";

interface OutputSelectorProps {
  value: OutputType;
  onChange: (value: OutputType) => void;
}

const OPTIONS: { value: OutputType; label: string; description: string }[] = [
  {
    value: "email",
    label: "Email de candidature",
    description: "Email professionnel concis et percutant",
  },
  {
    value: "linkedin",
    label: "Message LinkedIn",
    description: "Message engageant pour une prise de contact",
  },
  {
    value: "letter",
    label: "Lettre de motivation",
    description: "Lettre structurée et complète",
  },
];

export function OutputSelector({ value, onChange }: OutputSelectorProps) {
  return (
    <RadioGroup value={value} onValueChange={(v) => onChange(v as OutputType)}>
      <div className="grid gap-2">
        {OPTIONS.map((option) => (
          <div
            key={option.value}
            className={`flex items-start space-x-3 rounded-lg border p-3.5 transition-all cursor-pointer ${
              value === option.value
                ? 'border-primary bg-primary/5'
                : 'border-border hover:bg-accent'
            }`}
          >
            <RadioGroupItem value={option.value} id={option.value} className="mt-0.5" />
            <Label
              htmlFor={option.value}
              className="flex-1 cursor-pointer space-y-0.5"
            >
              <div className="font-medium">{option.label}</div>
              <div className="text-sm text-muted-foreground">
                {option.description}
              </div>
            </Label>
          </div>
        ))}
      </div>
    </RadioGroup>
  );
}
