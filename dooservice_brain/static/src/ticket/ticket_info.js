import { reactive } from "@odoo/owl";

/**
 * What the client knows of the ticket behind a chat, asked once per chat and again as it moves.
 *
 * Shared by the header badge and the composer, so it holds the web client's own ORM; a chat
 * that is no ticket is remembered as such and never asked again.
 */
export class TicketInfo {
    static shared = null;

    static of(orm) {
        TicketInfo.shared ??= new TicketInfo(orm);
        return TicketInfo.shared;
    }

    constructor(orm) {
        this.orm = orm;
        this.state = reactive({});
        this.loading = new Map();
    }

    get(channelId) {
        return this.state[channelId] || null;
    }

    async refresh(channelId) {
        if (!Number.isInteger(channelId) || this.state[channelId] === false) {
            return null;
        }
        if (!this.loading.has(channelId)) {
            const asked = this.orm
                .call("dooservice.ticket", "header_of", [channelId])
                .catch(() => false)
                .then((header) => {
                    this.state[channelId] = header;
                    this.loading.delete(channelId);
                    return header;
                });
            this.loading.set(channelId, asked);
        }
        return this.loading.get(channelId);
    }
}
