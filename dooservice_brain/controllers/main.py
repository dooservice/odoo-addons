from odoo import http
from odoo.exceptions import AccessError, UserError
from odoo.http import request
from odoo.tools import consteq

from ..constants import GROUP_REQUEST
from ..services.card_actions import CardActions
from ..services.cards_html import CardsHtml


class AssistantController(http.Controller):
    @http.route("/dooservice_brain/request/<int:question_id>", type="http", auth="user")
    def request_from_question(self, question_id):
        """From «Request it» under an earlier answer: the request read back, opened for the person to send."""
        if not request.env.user.has_group(GROUP_REQUEST):
            return request.redirect("/web")
        question = request.env["dooservice.brain.question"].browse(question_id).exists()
        if not question or question.user_id != request.env.user:
            return request.redirect("/web")
        created = request.env["dooservice.brain.request"]._from_question(question)
        return request.redirect(f"/web#model=dooservice.brain.request&id={created.id}&view_type=form")

    @http.route("/dooservice_brain/card/<int:message_id>/<string:card_id>/<string:action>", type="http", auth="user")
    def card_action(self, message_id, card_id, action, value="", token=""):
        """A link in an answer, in Odoo 16: done once, for the person whose chat it is."""
        expected = CardsHtml.token(request.env, request.env.uid, message_id, card_id, action, value)
        if consteq(expected, token):
            try:
                CardActions(request.env).act(message_id, card_id, action, value or None)
            except (AccessError, UserError):
                request.env.cr.rollback()
        message = request.env["mail.message"].sudo().browse(message_id)
        return request.redirect(f"/web#action=mail.action_discuss&active_id=mail.channel_{message.res_id}")
