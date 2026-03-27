from app.database import SessionLocal
from app.models import Country, Tournament, Season, Match


def save_country(country_id, name, slug):
    db = SessionLocal()
    try:
        obj = db.query(Country).filter_by(id=country_id).first()
        if not obj:
            obj = Country(id=country_id, name=name, slug=slug)
            db.add(obj)
        else:
            obj.name = name
            obj.slug = slug
        db.commit()
    finally:
        db.close()


def save_tournament(tournament_id, name, slug, country_id):
    db = SessionLocal()
    try:
        obj = db.query(Tournament).filter_by(id=tournament_id).first()
        if not obj:
            obj = Tournament(
                id=tournament_id,
                name=name,
                slug=slug,
                country_id=country_id
            )
            db.add(obj)
        else:
            obj.name = name
            obj.slug = slug
            obj.country_id = country_id
        db.commit()
    finally:
        db.close()


def save_season(season_id, name, tournament_id):
    db = SessionLocal()
    try:
        obj = db.query(Season).filter_by(id=season_id).first()
        if not obj:
            obj = Season(
                id=season_id,
                name=name,
                tournament_id=tournament_id
            )
            db.add(obj)
        else:
            obj.name = name
            obj.tournament_id = tournament_id
        db.commit()
    finally:
        db.close()


def save_match(match_id, tournament_id, season_id, data):
    db = SessionLocal()
    try:
        obj = db.query(Match).filter_by(id=match_id).first()
        if not obj:
            obj = Match(
                id=match_id,
                tournament_id=tournament_id,
                season_id=season_id,
                data=data
            )
            db.add(obj)
        else:
            obj.data = data
        db.commit()
    finally:
        db.close()
