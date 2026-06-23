# uma ferramenta para ver quantos dias seguidos a pessoa logou
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def check_consecutive_days(user):
    today = datetime.now().date()

    # primeiro login
    if user["last_login_date"] is None:
        user["current_streak"] = 1
        user["last_login_date"] = today
        logger.info("Bem vindo! Parabéns pelo primeiro acesso! Dias consecutivos: 1")
        return

    difference = today - user["last_login_date"]

    # login no mesmo dia
    if difference.days == 0:
        logger.info("Dias consecutivos: %s", user["current_streak"])

    # próximos dias
    elif difference.days == 1:
        user["current_streak"] += 1
        user["last_login_date"] = today
        logger.info("Continue assim! Dias consecutivos: %s", user["current_streak"])
    else:
        user["current_streak"] = 1
        user["last_login_date"] = today
        logger.info("Sentimos sua falta...dias consecutivos: 1")

