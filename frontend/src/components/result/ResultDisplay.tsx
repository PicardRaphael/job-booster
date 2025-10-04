"use client";

import { Copy, Check } from "lucide-react";
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { GenerateResponse } from "@/types/api";

interface ResultDisplayProps {
  data: GenerateResponse;
}

const OUTPUT_LABELS: Record<string, string> = {
  email: "Email de candidature",
  linkedin: "Message LinkedIn",
  letter: "Lettre de motivation",
};

export function ResultDisplay({ data }: ResultDisplayProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(data.output);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle>{OUTPUT_LABELS[data.output_type]}</CardTitle>
            <CardDescription>
              Généré avec succès • {data.sources.length} sources utilisées
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopy}
            className="gap-2"
          >
            {copied ? (
              <>
                <Check className="h-4 w-4" />
                Copié
              </>
            ) : (
              <>
                <Copy className="h-4 w-4" />
                Copier
              </>
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Generated Content */}
        <div className="rounded-lg bg-muted p-6">
          <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
            {data.output}
          </pre>
        </div>

        {/* Sources */}
        {data.sources.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-sm font-medium">Sources utilisées</h3>
            <div className="grid gap-3">
              {data.sources.map((source, index) => (
                <div
                  key={source.id}
                  className="rounded-lg border bg-card p-4 text-sm"
                >
                  <div className="mb-2 flex items-center justify-between">
                    <Badge variant="secondary">{source.source}</Badge>
                    <span className="text-xs text-muted-foreground">
                      Score: {(source.score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-muted-foreground">{source.text}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Trace ID */}
        {data.trace_id && (
          <div className="text-xs text-muted-foreground">
            Trace ID: {data.trace_id}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
