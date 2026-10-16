import { Component, onMounted, onWillUnmount, proxy, useProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { CardsLoader } from "./cards_loader";
import { DooserviceChart } from "./chart";

const FOLLOW_MS = 20000;
const STEPS = ["queued", "building", "ready", "approved", "deployed"];

/** The pieces under an answer of Dooservice: nothing is sent, created or changed without a button saying so. */
export class DooserviceCards extends Component {
    static template = "dooservice_brain.Cards";
    static components = { DooserviceChart };

    setup() {
        this.props = useProps();
        this.orm = useService("orm");
        this.steps = STEPS;
        this.state = proxy({ payload: null, busy: "", picked: {}, typed: {}, correcting: {} });
        onMounted(() => this.load());
        onWillUnmount(() => {
            this.gone = true;
            clearInterval(this.following);
        });
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
        if (this.gone) {
            return;
        }
        this.state.payload = payload;
        clearInterval(this.following);
        const open = Object.values(payload?.requests || {}).some((request) => !request.finished);
        if (open) {
            this.following = setInterval(async () => this.show(await CardsLoader.of(this.env.services.orm).cards(this.messageId)), FOLLOW_MS);
        }
    }

    done(card) {
        return this.state.payload.state[card.id] || {};
    }

    request(card) {
        return this.state.payload.requests[this.done(card).request] || null;
    }

    reached(card, step) {
        const request = this.request(card);
        return request && STEPS.indexOf(step) <= STEPS.indexOf(request.state);
    }

    toggle(card, value) {
        const picked = new Set(this.state.picked[card.id] || []);
        picked.has(value) ? picked.delete(value) : picked.add(value);
        this.state.picked[card.id] = [...picked];
    }

    async act(card, action, value = null) {
        if (this.state.busy) {
            return;
        }
        this.state.busy = card.id;
        try {
            const payload = await this.orm.call("res.users", "dooservice_brain_act", [this.messageId, card.id, action, value]);
            this.state.correcting[card.id] = false;
            this.show(payload);
        } finally {
            this.state.busy = "";
        }
    }
}
