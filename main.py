import setting as s

import discord
from discord.ui import *
from discord.commands import Option
from discord.ext import commands

import os
import json
import enum
import datetime

bot = commands.Bot(command_prefix="[", intents=discord.Intents.all())


def is_dev():
    def check_developer(inter:discord.Interaction | discord.ApplicationContext):
        return int(inter.author.id) in s.admins
    return commands.check(check_developer)


class TimeFormat(enum.Enum):
    DEFAULT = "%Y/%m/%d (%a) %H:%M:%S" #2023/01/01 (Sun) 01:00:00
    ONE     = "%Y/%m/%d (%a) %H:%M"    #2023/01/01 (Sun) 01:00
    TWO     = "%Y/%m/%d %H:%M:%S"      #2023/01/01 01:00:00
    THREE   = "%Y/%m/%d %H:%M"         #2023/01/01 01:00

    FOUR    = "%m/%d (%a) %H:%M:%S"    #01/01 (Sun) 01:00:00
    FIVE    = "%m/%d (%a) %H:%M"       #01/01 (Sun) 01:00 
    SIX     = "%m/%d %H:%M"            #01/01 01:00
    SEVEN   = "%m/%d %H:%M"            #01/01 01:00

    EIGHT   = "%H:%M:%S"               #01:00:00
    NINE    = "%H:%M"                  #01:00

    def __str__(self):
        return str(self.value)



class DiscordColors(enum.Enum):
    NOCOLOR= 0x2f3136

    def __str__(self):
        return int(self.value)


class Funshi:

    class Keywords:
        main_file_path   = "./FUNSHI/funshi.json"
        backup_path      = "./FUNSHI/backup.txt"
        edit_log_path    = "./FUNSHI/edit.log"
        role_1           = 1004316617385181244
        role_2           = 1004316596250087484


    class FSelect(discord.ui.Select):
        def __init__(self, placeholder:str, options: list[discord.SelectOption] = ... ) -> None:
            super().__init__(placeholder=placeholder, options=options)

        async def callback(self, interaction: discord.Interaction):
            with open(FW.main_file_path, mode="r", encoding="utf-8") as f:
                data = Funshi.loading()
                e = Funshi.details_base(data[self.values[0]])
            await interaction.response.send_message(embed=e)


    class FRemoveSelect(discord.ui.Select):
        def __init__(self, placeholder:str, options: list[discord.SelectOption] = ... ) -> None:
            super().__init__(placeholder=placeholder, options=options)

        async def callback(self, interaction: discord.Interaction):
            with open(FW.main_file_path, mode="r", encoding="utf-8") as f:
                data = Funshi.loading()
                true_data = data[self.values[0]]
                del data[self.values[0]]
                with open(FW.main_file_path, "r+") as f:
                    f.seek(0)
                    f.write(json.dumps(data, ensure_ascii=False, indent=4))
                    f.truncate()
                Funshi.my_log(fname=FW.edit_log_path, text=f"{interaction.user} - removed  {true_data['id']} = {true_data}", mode="a")
                e = Funshi.details_base(true_data)
                e.title="Successfully Removed!"
                await interaction.response.send_message(embed=e)


    class FView(discord.ui.View):
        def __init__(self, options: list[discord.SelectOption], timeout:int | None = 60, placeholder:str | None = None, mode:str="select"):
            super().__init__(timeout=timeout, disable_on_timeout=True)
            if mode == "select":
                self.add_item(Funshi.FSelect(placeholder=placeholder, options=options))
            elif mode == "remove-select":
                self.add_item(Funshi.FRemoveSelect(placeholder=placeholder, options=options))



    def check_in_list(__user:discord.Member, flag:bool=True):

        __result:bool = True
        __text:str = None
        __check_material = Funshi.loading()

        if (flag):
            if (str(__user.id) in __check_material):
                __result = False
                __text   = "This user is Already registerd! Please use this `/funshi-edit` if you wanna edit" 

            if (__user.bot):
                __result = False
                __text:str = "This user is a Bot! Can't register then"

            return __result, __text
        else:
            if (str(__user.id) not in __check_material):
                __result = False
                __text   = "No existing in member list" 

            return __result, __text 


    def backup():
        if (os.path.exists(FW.main_file_path) and os.path.exists(FW.edit_log_path)):
            flag:bool = False
            with open(FW.main_file_path, mode="r", encoding="utf-8") as f:
                data = json.dumps(json.load(f), indent=4, ensure_ascii=False)

                with open(FW.main_file_path, mode="w", encoding="utf-8") as backup:
                    backup.write(data)
                    flag = True
            return (FW.main_file_path, FW.edit_log_path, flag)
        else:
            raise FileExistsError(f"Not existing {FW.main_file_path} or {FW.edit_log_path} or Both")
                
                
    def loading(mode="r"):
        with open(file=FW.main_file_path, mode=mode) as f:
            return  json.load(f)


    def my_log(fname:str, text:str, mode:str="r+", level="INFO"):
        with open(fname, mode, encoding="utf-8") as f:
            f.write(f"{level} {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ")
            f.write(text)
            f.write("\n")


    def show_list(mode="json"):
        with open(FW.main_file_path, "r") as f:
            e = discord.Embed(title="憤死者名簿", description="```", color=discord.Color.red())
            if mode == "json":
                e.title="Formated!"
                e.description += f"json\n" + json.dumps(json.load(f), indent=2, ensure_ascii=False) + "```"
            else:
                object:dict = Funshi.loading()
                e.description += "ansi\n"

                for idx, obj in enumerate(object.values()):
                    e.description += f"\u001b[1;0m[\u001b[1;31m{idx + 1}\u001b[0m] \u001b[31m{obj['name']}\u001b[0m\u001b[31m#\u001b[31m{obj['discriminator']} \u001b[0m-\u001b[31m {obj['id']}\u001b[0m\n"
                e.description += "```"
                e.description = "```There is no Member.```" if e.description == "```ansi\n```" else e.description
            
            return e

    def show_details(user:dict):
        return Funshi.details_base(user)

    def list_base(user:discord.Member, about:str = None):
        return {
            "name":user.name,
            "discriminator":user.discriminator,
            "id":user.id,
            "about":about,
            "date":datetime.datetime.now().strftime(str(TimeFormat.DEFAULT))
        }

    def details_base(data:dict) -> discord.Embed:
        e = discord.Embed(color=int(DiscordColors.NOCOLOR.value)).set_footer(text=f"Date: {data['date']}")
        e.add_field(name="Name", value=f"```{data['name']}#{data['discriminator']}```").add_field(name="ID", value=f"```{data['id']}```")
        e.add_field(name="About", value = f"```{data['about']}```", inline=False)
        return e



FW = Funshi.Keywords




@bot.slash_command(name="funshi-backup", description="funshi.jsonのバックアップtxtファイルとEdit_log.txtファイルを送信")
@commands.check_any(commands.has_any_role(FW.role_1, FW.role_2), is_dev())
async def funshi_backup_send(inter:discord.Interaction):
    backup_path, edit_path, flag = Funshi.backup()
    if (flag):
        await inter.response.send_message(file=discord.File(backup_path))
        await inter.followup.send(file=discord.File(edit_path))
    else:
        await inter.response.send_message(flag)


@bot.slash_command(name="funshi-format", description="Bot製作者専用、サニティーチェック用")
@commands.check_any(commands.has_any_role(FW.role_1, FW.role_2), is_dev())
async def funshi_format(inter:discord.Interaction):
    a, b, flag = Funshi.backup()
    if (flag):
        with open(FW.main_file_path, "w", encoding="utf-8") as f:
            json.dump({}, f)
            Funshi.my_log(fname=FW.edit_log_path, text=f"{inter.user} - Formated funshi.json", mode="a")
    await inter.response.send_message(embed=Funshi.show_list())


@bot.slash_command(name="funshi-list", description="憤死者名簿を表示。 jsonはjsonファイルをそのまま、simple listは名簿から名前とタグのセットで表示")
async def funshi_list(inter:discord.Interaction, mode:Option(str, "display mode", choices = ["json", "simple list"])="simple list"):
    embed = Funshi.show_list(mode=mode)
    await inter.response.send_message(embed=embed)


@bot.slash_command(name="funshi-search", description="憤死者の詳細")
async def search_funshi_list(interaction:discord.Interaction):
    data:list[discord.SelectOption] = []
    funshi_data:dict = Funshi.loading()
    for idx, user in enumerate(funshi_data.values()):
        data.append(discord.SelectOption(
            label       = f"{idx + 1}: {user['name']}#{user['discriminator']}",
            value       = f"{user['id']}",
            description = f"{user['about']}")
    )
    await interaction.response.send_message(view=Funshi.FView(placeholder="ユーザーを指定してください。Timeout=60s", options=data))



@bot.slash_command(name="funshi-register", description="憤死者名簿に指定したユーザーを登録")
@commands.check_any(commands.has_any_role(FW.role_1, FW.role_2), is_dev())
async def funshi_register_on_slash(inter:discord.Interaction,
    user :Option(discord.Member, "憤死名簿に登録するメンバー"),
    about:Option(str, "人物像・憤死内容")
):
    flag, err = Funshi.check_in_list(user)
    if (flag):
        with open(FW.main_file_path, "r+") as f:
            data = Funshi.loading()
            data[user.id] = Funshi.list_base(user=user, about=about)
            f.seek(0)
            f.write(json.dumps(data, ensure_ascii=False, indent=4), )
            f.truncate()
        Funshi.my_log(fname=FW.edit_log_path, text=f"{inter.user} - registerd  {user.id} = {data[user.id]}", mode="a")
        e = Funshi.show_details(data[user.id])
        e.title="Successfully Registed!"
        await inter.response.send_message(embed=e)
    else:
        await inter.response.send_message(embed=discord.Embed(title="you cannot use this command.", description=err, color=discord.Color.red()), ephemeral=True)


@bot.user_command(name="funshi register", description="憤死者名簿に指定したユーザーを登録")
@commands.check_any(commands.has_any_role(FW.role_1, FW.role_2), is_dev())
async def funshi_register_on_user_cmd(inter:discord.Interaction, user=discord.Member):
    flag, err = Funshi.check_in_list(user)
    if (flag):
        with open(FW.main_file_path, "r+") as f:
            data = Funshi.loading()
            data[user.id] = Funshi.list_base(user=user, about = f"This user was added by {inter.user} with user cmd.")
            f.seek(0)
            f.write(json.dumps(data, ensure_ascii=False, indent=4))
            f.truncate()
        Funshi.my_log(fname=FW.edit_log_path, text=f"{inter.user} - registerd  {user.id} = {data[user.id]}", mode="a")
        e = Funshi.show_details(data[user.id])
        e.title="Successfully Registed!"
        await inter.response.send_message(embed=e)
    else:
        await inter.response.send_message(embed=discord.Embed(title="you cannot use this command.", description=err, color=discord.Color.red()), ephemeral=True) 


@bot.slash_command(name="funshi-remove")
@commands.check_any(commands.has_any_role(FW.role_1, FW.role_2), is_dev())
async def funshi_remove_re(inter:discord.Interaction):
    data:list[discord.SelectOption] = []
    funshi_data:dict = Funshi.loading()
    for idx, user in enumerate(funshi_data.values()):
        data.append(discord.SelectOption(
            label       = f"{idx + 1}: {user['name']}#{user['discriminator']}",
            value       = f"{user['id']}",
            description = f"{user['about']}")
    )
    try:
        await inter.response.send_message(view=Funshi.FView(placeholder="ユーザーを指定してください。Timeout=60s", options=data, mode="remove-select"))
    except:
        await inter.response.send_message(embed=discord.Embed(title="ApplicationCommandInvokeError", description="No member in list Maybe or something", color=0xFF0000), ephemeral=True)



if __name__ == "__main__":
    bot.run(s.token)
