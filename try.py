from src.methods.OAM_profile.rank import MemberRank
if __name__ == "__main__":
    a = MemberRank("510386488639488001")
    b = a.rank_target("total_onlineTime",3)
    for i in b.values:
        print(F"{i}")