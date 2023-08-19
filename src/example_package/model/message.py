# write a model for a message object

import sqlalchemy

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped

from typing import List

from .base import Base

# association_table = sqlalchemy.Table(
#     'association',
#     Base.metadata,
#     Column('message_id', Integer, ForeignKey('messages.id')),
#     # attachment
#     Column('attachment_id', Integer, ForeignKey('attachments.id')),
#     # embed
#     Column('embed_id', Integer, ForeignKey('embeds.id')),
#     # embed_field
#     Column('embed_field_id', Integer, ForeignKey('embed_fields.id')),
# )

message_attachment_association = sqlalchemy.Table('message_attachment_association', Base.metadata,
    Column('message_id', Integer, ForeignKey('messages.id')),
    Column('attachment_id', Integer, ForeignKey('attachments.id')),
    Column('additional_info', String)  # Additional information in the association
)

message_embed_association = sqlalchemy.Table('message_embed_association', Base.metadata,
    Column('message_id', Integer, ForeignKey('messages.id')),
    Column('embed_id', Integer, ForeignKey('embeds.id')),
    Column('additional_info', String)  # Additional information in the association
)

embed_field_association = sqlalchemy.Table('embed_field_association', Base.metadata,
    Column('embed_id', Integer, ForeignKey('embeds.id')),
    Column('embed_field_id', Integer, ForeignKey('embed_fields.id')),
    Column('additional_info', String)  # Additional information in the association
)

class Guild(Base):
    __tablename__ = 'guilds'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return f"<Guild(id={self.id}, name={self.name})>"

    def __str__(self):
        return f"{self.name}"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }
    
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    discriminator = Column(String)
    bot = Column(Boolean)
    display_name = Column(String)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, discriminator={self.discriminator}, avatar={self.avatar}, bot={self.bot})>"

    def __str__(self):
        if self.discriminator != '0':
            return f"{self.name}#{self.discriminator}"
        else:
            return f"{self.name}"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'discriminator': self.discriminator,
        }
    
class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    guild = Column(Integer, ForeignKey('guilds.id'))

    def __repr__(self):
        return f"<Channel(id={self.id}, name={self.name}, type={self.type}, guild={self.guild})>"

    def __str__(self):
        return f"{self.name}"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'guild': self.guild
        }

class Attachment(Base):
    __tablename__ = 'attachments'
    id = mapped_column(Integer, primary_key=True)
    url = Column(String)
    message = Column(Integer, ForeignKey('messages.id'))

    def __repr__(self):
        return f"<Attachment(id={self.id}, url={self.url})>"

    def __str__(self):
        return f"{self.url}"

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
        }
    
class EmbedField(Base):
    __tablename__ = 'embed_fields'
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    value = Column(String)
    inline = Column(Boolean)

    embed = Column(Integer, ForeignKey('embeds.id'))
    
class Embed(Base):
    __tablename__ = 'embeds'
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    type = Column(String)
    description = Column(String)
    url = Column(String)
    timestamp = Column(DateTime)
    color = Column(Integer)
    footer_text = Column(String)
    footer_icon_url = Column(String)
    image = Column(String)
    thumbnail = Column(String)
    video = Column(String)
    provider = Column(String)

    # FIX HERE
    # many-to-one relationship
    fields: Mapped[List["EmbedField"]] = relationship('EmbedField', secondary=embed_field_association, backref='embeds', cascade='all')
    # END OFFIX HERE

    message = Column(Integer, ForeignKey('messages.id'))

class Message(Base):
    __tablename__ = 'messages'
    id = mapped_column(Integer, primary_key=True)
    author = Column(Integer, ForeignKey('users.id'))
    content = Column(String)
    channel = Column(Integer, ForeignKey('channels.id'))
    timestamp = Column(DateTime)
    edited_timestamp = Column(DateTime)
    guild = Column(Integer, ForeignKey('guilds.id'))


    # backreference
    # one-to-many relationship
    reference = Column(Integer, ForeignKey('messages.id'))

    # FIX HERE
    # many-to-many relationship
    embeds: Mapped[List["Embed"]] = relationship('Embed', secondary=message_embed_association, backref='messages', cascade='all')
    attachments: Mapped[List["Attachment"]] = relationship('Attachment', secondary=message_attachment_association, backref='messages', cascade='all')
    # END OF FIX HERE

    def __repr__(self):
        return f"<Message(id={self.id}, author={self.author}, content={self.content}, channel={self.channel}, timestamp={self.timestamp}, guild={self.guild})>"

    def __str__(self):
        return f"{self.author}: {self.content}"

    def to_dict(self):
        return {
            'id': self.id,
            'author': self.author,
            'content': self.content,
            'channel': self.channel,
            'timestamp': self.timestamp,
            'guild': self.guild
        }

