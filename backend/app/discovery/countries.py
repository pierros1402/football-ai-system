from sqlalchemy.orm import Session
from app.models import Country
from app.discovery.client import fetch_json

async def discover_countries(db: Session):
    data = await fetch_json("sport/football/countries")

    countries = data.get("countries", [])

    inserted = 0
    updated = 0

    for c in countries:
        existing = db.query(Country).filter_by(id=c["id"]).first()

        if existing:
            existing.name = c["name"]
            existing.slug = c["slug"]
            updated += 1
        else:
            new_country = Country(
                id=c["id"],
                name=c["name"],
                slug=c["slug"]
            )
            db.add(new_country)
            inserted += 1

    db.commit()

    return {
        "inserted": inserted,
        "updated": updated,
        "total": len(countries)
    }
