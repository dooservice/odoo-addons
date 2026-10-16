"""Odoo 16: a piece's link in a message, pressed; the chat says what it did, or why it could not."""

from odoo import http
from odoo.exceptions import AccessError, UserError
from odoo.http import request
from odoo.tools import consteq

from ..services.bot_posting import BotPosting
from ..services.card_actions import CardActions
from ..services.cards_html import CardsHtml

DISCUSS = "/web#action=mail.action_discuss&active_id=mail.channel_{}"


class CardController(http.Controller):
    @http.route("/dooservice_brain/card/<int:message_id>/<string:card_id>/<string:action>", type="http", auth="user")
    def card_action(self, message_id, card_id, action, value="", label="", token=""):
        message = request.env["mail.message"].sudo().browse(message_id).exists()
        expected = CardsHtml.token(request.env, message_id, card_id, action, value, label)
        if not message or not consteq(expected, token):
            return request.redirect("/web")
        try:
            CardActions(request.env).act(message_id, card_id, action, value or None, label)
        except (AccessError, UserError) as error:
            request.env.cr.rollback()
            channel = request.env[message.model].sudo().browse(message.res_id)
            BotPosting(request.env).post(channel, str(error))
        return request.redirect(DISCUSS.format(message.res_id))
