"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { OfferInput } from "@/components/offer/OfferInput";
import { OutputSelector } from "@/components/offer/OutputSelector";
import { ResultDisplay } from "@/components/result/ResultDisplay";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useGenerate } from "@/hooks/useGenerate";
import { OutputType } from "@/types/api";

export default function Home() {
  const [jobOffer, setJobOffer] = useState("");
  const [outputType, setOutputType] = useState<OutputType>("email");
  const { mutate, data, isPending, error } = useGenerate();

  const handleSubmit = () => {
    if (!jobOffer.trim()) return;
    mutate({ job_offer: jobOffer, output_type: outputType });
  };

  const canSubmit = jobOffer.trim().length >= 50 && !isPending;

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto max-w-4xl px-4 py-12 md:py-16">
        {/* Header */}
        <div className="text-center space-y-4 mb-12">
          <h1 className="text-5xl md:text-6xl font-bold tracking-tight">
            <span className="bg-gradient-to-r from-primary via-emerald-400 to-primary bg-clip-text text-transparent">
              JobBooster
            </span>
          </h1>
          <p className="text-muted-foreground text-lg">
            Générez des candidatures personnalisées avec l'IA
          </p>
        </div>

        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle>Nouvelle candidature</CardTitle>
            <CardDescription>
              Collez votre offre d'emploi et choisissez le type de contenu à générer
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <OfferInput value={jobOffer} onChange={setJobOffer} />

            <div className="space-y-3">
              <label className="text-sm font-medium">Type de contenu</label>
              <OutputSelector value={outputType} onChange={setOutputType} />
            </div>

            {error && (
              <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-4 text-sm text-destructive">
                {error instanceof Error ? error.message : "Une erreur est survenue"}
              </div>
            )}

            <Button
              onClick={handleSubmit}
              disabled={!canSubmit}
              className="w-full"
              size="lg"
            >
              {isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Génération en cours...
                </>
              ) : (
                "Générer"
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Result */}
        {data && <ResultDisplay data={data} />}
      </div>
    </main>
  );
}
