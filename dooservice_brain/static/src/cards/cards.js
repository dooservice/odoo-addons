import { Component, onMounted, onWillUnmount, proxy, useProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { TicketOpener } from "../ticket/ticket_opener";
import { DEFAULT_OPTIONS } from "./card_options";
import { CardsLoader } from "./cards_loader";

/** The pieces under a message of Dooservice: nothing moves a ticket without a button saying so. */
export class DooserviceCards extends Component {
    static template = "dooservice_brain.Cards";

    setup() {
        this.props = useProps();
        this.orm = useService("orm");
        this.state = proxy({ payload: null, busy: "", typed: {}, correcting: {} });
        onMounted(() => this.load());
        onWillUnmount(() => (this.gone = true));
    }

    get messageId() {
        return this.props.message.id;
    }

    async load() {
        const loader = CardsLoader.of(this.env.services.orm);
        const author = this.props.message.author_id || this.props.message.author;
        const bot = await loader.bot();
        if (bot && author?.id === bot && Number.isInteger(this.messageId)) {
            this.show(await loader.cards(this.messageId));
        }
    }

    show(payload) {
        if (!this.gone) {
            this.state.payload = payload;
        }
    }

    done(card) {
        return this.state.payload.state[card.id] || {};
    }

    options(card) {
        return card.options?.length ? card.options : DEFAULT_OPTIONS[card.type] || [];
    }

    actionable(card) {
        if (!(card.type in DEFAULT_OPTIONS) || this.state.payload.closed) {
            return false;
        }
        return card.type !== "approval" || this.state.payload.can_approve;
    }

    chosen(card) {
        const option = this.options(card).find((option) => option.value === this.done(card).done);
        return option ? option.label : this.done(card).done;
    }

    press(card, option) {
        if (option.input && !this.state.correcting[card.id]) {
            this.state.correcting[card.id] = true;
            return;
        }
        return this.act(card, option.value, option.input ? this.state.typed[card.id] : null, option.label);
    }

    async act(card, action, value, label) {
        if (this.state.busy) {
            return;
        }
        this.state.busy = card.id;
        try {
            const payload = await this.orm.call("res.users", "dooservice_brain_act", [this.messageId, card.id, action, value, label]);
            this.state.correcting[card.id] = false;
            this.show(payload);
        } finally {
            this.state.busy = "";
        }
    }

    continueFrom(card) {
        new TicketOpener(this.env).ask({ continues: card.ticket, continuesNumber: card.number });
    }
}
