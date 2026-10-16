/** @odoo-module **/

import { registry } from "@web/core/registry";

import { TicketOpener } from "./ticket_opener";

/**
 * «New ticket» from a list or a form: the same dialog as the bulb, without leaving the screen.
 *
 * In Odoo 16 the link under a closed ticket reaches here too, by URL, naming the ticket to
 * continue; Discuss is opened first so the new chat has somewhere to appear.
 */
registry.category("actions").add("dooservice_brain.new_ticket", async (env, action) => {
    const params = action.params || {};
    if (!params.continues) {
        new TicketOpener(env).ask();
        return;
    }
    await env.services.action.doAction("mail.action_discuss");
    new TicketOpener(env).ask({
        continues: Number(params.continues),
        continuesNumber: params.continues_number || "",
    });
});
