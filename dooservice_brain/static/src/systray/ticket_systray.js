/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

import { TicketOpener } from "../ticket/ticket_opener";

/** The bulb: from any screen, a new ticket to Dooservice with that screen attached. */
export class TicketSystray extends Component {
    setup() {
        this.user = useService("user");
        this.state = useState({ allowed: false });
        onWillStart(async () => {
            this.state.allowed = await this.user.hasGroup("dooservice_brain.group_ask");
        });
    }

    open() {
        new TicketOpener(this.env).ask();
    }
}
TicketSystray.template = "dooservice_brain.TicketSystray";

registry.category("systray").add("dooservice_brain.ticket", { Component: TicketSystray }, { sequence: 30 });
