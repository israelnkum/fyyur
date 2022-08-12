from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Venue_Genre(db.Model):
    __table_name__ = 'venue_genres'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id", ondelete="CASCADE"), nullable=False)
    genre = db.Column(db.String(30), nullable=False)


class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String, nullable=True)
    seeking_description = db.Column(db.String(255))
    seeking_talent = db.Column(db.Boolean, default=False, server_default="false")
    genres = db.relationship("Venue_Genre", backref="venue", passive_deletes=True, lazy=True)
    shows = db.relationship("Show", backref="venue", passive_deletes=True, lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


class Artist_Genre(db.Model):
    __table_name__ = 'artist_genres'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id", ondelete="CASCADE"), nullable=False)
    genre = db.Column(db.String(30), nullable=False)


class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String, nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(500))
    genres = db.relationship("Artist_Genre", backref="artist", passive_deletes=True, lazy=True)
    shows = db.relationship("Show", backref="artist", passive_deletes=True, lazy=True)


class Show(db.Model):
    __tablename__ = "shows"
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id", ondelete="CASCADE"), primary_key=True)
    start_date_time = db.Column(db.DateTime, nullable=False)
