"""Seed script: real geographic data of Madagascar (6 provinces, 22 regions, sample communes)."""

import asyncio

from sqlalchemy import select

from app.core.database import async_session
from app.models.geography import Commune, Province, Region

# Madagascar: 6 provinces, 22 régions, communes représentatives
GEOGRAPHY_DATA = {
    "Antananarivo": {
        "code": "PRV-TANA",
        "regions": {
            "Analamanga": {
                "code": "REG-ALAM",
                "communes": [
                    ("Antananarivo-Renivohitra", "COM-TANA-1"),
                    ("Ambohidratrimo", "COM-AMBHDR"),
                    ("Ankazobe", "COM-ANKZB"),
                    ("Anjozorobe", "COM-ANJZR"),
                    ("Manjakandriana", "COM-MANJK"),
                ],
            },
            "Vakinankaratra": {
                "code": "REG-VKNK",
                "communes": [
                    ("Antsirabe I", "COM-ANTS1"),
                    ("Antsirabe II", "COM-ANTS2"),
                    ("Ambatolampy", "COM-AMBTL"),
                    ("Betafo", "COM-BETFO"),
                    ("Faratsiho", "COM-FARTS"),
                ],
            },
            "Itasy": {
                "code": "REG-ITAS",
                "communes": [
                    ("Miarinarivo", "COM-MIARN"),
                    ("Arivonimamo", "COM-ARVNM"),
                    ("Soavinandriana", "COM-SOAVN"),
                ],
            },
            "Bongolava": {
                "code": "REG-BNGL",
                "communes": [
                    ("Tsiroanomandidy", "COM-TSRNM"),
                    ("Fenoarivobe", "COM-FENRV"),
                ],
            },
        },
    },
    "Antsiranana": {
        "code": "PRV-ANTS",
        "regions": {
            "Diana": {
                "code": "REG-DIANA",
                "communes": [
                    ("Antsiranana I", "COM-ANTS-I"),
                    ("Antsiranana II", "COM-ANTS-II"),
                    ("Ambanja", "COM-AMBJA"),
                    ("Nosy Be", "COM-NSYBE"),
                    ("Ambilobe", "COM-AMBLB"),
                ],
            },
            "Sava": {
                "code": "REG-SAVA",
                "communes": [
                    ("Sambava", "COM-SAMBV"),
                    ("Antalaha", "COM-ANTLH"),
                    ("Vohémar", "COM-VOHM"),
                    ("Andapa", "COM-ANDAP"),
                ],
            },
        },
    },
    "Fianarantsoa": {
        "code": "PRV-FIAN",
        "regions": {
            "Haute Matsiatra": {
                "code": "REG-HMTS",
                "communes": [
                    ("Fianarantsoa I", "COM-FIAN1"),
                    ("Fianarantsoa II", "COM-FIAN2"),
                    ("Ambalavao", "COM-AMBLV"),
                    ("Ambohimahasoa", "COM-AMBHS"),
                ],
            },
            "Amoron'i Mania": {
                "code": "REG-AMRM",
                "communes": [
                    ("Ambositra", "COM-AMBST"),
                    ("Fandriana", "COM-FANDR"),
                    ("Manandriana", "COM-MANDR"),
                ],
            },
            "Vatovavy": {
                "code": "REG-VTVV",
                "communes": [
                    ("Mananjary", "COM-MANNJ"),
                    ("Ifanadiana", "COM-IFAND"),
                    ("Nosy Varika", "COM-NSYVR"),
                ],
            },
            "Fitovinany": {
                "code": "REG-FTVN",
                "communes": [
                    ("Manakara", "COM-MANKR"),
                    ("Vohipeno", "COM-VOHPN"),
                    ("Ikongo", "COM-IKNGO"),
                ],
            },
            "Atsimo-Atsinanana": {
                "code": "REG-ATAT",
                "communes": [
                    ("Farafangana", "COM-FARFG"),
                    ("Vangaindrano", "COM-VNGDR"),
                    ("Midongy du Sud", "COM-MIDNG"),
                ],
            },
            "Ihorombe": {
                "code": "REG-IHRB",
                "communes": [
                    ("Ihosy", "COM-IHOSY"),
                    ("Ivohibe", "COM-IVHBE"),
                    ("Iakora", "COM-IAKRA"),
                ],
            },
        },
    },
    "Mahajanga": {
        "code": "PRV-MHJG",
        "regions": {
            "Boeny": {
                "code": "REG-BOEN",
                "communes": [
                    ("Mahajanga I", "COM-MHJG1"),
                    ("Mahajanga II", "COM-MHJG2"),
                    ("Marovoay", "COM-MRVOY"),
                    ("Mitsinjo", "COM-MITSJ"),
                    ("Soalala", "COM-SOALL"),
                ],
            },
            "Betsiboka": {
                "code": "REG-BTSBK",
                "communes": [
                    ("Maevatanana", "COM-MAEVT"),
                    ("Tsaratanana", "COM-TSRTN"),
                    ("Kandreho", "COM-KNDRH"),
                ],
            },
            "Melaky": {
                "code": "REG-MELK",
                "communes": [
                    ("Maintirano", "COM-MAINTR"),
                    ("Morafenobe", "COM-MRFNB"),
                    ("Antsalova", "COM-ANTSLV"),
                    ("Besalampy", "COM-BSLMP"),
                ],
            },
            "Sofia": {
                "code": "REG-SOFI",
                "communes": [
                    ("Antsohihy", "COM-ANTSH"),
                    ("Befandriana-Nord", "COM-BFNDR"),
                    ("Mandritsara", "COM-MNDRT"),
                    ("Port-Bergé", "COM-PRTBG"),
                ],
            },
        },
    },
    "Toamasina": {
        "code": "PRV-TMSI",
        "regions": {
            "Atsinanana": {
                "code": "REG-ATSN",
                "communes": [
                    ("Toamasina I", "COM-TMSI1"),
                    ("Toamasina II", "COM-TMSI2"),
                    ("Brickaville", "COM-BRCKV"),
                    ("Vatomandry", "COM-VTMDR"),
                    ("Mahanoro", "COM-MAHNR"),
                ],
            },
            "Analanjirofo": {
                "code": "REG-ANLJ",
                "communes": [
                    ("Fénérive Est", "COM-FENRV-E"),
                    ("Mananara Nord", "COM-MNNR"),
                    ("Maroantsetra", "COM-MRNTS"),
                    ("Sainte-Marie", "COM-STMAR"),
                ],
            },
            "Alaotra-Mangoro": {
                "code": "REG-ALMG",
                "communes": [
                    ("Ambatondrazaka", "COM-AMBTZ"),
                    ("Moramanga", "COM-MRMNG"),
                    ("Andilamena", "COM-ANDLM"),
                    ("Amparafaravola", "COM-AMPFR"),
                ],
            },
        },
    },
    "Toliara": {
        "code": "PRV-TLRA",
        "regions": {
            "Atsimo-Andrefana": {
                "code": "REG-ATAN",
                "communes": [
                    ("Toliara I", "COM-TLRA1"),
                    ("Toliara II", "COM-TLRA2"),
                    ("Morombe", "COM-MRMBE"),
                    ("Ankazoabo", "COM-ANKZB-S"),
                    ("Betioky", "COM-BETKY"),
                ],
            },
            "Androy": {
                "code": "REG-ANDR",
                "communes": [
                    ("Ambovombe", "COM-AMBVB"),
                    ("Bekily", "COM-BEKLY"),
                    ("Tsihombe", "COM-TSHBE"),
                ],
            },
            "Anosy": {
                "code": "REG-ANOS",
                "communes": [
                    ("Taolagnaro", "COM-TAOLG"),
                    ("Amboasary Sud", "COM-AMBSR"),
                    ("Betroka", "COM-BETRK"),
                ],
            },
            "Menabe": {
                "code": "REG-MENB",
                "communes": [
                    ("Morondava", "COM-MRDVA"),
                    ("Belo sur Tsiribihina", "COM-BELO"),
                    ("Mahabo", "COM-MAHBO"),
                    ("Miandrivazo", "COM-MNDVZ"),
                ],
            },
        },
    },
}


async def seed() -> None:
    async with async_session() as db:
        # Check if data already exists
        result = await db.execute(select(Province).limit(1))
        existing = result.scalars().all()
        if len(existing) > 1:
            print(f"Geography data already seeded ({len(existing)}+ provinces). Skipping.")
            return

        # Delete existing data to start fresh
        await db.execute(Commune.__table__.delete())
        await db.execute(Region.__table__.delete())
        await db.execute(Province.__table__.delete())
        await db.flush()

        total_provinces = 0
        total_regions = 0
        total_communes = 0

        for province_name, province_data in GEOGRAPHY_DATA.items():
            province = Province(
                name=province_name,
                code=province_data["code"],
            )
            db.add(province)
            await db.flush()
            total_provinces += 1

            for region_name, region_data in province_data["regions"].items():
                region = Region(
                    name=region_name,
                    code=region_data["code"],
                    province_id=province.id,
                )
                db.add(region)
                await db.flush()
                total_regions += 1

                for commune_name, commune_code in region_data["communes"]:
                    commune = Commune(
                        name=commune_name,
                        code=commune_code,
                        region_id=region.id,
                    )
                    db.add(commune)
                    total_communes += 1

        await db.commit()
        print(f"Seeded: {total_provinces} provinces, {total_regions} regions, {total_communes} communes.")


if __name__ == "__main__":
    asyncio.run(seed())
