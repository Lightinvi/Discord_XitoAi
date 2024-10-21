from src.core import SQL,db_account,db_server

TABLE = "v_memberProfile"

class MemberRank():
    def __init__(self, guild_id) -> None:
        self.table = SQL(db_account).connect(db_server).v_table(TABLE)
        self.guild_id = str(guild_id)

    def rank_target(self, target:str, index:int):
        result = self.table.select(
                "userId",target
            ).where(
                    self.table.guildId == self.guild_id #pylint:disable = E1101
                ).order_by(
                        F"{target} desc"
                    ).result.data
        result = result[:index]
        return result
