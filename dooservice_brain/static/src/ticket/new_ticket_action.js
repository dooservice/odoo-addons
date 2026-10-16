import { registry } from "@web/core/registry";

import { TicketOpener } from "./ticket_opener";

/** «New ticket» from a list or a form: the same dialog as the bulb, without leaving the screen. */
registry.category("actions").add("dooservice_brain.new_ticket", (env) => new TicketOpener(env).ask());
