import { Component, useEffect, useProps } from "@odoo/owl";

import { TicketInfo } from "./ticket_info";

/** The ticket over its chat: kind, process and state, refreshed as messages arrive. */
export class TicketBadge extends Component {
    static template = "dooservice_brain.TicketBadge";

    setup() {
        this.props = useProps();
        this.info = TicketInfo.of(this.env.services.orm);
        this.state = this.info.state;
        useEffect(() => {
            const { model, id, messages } = this.props.thread;
            if (model === "discuss.channel") {
                this.info.refresh(id, messages?.length ?? 0);
            }
        });
    }

    get header() {
        return this.props.thread.model === "discuss.channel" ? this.state[this.props.thread.id] || null : null;
    }

    get tone() {
        const tones = {
            open: "text-bg-info",
            running: "text-bg-primary",
            waiting_consultant: "text-bg-warning",
            waiting_user: "text-bg-warning",
            resolved: "text-bg-success",
            closed: "text-bg-secondary",
        };
        return tones[this.header?.state] || "text-bg-light";
    }
}
