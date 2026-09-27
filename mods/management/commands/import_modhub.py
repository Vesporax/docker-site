"""
Commande d'import des dossiers scrapés depuis le ModHub de Farming Simulator.

Structure attendue :
    modhub_data/
        mod_350732/
            mod_350732.json
            350732_1.png
            350732_2.png
            ...
        mod_314008/
            mod_314008.json
            314008_1.png
            ...

Usage :
    python manage.py import_modhub --data-dir /chemin/vers/modhub_data --mapping /chemin/vers/category_mapping.json

Options :
    --data-dir   Dossier contenant les sous-dossiers mod_XXXXX (défaut: ./modhub_data)
    --mapping    Fichier JSON de mapping catégories EN → FR (défaut: ./category_mapping.json)
    --dry-run    Simule l'import sans rien écrire en base
    --limit      Limite le nombre de mods importés (utile pour tester)
"""

import json
import re
import os
import shutil
from pathlib import Path

from django.contrib.auth.models import User
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from mods.models import Mod, Game, Category, ModImage


class Command(BaseCommand):
    help = "Importe les mods scrapés depuis les dossiers ModHub FS"

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-dir',
            type=str,
            default='./modhub_data',
            help='Dossier parent contenant les sous-dossiers mod_XXXXX'
        )
        parser.add_argument(
            '--mapping',
            type=str,
            default='./category_mapping.json',
            help='Fichier JSON de mapping catégories anglais → français'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simule sans écrire en base'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limite le nombre de mods importés'
        )

    def handle(self, *args, **options):
        data_dir = Path(options['data_dir'])
        mapping_file = Path(options['mapping'])
        dry_run = options['dry_run']
        limit = options['limit']

        # ── Vérifications initiales ───────────────────────────────────────────
        if not data_dir.is_dir():
            raise CommandError(f"Dossier introuvable : {data_dir}")

        if not mapping_file.is_file():
            raise CommandError(f"Fichier de mapping introuvable : {mapping_file}")

        # ── Chargement du mapping ─────────────────────────────────────────────
        with open(mapping_file, 'r', encoding='utf-8') as f:
            category_mapping = json.load(f)

        # ── Compte Modhub ─────────────────────────────────────────────────────
        try:
            modhub_user = User.objects.get(username='Modhub')
        except User.DoesNotExist:
            raise CommandError(
                "L'utilisateur 'Modhub' n'existe pas. "
                "Créez-le d'abord via le panel admin."
            )

        # ── Jeu Farming Simulator 25 ──────────────────────────────────────────
        game, _ = Game.objects.get_or_create(
            slug='farming-simulator-25',
            defaults={'name': 'Farming Simulator 25'}
        )

        # ── Récupération des dossiers mod_XXXXX ───────────────────────────────
        mod_dirs = sorted([
            d for d in data_dir.iterdir()
            if d.is_dir() and d.name.startswith('mod_')
        ])

        if not mod_dirs:
            raise CommandError(f"Aucun dossier mod_XXXXX trouvé dans {data_dir}")

        if limit:
            mod_dirs = mod_dirs[:limit]

        self.stdout.write(f"📂 {len(mod_dirs)} dossier(s) trouvé(s)")
        if dry_run:
            self.stdout.write(self.style.WARNING("⚠️  Mode dry-run — aucune écriture en base"))

        # ── Compteurs ─────────────────────────────────────────────────────────
        created = 0
        skipped = 0
        errors = 0
        unmapped = set()

        # ── Import ────────────────────────────────────────────────────────────
        for mod_dir in mod_dirs:
            mod_id = mod_dir.name.replace('mod_', '')

            # Trouver le JSON
            json_files = list(mod_dir.glob('*.json'))
            if not json_files:
                self.stdout.write(self.style.WARNING(f"  ⚠ {mod_dir.name} — pas de JSON, ignoré"))
                errors += 1
                continue

            json_file = json_files[0]

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # ── Nom du mod ────────────────────────────────────────────────
                name = self._extract_name(data.get('download_link', ''), mod_id)

                # ── Slug unique ───────────────────────────────────────────────
                base_slug = slugify(name)
                if not base_slug:
                    base_slug = f"mod-{mod_id}"

                # Vérification doublon
                if Mod.objects.filter(slug=base_slug).exists():
                    self.stdout.write(f"  ↷ {name} — déjà importé, ignoré")
                    skipped += 1
                    continue

                slug = self._unique_slug(base_slug)

                # ── Catégorie ─────────────────────────────────────────────────
                raw_category = data.get('category', '')
                french_category_name = category_mapping.get(raw_category)

                if not french_category_name:
                    unmapped.add(raw_category)
                    french_category_name = 'Divers'

                category = Category.objects.filter(name=french_category_name).first()
                if not category:
                    category = Category.objects.filter(name='Divers').first()

                # ── Données du mod ────────────────────────────────────────────
                description = data.get('description', '').strip()
                version = data.get('version', '1.0.0.0')
                download_link = data.get('download_link', '')

                if not download_link:
                    self.stdout.write(self.style.WARNING(f"  ⚠ {name} — pas de lien de téléchargement, ignoré"))
                    errors += 1
                    continue

                if dry_run:
                    self.stdout.write(f"  [DRY] {name} → {french_category_name} ({slug})")
                    created += 1
                    continue

                # ── Création du mod ───────────────────────────────────────────
                mod = Mod.objects.create(
                    name=name,
                    slug=slug,
                    description=description,
                    game=game,
                    main_author=modhub_user,
                    version=version,
                    download_link=download_link,
                    status='approved',
                )

                if category:
                    mod.categories.add(category)

                # ── Images ────────────────────────────────────────────────────
                image_files = sorted([
                    f for f in mod_dir.iterdir()
                    if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp')
                ])

                for order, img_path in enumerate(image_files[:6]):
                    with open(img_path, 'rb') as img_file:
                        ModImage.objects.create(
                            mod=mod,
                            image=File(img_file, name=img_path.name),
                            order=order
                        )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ {name} — {len(image_files[:6])} image(s) — {french_category_name}"
                    )
                )
                created += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ {mod_dir.name} — erreur : {e}"))
                errors += 1

        # ── Résumé ────────────────────────────────────────────────────────────
        self.stdout.write("\n── Résumé ───────────────────────────────────────")
        self.stdout.write(self.style.SUCCESS(f"  ✓ Créés    : {created}"))
        self.stdout.write(f"  ↷ Ignorés  : {skipped}")
        self.stdout.write(self.style.ERROR(f"  ✗ Erreurs  : {errors}") if errors else f"  ✗ Erreurs  : {errors}")

        if unmapped:
            self.stdout.write(self.style.WARNING("\n  ⚠ Catégories sans mapping (classées dans 'Divers') :"))
            for cat in sorted(unmapped):
                self.stdout.write(f"    - {cat}")
            self.stdout.write("  → Ajoute-les dans category_mapping.json si besoin.")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _extract_name(self, download_link: str, fallback: str) -> str:
        """
        Extrait le nom lisible depuis le lien de téléchargement.
        Ex: .../FS25_CountrysideFields.zip → "Countryside Fields"
        """
        if not download_link:
            return f"Mod {fallback}"

        filename = Path(download_link).stem           # FS25_CountrysideFields
        # Retire le préfixe de jeu (FS25_, FS22_, etc.)
        name = re.sub(r'^FS\d+_', '', filename)       # CountrysideFields
        # Sépare le CamelCase en mots
        name = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', name)   # Countryside Fields
        # Remplace les underscores résiduels
        name = name.replace('_', ' ').strip()
        return name if name else f"Mod {fallback}"

    def _unique_slug(self, base_slug: str) -> str:
        """Génère un slug unique en ajoutant un suffixe numérique si nécessaire."""
        slug = base_slug
        counter = 1
        while Mod.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug