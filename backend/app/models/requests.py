"""
API Request Models.

Pydantic models pour les requêtes HTTP.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class GenerateRequest(BaseModel):
    """
    Requête de génération de contenu.

    Supporte deux modes:
    1. Texte direct via job_offer
    2. Upload de fichier via job_offer_file (base64 encoded .md file)
    """

    job_offer: Optional[str] = Field(
        default=None,
        description="Texte de l'offre d'emploi (minimum 50 caractères)",
        min_length=50,
    )
    job_offer_file: Optional[str] = Field(
        default=None,
        description="Contenu du fichier .md encodé en base64",
    )
    output_type: Literal["email", "linkedin", "letter"] = Field(
        ...,
        description="Type de contenu à générer",
    )

    @field_validator("job_offer", "job_offer_file")
    @classmethod
    def validate_job_offer_input(cls, v, info):
        """Valide qu'au moins un des deux champs est fourni."""
        # Cette validation se fait au niveau du modèle complet
        return v

    def model_post_init(self, __context):
        """Valide qu'exactement un des deux champs est fourni."""
        if not self.job_offer and not self.job_offer_file:
            raise ValueError(
                "Au moins un de 'job_offer' ou 'job_offer_file' doit être fourni"
            )
        if self.job_offer and self.job_offer_file:
            raise ValueError(
                "Seulement un de 'job_offer' ou 'job_offer_file' peut être fourni"
            )

    def get_job_offer_text(self) -> str:
        """
        Retourne le texte de l'offre d'emploi.

        Si un fichier est fourni, le décode du base64.
        Sinon retourne le texte direct.
        """
        if self.job_offer_file:
            import base64

            decoded_bytes = base64.b64decode(self.job_offer_file)
            return decoded_bytes.decode("utf-8")
        return self.job_offer or ""
