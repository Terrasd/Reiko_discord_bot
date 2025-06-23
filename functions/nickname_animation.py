from discord.ext import tasks


class NicknameAnimator:
    def __init__(self, client, guild_id, user_id, animation_type="scroll",
                 base_nickname="Твой Ник", window_size=10, nicknames=None,
                 interval=90):
        """
        Универсальный класс для анимации никнейма.

        :param client: объект бота (discord.Client)
        :param guild_id: ID сервера (где менять ник)
        :param user_id: ID пользователя (чей ник менять)
        :param animation_type: "scroll" (бегущая строка) или "sequence" (список ников)
        :param base_nickname: Базовый ник (если выбрана "scroll")
        :param window_size: Окно для бегущей строки
        :param nicknames: Список ников для последовательной смены (если выбрана "sequence")
        :param interval: Интервал в секундах (по умолчанию 90)
        """
        self.client = client
        self.guild_id = guild_id
        self.user_id = user_id
        self.animation_type = animation_type
        self.base_nickname = base_nickname
        self.window_size = window_size
        self.nicknames = nicknames or ["Ник 1", "Ник 2", "Ник 3"]
        self.interval = interval
        self.index = 0

    def get_next_nickname(self):
        """Выбирает следующий ник в зависимости от типа анимации."""
        if self.animation_type == "scroll":
            text = self.base_nickname + " "
            looped_text = text + text
            return looped_text[self.index:self.index + self.window_size]

        elif self.animation_type == "sequence":
            return self.nicknames[self.index]

        return self.base_nickname

    async def update_nickname(self):
        """Меняет ник пользователя на сервере."""
        guild = self.client.get_guild(self.guild_id)
        if not guild:
            print("Не удалось найти сервер!")
            return

        member = guild.get_member(self.user_id)
        if not member:
            print("Не удалось найти участника!")
            return

        new_nick = self.get_next_nickname()
        self.index = (self.index + 1) % (len(self.base_nickname) if
                                         self.animation_type == "scroll" else
                                         len(self.nicknames))

        try:
            await member.edit(nick=new_nick)
        except Exception as e:
            print(f"Ошибка при смене ника: {e}")

    @tasks.loop(seconds=90)
    async def animate_nickname(self):
        """Запускает анимацию изменения ника."""
        await self.update_nickname()

    def start(self):
        """Запускает цикл анимации."""
        self.animate_nickname.change_interval(seconds=self.interval)
        self.animate_nickname.start()
