from core.client import Bangumi
from errors import AccountTeamError
from models.bangumi import MyTeam
from utils.const import TEAM_NAME


def assert_team(client: Bangumi, team_name: str=TEAM_NAME) -> MyTeam:
    for myteam in client.my_teams():
        if myteam.name == team_name:
            return myteam
    raise AccountTeamError('登陆账户 ' + client.username + ' 不属于"' + team_name + '"团队！')


