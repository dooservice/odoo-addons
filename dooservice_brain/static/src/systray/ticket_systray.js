import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";

import { TicketOpener } from "../ticket/ticket_opener";

/** The bulb: from any screen, a new ticket to Dooservice with that screen attached. */
export class TicketSystray extends Component {
    static template = "dooservice_brain.TicketSystray";
    static props = {};

    setup() {
        this.state = useState({ allowed: false });
        onWillStart(async () => {
            this.state.allowed = await user.hasGroup("dooservice_brain.group_ask");
        });
    }

    open() {
        new TicketOpener(this.env).ask();
    }
}

registry.category("systray").add("dooservice_brain.ticket", { Component: TicketSystray }, { sequence: 30 });
