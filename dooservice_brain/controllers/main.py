from odoo import http
from odoo.http import request

from ..constants import GROUP_REQUEST


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
