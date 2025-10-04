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
    <main className="min-h-screen bg-gradient-to-b from-background to-muted/20 p-4 md:p-8">
      <div className="mx-auto max-w-6xl space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">JobBooster</h1>
          <p className="text-muted-foreground text-lg">
            Boostez vos candidatures avec l'IA
          </p>
        </div>

        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle>Nouvelle candidature</CardTitle>
            <CardDescription>
              Collez l'offre d'emploi ci-dessous et choisissez le type de contenu à générer
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <OfferInput value={jobOffer} onChange={setJobOffer} />

            <div className="space-y-2">
              <label className="text-sm font-medium">Type de contenu</label>
              <OutputSelector value={outputType} onChange={setOutputType} />
              <p className="text-xs text-muted-foreground">
                ⚠️ Un seul choix possible par génération
              </p>
            </div>

            {error && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
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
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
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
