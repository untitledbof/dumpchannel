from typing import cast
import discord

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from model.message import Embed, EmbedField, Guild, User, Channel, Message, Attachment
from model.base import Base
from config_secret import TOKEN

engine = create_engine('sqlite:///palera1n12.db')

guild_to_log = 1028398973452570725
channel_to_log = 1028398976640229380

Session = sessionmaker(bind=engine)
session = Session()

with engine.connect() as connection:
    # Set the page size to 8192
    connection.execute(text("PRAGMA page_size = 8192;"))

    # Enable Write-Ahead Logging (WAL)
    connection.execute(text("PRAGMA journal_mode = WAL;"))

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        self.guild = self.get_guild(guild_to_log)
        self.channel = self.guild.get_channel(channel_to_log)
        print(self.guild)
        print(self.channel)

        guild = Guild(
            id=self.guild.id,
            name=self.guild.name,
        )

        exists = session.query(Guild).filter_by(id=self.guild.id).first()
        if not exists:
            session.add(guild)

        channel = Channel(
            id=self.channel.id,
            name=self.channel.name,
            guild=self.guild.id,
        )

        exists = session.query(Channel).filter_by(id=self.channel.id).first()

        if not exists:
            session.add(channel)

        cnt = 0

        async for message in self.channel.history(limit=None):
            if cnt % 1000 == 0:
                print(cnt)
                session.commit()

            exists = session.query(Message).filter_by(id=message.id).first()
            
            cnt += 1
            
            if exists:
                continue

            # if message.webhook_id is not None:
            exists = session.query(User).filter_by(id=message.author.id).first()


            if not exists:
                user = User(
                    id=message.author.id,
                    name=message.author.name,
                    discriminator=message.author.discriminator,
                    bot=message.author.bot,
                    display_name=message.author.display_name,
                )
                session.add(user)
            message2 = Message(
                id=message.id,
                content=message.content,
                author=message.author.id,
                channel=message.channel.id,
                timestamp=message.created_at,
                guild=message.guild.id,
                reference=cast(discord.MessageReference, message.reference).message_id if message.reference else None,
                edited_timestamp=message.edited_at,
                # attachment=[attach.id for attach in message.attachments],
            )

            for attach in message.attachments:
                attachment = Attachment(
                    id=attach.id,
                    url=attach.url,
                    message=message.id,
                )
                exists = session.query(Attachment).filter_by(id=attach.id).first()
                if not exists:
                    session.add(attachment)
                    message2.attachments.append(attachment)

            for embed in message.embeds:
                embed2 = Embed(
                    title=embed.title,
                    type=embed.type,
                    description=embed.description,
                    color=embed.color.value if embed.color else None,
                    url=embed.url,
                    timestamp=embed.timestamp,
                    footer_text=embed.footer.text,
                    footer_icon_url=embed.footer.icon_url,
                    message=message.id,
                    image=embed.image.url if embed.image else None,
                    thumbnail=embed.thumbnail.url if embed.thumbnail else None,
                    video=embed.video.url if embed.video else None,
                    provider=embed.provider.name if embed.provider else None,
                )
                for field in embed.fields:
                    field2 = EmbedField(
                        name=field.name,
                        value=field.value,
                        inline=field.inline,
                    )
                    embed2.fields.append(field2)
                session.add(embed2)
                message2.embeds.append(embed2)
            

            session.add(message2)

        session.commit()

        print('Done')
        await self.close()


Base.metadata.create_all(engine)

client = MyClient()

client.run(TOKEN)
