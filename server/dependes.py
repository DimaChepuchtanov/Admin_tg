from base.post import DataBasePost
from base.user import DataBaseUser
from server.user import MiddleLoyeUser
from server.post import MiddleLoyePost

user_ = MiddleLoyeUser(DataBaseUser())
post_ = MiddleLoyePost(DataBasePost())