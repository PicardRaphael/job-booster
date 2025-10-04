import { useMutation } from "@tanstack/react-query";
import { generateContent } from "@/lib/api";
import type { GenerateRequest, GenerateResponse } from "@/types/api";
import { useToast } from "@/hooks/use-toast";

export function useGenerate() {
  const { toast } = useToast();

  return useMutation<GenerateResponse, Error, GenerateRequest>({
    mutationFn: generateContent,
    onSuccess: () => {
      toast({
        title: "Génération réussie",
        description: "Votre contenu a été généré avec succès.",
      });
    },
    onError: (error) => {
      toast({
        title: "Erreur",
        description: error.message || "Une erreur est survenue lors de la génération.",
        variant: "destructive",
      });
    },
  });
}
